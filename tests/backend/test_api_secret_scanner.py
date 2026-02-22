
from app.models import User
from app.auth import get_password_hash

def create_test_user(db, email="secretscanner@example.com", password="password123"):
    hashed = get_password_hash(password)
    user = User(email=email, password_hash=hashed, full_name="Scanner Test User", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_auth_token(client, email, password):
    response = client.post("/token", data={"username": email, "password": password})
    return response.json()["access_token"]

def test_scan_api_unauthorized(client):
    response = client.post("/secrets/scan", json={"content": "some content"})
    assert response.status_code == 401

def test_scan_api_valid_no_secrets(client, db):
    email = "clean@example.com"
    password = "password123"
    create_test_user(db, email, password)
    token = get_auth_token(client, email, password)
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "content": 'resource "aws_instance" "test" {}',
        "filename": "test.tf"
    }
    
    response = client.post("/secrets/scan", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["total_findings"] == 0
    assert len(data["findings"]) == 0

def test_scan_api_detected_secret(client, db):
    email = "leaky@example.com"
    password = "password123"
    create_test_user(db, email, password)
    token = get_auth_token(client, email, password)
    
    headers = {"Authorization": f"Bearer {token}"}
    # Using a fake key that matches the pattern (AKIA + 16 chars)
    # The PROD123 suffix ensures it's not in the 'EXAMPLE' allowlist if one exists
    payload = {
        "content": 'aws_access_key_id = "AKIAIOSFODNN7PROD123"',
        "filename": "leaky.tf"
    }
    
    response = client.post("/secrets/scan", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["total_findings"] > 0
    assert data["findings"][0]["type"] == "aws_access_key"
    assert "AKIA" in data["findings"][0]["snippet"]
