from sqlalchemy.orm import Session
from app.models import Organization, User
from typing import Optional
import uuid

class OrganizationService:
    """
    Manages Enterprise Organizations/Tenants.
    """
    
    def create_organization(self, db: Session, name: str, user: User) -> Organization:
        """
        Create a new organization and assign the user as owner/member.
        Automatic slug generation.
        """
        # Generate slug from name
        base_slug = name.lower().replace(" ", "-")
        slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        
        org = Organization(
            name=name,
            slug=slug,
            subscription_tier="free",
            max_projects=1,
            max_users=3
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Link user to this org
        user.organization_id = org.id
        db.commit()
        db.refresh(user)
        
        return org

    def get_organization_by_user(self, db: Session, user_id: int) -> Optional[Organization]:
        """Get the organization a user belongs to."""
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.organization_id:
            return db.query(Organization).filter(Organization.id == user.organization_id).first()
        return None

    def update_subscription(self, db: Session, org_id: int, tier: str):
        """Update subscription tier and limits."""
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return None
            
        org.subscription_tier = tier
        
        # Set limits based on tier
        if tier == "pro":
            org.max_projects = 10
            org.max_users = 10
        elif tier == "enterprise":
            org.max_projects = 999
            org.max_users = 999
        else:
            org.max_projects = 1
            org.max_users = 3
            
        db.commit()
        db.refresh(org)
        return org
