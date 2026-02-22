from datetime import datetime, timedelta
from app.models import User, RefreshToken
from app.auth import get_password_hash

def create_test_user(db, email="test@example.com", password="password123"):
    hashed = get_password_hash(password)
    user = User(email=email, password_hash=hashed, full_name="Test User", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_login_success(client, db):
    email = "login@example.com"
    password = "password123"
    create_test_user(db, email, password)
    
    response = client.post("/token", data={"username": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify DB entry
    refresh_token = db.query(RefreshToken).filter(RefreshToken.token == data["refresh_token"]).first()
    assert refresh_token is not None
    assert refresh_token.revoked is False

def test_login_failure(client, db):
    response = client.post("/token", data={"username": "wrong@example.com", "password": "wrongpassword"})
    assert response.status_code == 401

def test_refresh_token_flow(client, db):
    email = "refresh@example.com"
    password = "password123"
    create_test_user(db, email, password)
    
    # Login
    login_res = client.post("/token", data={"username": email, "password": password})
    refresh_token = login_res.json()["refresh_token"]
    
    # Refresh
    refresh_res = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["refresh_token"] != refresh_token
    
    # Check old token revoked
    old_token_db = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    assert old_token_db.revoked is True
    
    # Try using revoked token
    fail_res = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert fail_res.status_code == 401

def test_sessions_list(client, db):
    email = "sessions@example.com"
    password = "password123"
    create_test_user(db, email, password)
    
    # Login twice to create 2 sessions
    res1 = client.post("/token", data={"username": email, "password": password})
    token1 = res1.json()["access_token"]
    
    res2 = client.post("/token", data={"username": email, "password": password})
    
    # Authenticate with first token
    response = client.get("/sessions", headers={"Authorization": f"Bearer {token1}"})
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) == 2

def test_logout_all(client, db):
    email = "logout@example.com"
    password = "password123"
    create_test_user(db, email, password)
    
    # Login
    res = client.post("/token", data={"username": email, "password": password})
    data = res.json()
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    
    # Logout all
    logout_res = client.post("/logout/all", headers={"Authorization": f"Bearer {access_token}"})
    assert logout_res.status_code == 200
    
    # Check token revoked in DB
    token_db = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    assert token_db.revoked is True
    
    # Try to refresh (should fail)
    refresh_res = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 401
