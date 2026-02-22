from app.database import SessionLocal
from app.models import User
db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@company.com').first()
if user:
    print(f"User found: {user.email}")
    print(f"Hash: {user.password_hash}")
else:
    print("User not found")
db.close()
