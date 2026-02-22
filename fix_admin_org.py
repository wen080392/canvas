"""Fix admin user by creating organization"""
import sys
sys.path.insert(0, 'apps/backend')

from app.database import get_db
from app.models import User, Organization
from app.services.organization_service import OrganizationService

db = next(get_db())

# Find admin user
admin = db.query(User).filter(User.email == "admin@company.com").first()
if admin:
    print(f"Found admin user: id={admin.id}, org_id={admin.organization_id}")
    
    if admin.organization_id is None:
        print("Admin has no organization, creating one...")
        
        # Create organization for admin
        org_service = OrganizationService()
        org = org_service.create_organization(db, "Admin Organization", admin)
        print(f"✓ Created organization: {org.name} (id={org.id})")
        print(f"✓ Updated admin.organization_id to {admin.organization_id}")
    else:
        print("Admin already has organization, nothing to do")
else:
    print("Admin user not found")
