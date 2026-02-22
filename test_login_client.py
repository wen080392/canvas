"""Test the exact login flow from the router"""
import sys
sys.path.insert(0, 'apps/backend')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== Testing /token endpoint with TestClient ===")
try:
    response = client.post(
        "/token",
        data={"username": "admin@company.com", "password": "admin123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500] if len(response.text) > 500 else response.text}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
