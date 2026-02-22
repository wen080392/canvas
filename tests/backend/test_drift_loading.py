import sys
import pytest
import asyncio
from unittest.mock import MagicMock

# Mock boto3 before importing app modules that depend on it
sys.modules["boto3"] = MagicMock()

from app.services.drift_detector import DriftDetectionService
from app.models import Project

# @pytest.mark.asyncio -> REMOVED
def test_load_terraform_state():
    """Test loading terraform state from local file"""
    async def _run_test():
        # Mock DB session
        mock_db = MagicMock()
        
        # Create service
        service = DriftDetectionService(mock_db)
        
        # Mock project
        project = Project(id=999, name="Test Project")
        
        # Call method
        state = await service._load_terraform_state(project)
        
        # Verify
        print(f"Loaded state version: {state.get('version')}")
        print(f"Resources found: {len(state.get('resources', []))}")
        
        assert state.get('version') == 4
        assert len(state.get('resources')) > 0
        
        resource = state['resources'][0]
        assert resource['type'] == 'aws_s3_bucket'
        assert resource['instances'][0]['attributes']['bucket'] == 'example-bucket-12345'
        
        print("Test passed successfully!")

    asyncio.run(_run_test())

# @pytest.mark.asyncio -> REMOVED
def test_load_terraform_state_s3():
    """Test loading terraform state from S3"""
    async def _run_test():
        import os
        from unittest.mock import MagicMock
        
        # Mock environment variable
        os.environ["TERRAFORM_STATE_BUCKET"] = "my-tf-state-bucket"
        
        # Mock DB session
        mock_db = MagicMock()
        
        # Create service
        service = DriftDetectionService(mock_db)
        
        # Mock S3 client
        mock_s3 = MagicMock()
        service.s3_client = mock_s3
        
        # Setup mock response
        mock_content = b'{"version": 4, "resources": [{"type": "aws_s3_bucket", "instances": [{"attributes": {"bucket": "s3-bucket"}}]}]}'
        mock_response = {'Body': MagicMock(read=lambda: mock_content)}
        mock_s3.get_object.return_value = mock_response
        
        # Mock project
        project = Project(id=1000, name="S3 Project")
        
        # Patch os.path.exists to return False to skip local checks
        from unittest.mock import patch
        with patch("os.path.exists", return_value=False):
            # Call method
            state = await service._load_terraform_state(project)
        
        # Verify
        mock_s3.get_object.assert_called_with(Bucket="my-tf-state-bucket", Key="projects/1000/terraform.tfstate")
        assert state.get('version') == 4
        assert len(state.get('resources')) == 1
        
        print("S3 Test passed successfully!")
        
        # Cleanup
        del os.environ["TERRAFORM_STATE_BUCKET"]

    asyncio.run(_run_test())

if __name__ == "__main__":
    # Allow running directly
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_load_terraform_state())
    loop.run_until_complete(test_load_terraform_state_s3())
    loop.close()
