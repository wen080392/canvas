"""Reset admin password in the CORRECT database (apps/backend/cloudguardian.db)"""
import sys
import os

# Set CWD to apps/backend so SQLite path resolves correctly
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import User
from app.auth import get_password_hash, verify_password

db = next(get_db())

# Find admin user
admin = db.query(User).filter(User.email == "admin@company.com").first()
if admin:
    print(f"Found admin in correct DB")
    print(f"Current hash: {admin.password_hash[:30]}...")
    
    # Create new hash
    new_hash = get_password_hash("admin123")
    admin.password_hash = new_hash
    db.commit()
    
    print(f"New hash: {new_hash[:30]}...")
    print(f"Verify: {verify_password('admin123', new_hash)}")
    print("✅ Password reset complete!")
else:
    print("Admin user not found in this database!")
