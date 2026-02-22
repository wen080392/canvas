"""Reset admin password"""
import sys
sys.path.insert(0, 'apps/backend')

from app.database import get_db
from app.models import User
from app.auth import get_password_hash, verify_password

db = next(get_db())

# Find admin user
admin = db.query(User).filter(User.email == "admin@company.com").first()
if admin:
    print(f"Resetting password for: {admin.email}")
    
    # Create new hash for admin123
    new_password = "admin123"
    new_hash = get_password_hash(new_password)
    
    admin.password_hash = new_hash
    db.commit()
    
    print(f"✓ Password reset to '{new_password}'")
    print(f"New hash: {new_hash[:60]}...")
    
    # Verify it works
    db.refresh(admin)
    result = verify_password(new_password, admin.password_hash)
    print(f"Verification: {result}")
else:
    print("Admin not found")
