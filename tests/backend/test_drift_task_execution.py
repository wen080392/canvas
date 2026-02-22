import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# 1. Mock boto3 and celery BEFORE importing app modules
# If runs via pytest with conftest.py, boto3 might already be mocked.
if "boto3" not in sys.modules or not isinstance(sys.modules["boto3"], MagicMock):
    sys.modules["boto3"] = MagicMock()

sys.modules["celery"] = MagicMock()
sys.modules["celery.schedules"] = MagicMock()

# Need to mock celery_app object too since tasks import it
celery_mock = MagicMock()
# Mock the @task decorator to just return the function
def task_decorator(*args, **kwargs):
    def wrapper(func):
        return func
    return wrapper
celery_mock.task = task_decorator
sys.modules["celery_app"] = MagicMock()
sys.modules["celery_app"].celery_app = celery_mock

from app.database import Base, engine, SessionLocal
from app.models import Project, Organization, User, DriftAlert
from tasks.drift_check import check_project_drift

def setup_data(db):
    """Create test data"""
    import uuid
    # Use unique names to avoid collisions if DB isn't perfectly clean
    suffix = str(uuid.uuid4())[:8]
    org = Organization(name=f"Test Org {suffix}", slug=f"test-org-{suffix}")
    db.add(org)
    db.commit()
    db.refresh(org)
    
    project = Project(
        organization_id=org.id,
        name="Drift Test Project",
        id=12345 + int(uuid.uuid4().int % 1000) # Random ID
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def mock_s3_acl_response():
    """Return a response indicating public access (DRIFT!)"""
    return {
        'Grants': [
            {
                'Grantee': {'URI': 'http://acs.amazonaws.com/groups/global/AllUsers'},
                'Permission': 'READ'
            }
        ],
        'Owner': {'DisplayName': 'owner', 'ID': 'owner_id'}
    }

def test_drift_task_execution(db):
    """Test the synchronous execution of the drift check task"""
    # Patch SessionLocal in the task module to return our test db session
    # We use a MagicMock that returns 'db' when called -> SessionLocal() == db
    with patch("tasks.drift_check.SessionLocal", return_value=db):
        
        project = setup_data(db)
        
        # Configure the global boto3 mock (or existing one)
        mock_boto3 = sys.modules["boto3"]
        mock_s3_client = MagicMock()
        
        # Configure the mock client to return our "Public" ACL
        mock_s3_client.get_bucket_acl.return_value = mock_s3_acl_response()
        
        # When boto3.client('s3') is called, return our mock_s3_client
        def side_effect(service_name, **kwargs):
            if service_name == 's3':
                return mock_s3_client
            return MagicMock() # Return generic mocks for ec2, rds etc
            
        # Store original side effect to restore later
        original_side_effect = None
        if isinstance(mock_boto3.client, MagicMock):
            original_side_effect = mock_boto3.client.side_effect
            
        mock_boto3.client.side_effect = side_effect
        
        try:
            # RUN THE TASK
            # Note: We need to mock _load_terraform_state behavior or ensure files exist.
            # The service tries to load files. Since we don't have real files for this random project,
            # we should mock _load_terraform_state in the service or rely on simulation/mock fallback.
            # BUT check_project_drift creates a NEW DriftDetectionService(db).
            # The service falls back to mock state if file not found.
            # Mock state has "aws_s3_bucket" resource named "critical-data" with bucket "company-data-prod"
            # Our mock_s3_client will return PUBLIC for ANY bucket.
            # So it should detect drift.
            
            print(f"Checking drift for project {project.id}...")
            
            # Prevent the task from closing the shared test session
            with patch.object(db, 'close', return_value=None):
                result = check_project_drift(project.id)
            
            print("Task Result:", result)
            
            assert result["status"] == "completed"
            
            # Check database for alerts
            alerts = db.query(DriftAlert).filter(DriftAlert.project_id == project.id).all()
            print(f"Found {len(alerts)} alerts in DB")
            
            # We expect alerts because Mock State (from fallback) + Public S3 response = Drift
            assert len(alerts) >= 1
            alert = alerts[0]
            # DriftDetectionService mock state uses bucket name "company-data-prod"
            # BUT if local terraform.tfstate exists, it uses "example-bucket-12345".
            # We accept both.
            
            assert any(x in alert.resource_id for x in ["company-data-prod", "critical-data", "example-bucket-12345"])
            
        finally:
            # Restore
            if isinstance(mock_boto3.client, MagicMock):
                mock_boto3.client.side_effect = original_side_effect


if __name__ == "__main__":
    test_drift_task_execution()
