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
        alerts = drift_service.check_drift(project_id)
        
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
