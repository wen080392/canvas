"""Direct test of login function"""
import sys
sys.path.insert(0, 'apps/backend')

from app.database import get_db
from app.models import User, RefreshToken
from app.auth import authenticate_user, create_access_token, verify_password
from app.schemas import Token
from datetime import timedelta, datetime
import uuid

db = next(get_db())

# Test authenticate_user
print("=== Testing authenticate_user ===")
try:
    user = authenticate_user(db, "admin@company.com", "admin123")
    if user:
        print(f"✓ authenticate_user returned: {user.email}")
    else:
        print("✗ authenticate_user returned None")
        # Let's debug more
        u = db.query(User).filter(User.email == "admin@company.com").first()
        if u:
            print(f"  User found in DB, hash: {u.password_hash[:50]}...")
            result = verify_password("admin123", u.password_hash)
            print(f"  verify_password result: {result}")
except Exception as e:
    print(f"✗ Error in authenticate_user: {e}")
    import traceback
    traceback.print_exc()

# Test token creation
print("\n=== Testing create_access_token ===")
try:
    token = create_access_token(data={"sub": "admin@company.com"}, expires_delta=timedelta(minutes=30))
    print(f"✓ Token created: {token[:50]}...")
except Exception as e:
    print(f"✗ Error creating token: {e}")

# Test RefreshToken creation
print("\n=== Testing RefreshToken creation ===")
try:
    user = db.query(User).filter(User.email == "admin@company.com").first()
    if user:
        refresh_token_str = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=7)
        new_refresh = RefreshToken(user_id=user.id, token=refresh_token_str, expires_at=expires_at)
        db.add(new_refresh)
        db.commit()
        print(f"✓ RefreshToken created: {refresh_token_str[:20]}...")
except Exception as e:
    print(f"✗ Error creating RefreshToken: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Done ===")
