"""Diagnostic script to test registration endpoint"""
import sys
sys.path.insert(0, 'apps/backend')

from app.database import get_db, engine
from app.models import Base, User
from app.auth import get_password_hash
from sqlalchemy.orm import Session

# Test 1: Check database connection
print("=== Test 1: Database Connection ===")
try:
    db = next(get_db())
    print("✓ Database connected successfully")
except Exception as e:
    print(f"✗ Database error: {e}")
    sys.exit(1)

# Test 2: Check User model
print("\n=== Test 2: User Model ===")
try:
    users = db.query(User).limit(3).all()
    print(f"✓ Found {len(users)} users in database")
    for u in users:
        print(f"  - {u.email} (id={u.id}, org_id={u.organization_id})")
except Exception as e:
    print(f"✗ User query error: {e}")

# Test 3: Password hashing
print("\n=== Test 3: Password Hashing ===")
try:
    test_hash = get_password_hash("testpassword123")
    print(f"✓ Hash generated: {test_hash[:50]}...")
except Exception as e:
    print(f"✗ Password hash error: {e}")

# Test 4: Create new user (dry run)
print("\n=== Test 4: User Creation Check ===")
try:
    from app.models import Organization
    from app.services.organization_service import OrganizationService
    
    # Check if Organization table exists
    orgs = db.query(Organization).limit(1).all()
    print(f"✓ Organization table exists, found {len(orgs)} orgs")
    
    # Check email constraint
    existing = db.query(User).filter(User.email == "testuser123@example.com").first()
    if existing:
        print(f"  Note: user testuser123@example.com already exists (id={existing.id})")
    else:
        print("  User testuser123@example.com does not exist yet")
        
except Exception as e:
    print(f"✗ Organization/User check error: {e}")

print("\n=== Done ===")
