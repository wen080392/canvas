
from app.models import User
from app.auth import get_password_hash

def create_test_user(db, email="drift@example.com", password="password123"):
    hashed = get_password_hash(password)
    user = User(email=email, password_hash=hashed, full_name="Drift Test User", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_auth_token(client, email, password):
    response = client.post("/token", data={"username": email, "password": password})
    return response.json()["access_token"]

def test_drift_scan_api_unauthorized(client):
    response = client.post("/drift/scan")
    assert response.status_code == 401

def test_drift_scan_simulation_mode(client, db):
    email = "drift_sim@example.com"
    password = "password123"
    create_test_user(db, email, password)
    token = get_auth_token(client, email, password)
    

    headers = {"Authorization": f"Bearer {token}"}
    
    # Configure the global boto3 mock to raise exception on list_buckets
    # This forces DriftDetectionService into simulation_mode=True
    import sys
    mock_boto3 = sys.modules["boto3"]
    original_side_effect = mock_boto3.client.return_value.list_buckets.side_effect
    mock_boto3.client.return_value.list_buckets.side_effect = Exception("No AWS Creds")
    
    try:
        # Trigger scan
        # In simulation mode (env without AWS creds), this should return mock alerts
        response = client.post("/drift/scan", headers=headers)
        assert response.status_code == 200
        
        alerts = response.json()
        assert isinstance(alerts, list)
        
        # We should see mock alerts (S3, SG, RDS)
        assert len(alerts) > 0
        
        # Validate structure matches frontend expectations
        alert = alerts[0]
        assert "resource_id" in alert
        assert "severity" in alert
        assert "drift_details" in alert
    finally:
         # Restore side effect to avoid breaking subsequent tests
         mock_boto3.client.return_value.list_buckets.side_effect = original_side_effect

