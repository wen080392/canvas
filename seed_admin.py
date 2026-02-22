from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()
email = "admin@company.com"
password = "password"

user = db.query(User).filter(User.email == email).first()

if not user:
    print(f"User {email} not found. Creating...")
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        full_name="Admin User",
        is_active=True
    )
    db.add(user)
    db.commit()
    print("User created successfully.")
else:
    # Reset password just in case
    print(f"User {email} found. Resetting password...")
    user.password_hash = get_password_hash(password)
    db.commit()
    print("Password reset successfully.")

db.close()
