"""
Scheduler for running periodic maintenance and ETL jobs.

This module sets up and manages scheduled jobs using APScheduler.
"""

import os
import logging
from datetime import datetime, time
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SchedulerManager:
    """Manager for scheduled jobs."""
    
    def __init__(self, enable_scheduled_jobs: bool = None):
        """Initialize the scheduler manager.
        
        Args:
            enable_scheduled_jobs: Whether to enable scheduled jobs.
                                 If None, checks the ENABLE_SCHEDULED_JOBS environment variable.
        """
        if enable_scheduled_jobs is None:
            self.enable_scheduled_jobs = os.getenv("ENABLE_SCHEDULED_JOBS", "False").lower() == "true"
        else:
            self.enable_scheduled_jobs = enable_scheduled_jobs
            
        self.scheduler = BackgroundScheduler(daemon=True)
        self.jobs = {}
        
        # Configure default timezone
        self.timezone = 'UTC'  # You can change this to your preferred timezone
    
    def add_job(
        self,
        func,
        job_id: str,
        trigger: str = 'cron',
        **trigger_args
    ) -> bool:
        """Add a job to the scheduler.
        
        Args:
            func: The function to be scheduled
            job_id: Unique identifier for the job
            trigger: Type of trigger to use ('cron', 'interval', 'date')
            **trigger_args: Arguments for the trigger
            
        Returns:
            bool: True if job was added, False otherwise
        """
        if not self.enable_scheduled_jobs:
            logger.warning(f"Scheduled jobs are disabled. Not adding job: {job_id}")
            return False
            
        try:
            # Remove existing job with the same ID if it exists
            if job_id in self.jobs:
                self.scheduler.remove_job(job_id)
                
            # Add the new job
            job = self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                timezone=self.timezone,
                **trigger_args
            )
            
            self.jobs[job_id] = job
            
            next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run_time else "N/A"
            logger.info(f"Added job '{job_id}'. Next run: {next_run}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add job '{job_id}': {e}", exc_info=True)
            return False
    
    def start(self) -> bool:
        """Start the scheduler.
        
        Returns:
            bool: True if scheduler started successfully, False otherwise
        """
        if not self.enable_scheduled_jobs:
            logger.warning("Scheduled jobs are disabled. Not starting scheduler.")
            return False
            
        if self.scheduler.running:
            logger.warning("Scheduler is already running")
            return True
            
        try:
            self.scheduler.start()
            logger.info("Scheduler started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}", exc_info=True)
            return False
    
    def shutdown(self) -> bool:
        """Shutdown the scheduler.
        
        Returns:
            bool: True if scheduler was shut down successfully, False otherwise
        """
        if not self.scheduler.running:
            logger.warning("Scheduler is not running")
            return True
            
        try:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler has been shut down")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}", exc_info=True)
            return False
    
    def get_scheduled_jobs(self) -> list:
        """Get information about all scheduled jobs.
        
        Returns:
            list: List of dictionaries with job information
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'pending': job.pending
            })
        return jobs

def schedule_default_jobs(scheduler: Optional[SchedulerManager] = None) -> SchedulerManager:
    """Set up default scheduled jobs.
    
    Args:
        scheduler: Optional SchedulerManager instance. If None, creates a new one.
        
    Returns:
        SchedulerManager: The configured scheduler instance
    """
    if scheduler is None:
        scheduler = SchedulerManager()
    
    # Import here to avoid circular imports
    from housekeeping.file_cleanup import run_cleanup
    from etl.refresh_pipeline import run_etl_pipeline
    
    # Schedule file cleanup to run daily at 2 AM
    scheduler.add_job(
        func=run_cleanup,
        job_id="file_cleanup",
        trigger="cron",
        hour=2,
        minute=0
    )
    
    # Schedule ETL pipeline to run daily at 3 AM
    scheduler.add_job(
        func=run_etl_pipeline,
        job_id="etl_pipeline",
        trigger="cron",
        hour=3,
        minute=0
    )
    
    return scheduler

# Global scheduler instance
_scheduler = None

def get_scheduler() -> SchedulerManager:
    """Get or create the global scheduler instance.
    
    Returns:
        SchedulerManager: The global scheduler instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = SchedulerManager()
    return _scheduler

def start_scheduler() -> bool:
    """Start the global scheduler with default jobs.
    
    Returns:
        bool: True if scheduler started successfully, False otherwise
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = schedule_default_jobs()
    return _scheduler.start()

if __name__ == "__main__":
    # Example usage
    print("Starting scheduler with default jobs...")
    scheduler = schedule_default_jobs()
    scheduler.start()
    
    try:
        # Keep the script running
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down scheduler...")
        scheduler.shutdown()
