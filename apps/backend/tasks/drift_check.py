"""
Celery Tasks for Drift Detection
"""

from celery_app import celery_app
from app.database import SessionLocal
from app.services.drift_detector import DriftDetectionService
from app.models import Project

@celery_app.task(name="tasks.drift_check.check_project_drift")
def check_project_drift(project_id: int):
    """
    Async task to check drift for a single project
    
    Args:
        project_id: ID of the project to check
    """
    db = SessionLocal()
    try:
        drift_service = DriftDetectionService(db)
        
        import asyncio
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If we are already in an event loop, we can't use run_until_complete
            # For this specific task, we'll try to create a new loop in a thread or just fail nicely?
            # Actually, asyncio.run() fails if a loop is running.
            # Best effort for tests/demo:
            if hasattr(loop, 'create_task'):
                # We can't await here because we are sync. 
                # This path is problematic for blocking calls.
                raise RuntimeError("Cannot block synchronously from inside a running event loop")
        else:
             alerts = asyncio.run(drift_service.check_drift(project_id))
         
        return {
            "project_id": project_id,
            "alerts_count": len(alerts),
            "status": "completed"
        }
    except Exception as e:
        return {
            "project_id": project_id,
            "error": str(e),
            "status": "failed"
        }
    finally:
        db.close()

@celery_app.task(name="tasks.drift_check.check_all_projects_drift")
def check_all_projects_drift():
    """
    Scheduled task to check drift for all active projects
    
    Runs every hour via Celery Beat
    """
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        
        results = []
        for project in projects:
            # Trigger async task for each project
            task = check_project_drift.delay(project.id)
            results.append({
                "project_id": project.id,
                "task_id": task.id
            })
        
        return {
            "projects_checked": len(results),
            "tasks": results
        }
    finally:
        db.close()
