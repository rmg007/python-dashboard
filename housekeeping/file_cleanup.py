"""
File cleanup module for removing old export files.

This module provides functionality to clean up old export files from the
static/exports directory, keeping only files newer than the specified
retention period.
"""

import time
from pathlib import Path
from typing import List

# Default export directory (relative to project root)
EXPORT_DIR = Path("static/exports")

# Default retention period in days
DAYS_TO_KEEP = 30

def delete_old_files(path: Path, days: int) -> List[str]:
    """
    Delete files older than the specified number of days.
    
    Args:
        path: Directory path to search for files
        days: Number of days to keep files
        
    Returns:
        List of names of deleted files
    """
    now = time.time()
    cutoff = now - (days * 86400)  # 86400 seconds in a day
    deleted = []

    # Ensure the path exists and is a directory
    if not path.exists() or not path.is_dir():
        print(f"[CLEANUP] Directory not found: {path}")
        return deleted

    # Iterate through all items in the directory
    for item in path.iterdir():
        try:
            # Check if item is a file and older than cutoff
            if item.is_file() and item.stat().st_mtime < cutoff:
                item.unlink()
                deleted.append(str(item.relative_to(path)))
            # If it's a directory, recurse into it
            elif item.is_dir():
                deleted.extend(delete_old_files(item, days))
        except Exception as e:
            print(f"[CLEANUP] Error processing {item}: {e}")
    
    return deleted

def run_cleanup(days: int = None, export_dir: Path = None) -> dict:
    """
    Run the cleanup process for old export files.
    
    Args:
        days: Number of days to keep files (default: DAYS_TO_KEEP)
        export_dir: Directory containing exports (default: EXPORT_DIR)
        
    Returns:
        dict: Summary of the cleanup operation
    """
    if days is None:
        days = DAYS_TO_KEEP
    if export_dir is None:
        export_dir = Path(__file__).parent.parent / EXPORT_DIR
    else:
        export_dir = Path(export_dir)
    
    print(f"[CLEANUP] Starting cleanup of files older than {days} days in {export_dir}")
    
    try:
        deleted_files = delete_old_files(export_dir, days)
        result = {
            "status": "success",
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files,
            "directory": str(export_dir),
            "retention_days": days
        }
        print(f"[CLEANUP] Deleted {len(deleted_files)} old export files")
    except Exception as e:
        error_msg = f"Cleanup failed: {str(e)}"
        print(f"[CLEANUP] ERROR: {error_msg}")
        result = {
            "status": "error",
            "error": error_msg,
            "deleted_count": 0,
            "deleted_files": [],
            "directory": str(export_dir),
            "retention_days": days
        }
    
    return result

if __name__ == "__main__":
    # Example usage when run directly
    result = run_cleanup()
    print("Cleanup result:", result)
