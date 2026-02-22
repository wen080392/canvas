"""Test password verification directly"""
import sys
sys.path.insert(0, 'apps/backend')

from app.database import get_db
from app.models import User
from app.auth import verify_password, get_password_hash

db = next(get_db())

# Find admin user
admin = db.query(User).filter(User.email == "admin@company.com").first()
if admin:
    print(f"Admin user found: {admin.email}")
    print(f"Password hash: {admin.password_hash[:80]}...")
    print(f"Hash length: {len(admin.password_hash)}")
    
    # Try to verify password
    print("\n=== Testing password verification ===")
    try:
        result = verify_password("admin123", admin.password_hash)
        print(f"verify_password('admin123'): {result}")
    except Exception as e:
        print(f"ERROR verifying password: {e}")
        
    # Check if it's a bcrypt hash vs pbkdf2
    if admin.password_hash.startswith("$2"):
        print("\n⚠ Hash looks like bcrypt but auth.py uses pbkdf2_sha256!")
        print("Need to reset password with new hash format")
        
        # Create new hash
        new_hash = get_password_hash("admin123")
        print(f"\nNew hash (pbkdf2_sha256): {new_hash[:60]}...")
        
        # Update the password
        admin.password_hash = new_hash
        db.commit()
        print("✓ Password hash updated!")
        
        # Verify again
        result = verify_password("admin123", admin.password_hash)
        print(f"verify_password('admin123') after fix: {result}")
        
    elif admin.password_hash.startswith("$pbkdf2"):
        print("\n✓ Hash is already pbkdf2_sha256 format")
else:
    print("Admin user not found!")
