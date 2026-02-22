"""
Test script for Drift Detection Service

This creates a test project and triggers drift detection.
For real AWS testing, set AWS credentials in environment.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import Project, Organization, DriftAlert
from app.services.drift_detector import DriftDetectionService
import asyncio

def setup_test_database():
    """Create tables and test data"""
    print("📋 Setting up test database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create test organization
        org = Organization(
            name="Test Company",
            slug="test-company",
            subscription_tier="enterprise"
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Create test project
        project = Project(
            organization_id=org.id,
            name="test-infrastructure",
            repository_url="https://github.com/test/infra",
            default_branch="main"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        print(f"✅ Created test project with ID: {project.id}")
        return project.id
        
    finally:
        db.close()

async def test_drift_detection(project_id: int):
    """Test drift detection service"""
    print(f"\n🔍 Testing Drift Detection for project {project_id}...")
    
    db = SessionLocal()
    try:
        # Initialize drift detector
        drift_service = DriftDetectionService(db, aws_region="us-east-1")
        
        print("⚠️  Note: This will fail without real AWS credentials")
        print("   For a full test, set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY\n")
        
        # Try to check drift
        try:
            alerts = await drift_service.check_drift(project_id)
            print(f"✅ Drift check completed!")
            print(f"   Found {len(alerts)} drift alerts")
            
            for alert in alerts:
                print(f"\n   Alert #{alert.id}:")
                print(f"   - Resource: {alert.resource_id}")
                print(f"   - Type: {alert.resource_type.value}")
                print(f"   - Severity: {alert.severity.value}")
                print(f"   - Details: {alert.drift_details}")
                
        except Exception as e:
            print(f"⚠️  Drift check failed (expected without AWS): {e}")
            print("\n💡 To test with real AWS:")
            print("   1. Set AWS credentials:")
            print("      export AWS_ACCESS_KEY_ID='your-key'")
            print("      export AWS_SECRET_ACCESS_KEY='your-secret'")
            print("   2. Ensure you have S3 buckets or Security Groups")
            print("   3. Run this script again")
    
    finally:
        db.close()

def test_api_endpoint(project_id: int):
    """Test the FastAPI endpoint"""
    print(f"\n🌐 Testing API Endpoint...")
    print(f"   Run this in another terminal:")
    print(f"   curl -X POST http://localhost:8000/api/v1/drift/check/{project_id}")
    print(f"\n   Or with Python:")
    print(f"   import requests")
    print(f"   response = requests.post('http://localhost:8000/api/v1/drift/check/{project_id}')")
    print(f"   print(response.json())")

if __name__ == "__main__":
    print("🚀 CloudGuardian Drift Detection Test Suite\n")
    
    # Setup
    project_id = setup_test_database()
    
    # Test drift detection
    asyncio.run(test_drift_detection(project_id))
    
    # Show API test instructions
    test_api_endpoint(project_id)
    
    print("\n✅ Test setup complete!")
    print("   Next: Start the backend with 'uvicorn main:app --reload'")
