"""
Scheduled export jobs using APScheduler.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExportScheduler:
    """Manages scheduled export jobs."""
    
    def __init__(self, db):
        """Initialize the scheduler with a database connection."""
        self.scheduler = BackgroundScheduler()
        self.db = db
        self.jobs_initialized = False
    
    def init_scheduler(self):
        """Initialize the scheduler and load scheduled jobs from the database."""
        if self.jobs_initialized:
            return
            
        logger.info("Initializing export scheduler...")
        
        try:
            # Load scheduled exports from the database
            with self.db.engine.connect() as conn:
                result = conn.execute(
                    text("""
                    SELECT id, user_id, name, format, frequency, filters, next_run 
                    FROM export_schedules 
                    WHERE active = TRUE
                    """)
                )
                schedules = [dict(row) for row in result.mappings()]
            
            # Schedule each export
            for schedule in schedules:
                self.schedule_export(
                    schedule_id=schedule['id'],
                    user_id=schedule['user_id'],
                    name=schedule['name'],
                    export_format=schedule['format'],
                    frequency=schedule['frequency'],
                    filters=json.loads(schedule['filters']) if schedule['filters'] else {},
                    next_run=schedule['next_run']
                )
            
            # Start the scheduler
            self.scheduler.start()
            self.jobs_initialized = True
            logger.info(f"Scheduler started with {len(schedules)} scheduled exports")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}", exc_info=True)
    
    def schedule_export(
        self,
        schedule_id: int,
        user_id: str,
        name: str,
        export_format: str,
        frequency: str,
        filters: Dict[str, Any],
        next_run: datetime = None
    ) -> bool:
        """Schedule a new export job."""
        try:
            # Remove any existing job with this ID
            self.remove_schedule(schedule_id)
            
            # Calculate next run time if not provided
            if not next_run:
                next_run = self._calculate_next_run(datetime.now(), frequency)
            
            # Create a trigger based on frequency
            trigger = self._create_trigger(frequency, next_run)
            
            # Add the job to the scheduler
            self.scheduler.add_job(
                self._run_scheduled_export,
                trigger=trigger,
                id=f"export_{schedule_id}",
                args=[schedule_id],
                name=f"{name} ({export_format.upper()}) - {user_id}",
                replace_existing=True,
                max_instances=1,
                misfire_grace_time=3600,  # 1 hour grace period
                coalesce=True
            )
            
            logger.info(f"Scheduled export job: {name} (ID: {schedule_id}) to run {frequency} starting {next_run}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule export {schedule_id}: {e}", exc_info=True)
            return False
    
    def remove_schedule(self, schedule_id: int) -> bool:
        """Remove a scheduled export job."""
        job_id = f"export_{schedule_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled export job: {job_id}")
            return True
        return False
    
    def _run_scheduled_export(self, schedule_id: int):
        """Execute a scheduled export job."""
        try:
            with self.db.engine.connect() as conn:
                # Get the schedule details
                result = conn.execute(
                    text("""
                    SELECT user_id, name, format, filters 
                    FROM export_schedules 
                    WHERE id = :id AND active = TRUE
                    """),
                    {"id": schedule_id}
                )
                schedule = result.mappings().first()
                
                if not schedule:
                    logger.warning(f"Scheduled export {schedule_id} not found or inactive")
                    return
                
                schedule = dict(schedule)
                user_id = schedule['user_id']
                
                # Get the filtered data
                # Note: This assumes you have a function to get filtered data based on the filters
                # You'll need to implement this based on your data model
                filters = json.loads(schedule['filters']) if schedule['filters'] else {}
                # df = get_filtered_data(filters)  # Implement this function
                
                # For now, we'll just log the export
                logger.info(
                    f"Running scheduled export {schedule['name']} "
                    f"(ID: {schedule_id}) for user {user_id}"
                )
                
                # Update last_run and next_run in the database
                conn.execute(
                    text("""
                    UPDATE export_schedules 
                    SET last_run = NOW(), 
                        next_run = :next_run
                    WHERE id = :id
                    """),
                    {
                        "id": schedule_id,
                        "next_run": self._calculate_next_run(datetime.now(), schedule['frequency'])
                    }
                )
                conn.commit()
                
                logger.info(f"Completed scheduled export {schedule['name']} (ID: {schedule_id})")
                
        except Exception as e:
            logger.error(f"Error running scheduled export {schedule_id}: {e}", exc_info=True)
            raise  # Re-raise the exception after logging
    
    @staticmethod
    def _calculate_next_run(base_time: datetime, frequency: str) -> datetime:
        """Calculate the next run time based on frequency."""
        if frequency == "hourly":
            return base_time + timedelta(hours=1)
        elif frequency == "daily":
            return base_time + timedelta(days=1)
        elif frequency == "weekly":
            return base_time + timedelta(weeks=1)
        elif frequency == "monthly":
            # Add approximately one month
            next_month = base_time.month % 12 + 1
            year = base_time.year + (base_time.month // 12)
            try:
                return base_time.replace(year=year, month=next_month, day=1)
            except ValueError:
                # Handle invalid date (e.g., Jan 31 + 1 month = Feb 31)
                return (base_time.replace(day=1) + timedelta(days=32)).replace(day=1)
        else:
            # Default to daily
            return base_time + timedelta(days=1)
    
    @staticmethod
    def _create_trigger(frequency: str, next_run: datetime):
        """Create an APScheduler trigger based on frequency."""
        if frequency == "hourly":
            return CronTrigger(
                minute=next_run.minute,
                jitter=300  # Add up to 5 minutes of jitter to prevent thundering herd
            )
        elif frequency == "daily":
            return CronTrigger(
                hour=next_run.hour,
                minute=next_run.minute,
                jitter=600  # Add up to 10 minutes of jitter
            )
        elif frequency == "weekly":
            return CronTrigger(
                day_of_week=next_run.weekday(),
                hour=next_run.hour,
                minute=next_run.minute,
                jitter=1800  # Add up to 30 minutes of jitter
            )
        elif frequency == "monthly":
            return CronTrigger(
                day=next_run.day,
                hour=next_run.hour,
                minute=next_run.minute,
                jitter=3600  # Add up to 1 hour of jitter
            )
        else:
            # Default to daily
            return CronTrigger(
                hour=next_run.hour,
                minute=next_run.minute,
                jitter=600
            )
    
    def shutdown(self):
        """Shutdown the scheduler cleanly."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Export scheduler shut down")

# Global scheduler instance
scheduler = None


def init_scheduler(db):
    """Initialize the global scheduler instance."""
    global scheduler
    if scheduler is None:
        scheduler = ExportScheduler(db)
        scheduler.init_scheduler()
    return scheduler
