"""
Simple HTTP Test for Drift Detection API

This tests the drift detection endpoint without AWS credentials.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_drift_endpoint():
    """Test drift detection API endpoint"""
    print("🧪 Testing Drift Detection API\n")
    
    # Test project_id = 1 (you may need to create this first)
    project_id = 1
    
    print(f"📡 Testing: POST /api/v1/drift/check/{project_id}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/drift/check/{project_id}")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ API endpoint is working!")
        else:
            print(f"\n⚠️  API returned error (expected without project/AWS)")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the backend running?")
        print("   Start it with: python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_get_alerts():
    """Test getting drift alerts"""
    project_id = 1
    
    print(f"\n📡 Testing: GET /api/v1/drift/alerts/{project_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/drift/alerts/{project_id}")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 CloudGuardian Drift Detection - Simple Test\n")
    
    test_drift_endpoint()
    test_get_alerts()
    
    print("\n💡 To test with real AWS:")
    print("   1. Set AWS credentials in environment variables")
    print("   2. Create a project in the database")
    print("   3. Add Terraform state file references")
    print("   4. Run this test again")
