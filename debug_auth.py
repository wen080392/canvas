from app.database import SessionLocal
from app.models import User
from app.auth import verify_password, pwd_context

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@company.com').first()

if user:
    print(f"User found: {user.email}")
    raw_hash = user.password_hash
    print(f"Hash repr: {repr(raw_hash)}")
    
    password = "password"
    try:
        is_valid = verify_password(password, raw_hash)
        print(f"Verification result: {is_valid}")
    except Exception as e:
        print(f"Verification FAILED with error: {e}")
        import traceback
        traceback.print_exc()

    # Debug context
    print(f"Context schemes: {pwd_context.schemes()}")
else:
    print("User not found")
db.close()
