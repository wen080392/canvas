from sqlalchemy import Column, Integer, String, Enum, DateTime, JSON, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database import Base

# ==================== ENUMS ====================

class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ScanStatus(str, enum.Enum):
    OPEN = "OPEN"
    FIXED = "FIXED"
    IGNORED = "IGNORED"
    IN_PROGRESS = "IN_PROGRESS"

class DriftStatus(str, enum.Enum):
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"

class PRStatus(str, enum.Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"
    CLOSED = "CLOSED"
    FAILED = "FAILED"

class SecretType(str, enum.Enum):
    AWS_KEY = "AWS_KEY"
    API_TOKEN = "API_TOKEN"
    DB_PASSWORD = "DB_PASSWORD"
    PRIVATE_KEY = "PRIVATE_KEY"
    STRIPE_KEY = "STRIPE_KEY"
    GITHUB_TOKEN = "GITHUB_TOKEN"
    GENERIC = "GENERIC"

class RemediationType(str, enum.Enum):
    AUTO_FIX = "AUTO_FIX"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    IGNORED = "IGNORED"

class ResourceType(str, enum.Enum):
    S3_BUCKET = "S3_BUCKET"
    EC2_INSTANCE = "EC2_INSTANCE"
    RDS_DATABASE = "RDS_DATABASE"
    SECURITY_GROUP = "SECURITY_GROUP"
    IAM_ROLE = "IAM_ROLE"
    LAMBDA_FUNCTION = "LAMBDA_FUNCTION"
    VPC = "VPC"
    OTHER = "OTHER"

# ==================== CORE MODELS ====================

class User(Base):
    """User account"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    
    # Context (Tenancy)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True) # User belongs to a tenant
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    scans = relationship("TerraformScan", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    user = relationship("User", back_populates="refresh_tokens")

class Organization(Base):
    """Enterprise organization/tenant"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True)
    
    # Billing & Plan
    subscription_tier = Column(String(50), default="free")  # free, pro, enterprise
    stripe_customer_id = Column(String(100), nullable=True)
    billing_email = Column(String(255), nullable=True)
    max_projects = Column(Integer, default=1)
    max_users = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    
class Notification(Base):
    """User notification messages"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="notifications")

# ==================== TERRAFORM SCANS ====================

class TerraformScan(Base):
    """Simple Terraform file scans"""
    __tablename__ = "terraform_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    issues_found = Column(JSON)  # List of issues
    issues_count = Column(Integer, default=0)
    status = Column(String(50), default="PASSED")  # PASSED, WARNING, BLOCKED, CRITICAL
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="scans")

class Project(Base):
    """Git repository/project being scanned"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String(255), nullable=False)
    repository_url = Column(String(500))
    github_repo_id = Column(String(100), index=True)
    default_branch = Column(String(100), default="main")
    last_scan_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    organization = relationship("Organization", back_populates="projects")
    scan_results = relationship("ScanResult", back_populates="project")
    drift_alerts = relationship("DriftAlert", back_populates="project")
    secrets = relationship("SecretLeak", back_populates="project")
    resources = relationship("InfrastructureResource", back_populates="project")

# ==================== SECURITY SCANNING ====================

class ScanResult(Base):
    """Security scan findings"""
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    resource_id = Column(String(255), index=True)
    resource_type = Column(Enum(ResourceType))
    rule_id = Column(String(100), index=True)
    severity = Column(Enum(Severity), default=Severity.MEDIUM)
    description = Column(Text)
    file_path = Column(String(500))
    line_number = Column(Integer)
    status = Column(Enum(ScanStatus), default=ScanStatus.OPEN)
    fix_suggestion = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime)
    
    project = relationship("Project", back_populates="scan_results")
    remediations = relationship("RemediationPR", back_populates="scan_result")

# ==================== DRIFT DETECTION ====================

class DriftAlert(Base):
    """Infrastructure drift (code vs reality)"""
    __tablename__ = "drift_alerts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    resource_id = Column(String(255), index=True)
    resource_type = Column(Enum(ResourceType))
    aws_arn = Column(String(500))
    expected_state = Column(JSON)  # From Terraform state
    actual_state = Column(JSON)    # From AWS API
    drift_details = Column(JSON)   # Specific differences
    severity = Column(Enum(Severity), default=Severity.MEDIUM)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    status = Column(Enum(DriftStatus), default=DriftStatus.PENDING)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime)
    
    project = relationship("Project", back_populates="drift_alerts")

# ==================== AUTO-REMEDIATION ====================

class RemediationPR(Base):
    """Auto-fix Pull Requests"""
    __tablename__ = "remediation_prs"

    id = Column(Integer, primary_key=True, index=True)
    scan_result_id = Column(Integer, ForeignKey("scan_results.id"), nullable=True)
    drift_alert_id = Column(Integer, ForeignKey("drift_alerts.id"), nullable=True)
    pr_number = Column(Integer)
    pr_url = Column(String(500))
    github_pr_id = Column(String(100))
    branch_name = Column(String(255))
    status = Column(Enum(PRStatus), default=PRStatus.OPEN)
    remediation_type = Column(Enum(RemediationType))
    changes_made = Column(JSON)  # Summary of what was changed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    merged_at = Column(DateTime)
    
    scan_result = relationship("ScanResult", back_populates="remediations")

# ==================== SECRET SCANNING ====================

class SecretLeak(Base):
    """Detected secrets/credentials in code"""
    __tablename__ = "secret_leaks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    secret_type = Column(Enum(SecretType))
    file_path = Column(String(500))
    line_number = Column(Integer)
    secret_hash = Column(String(64), index=True)  # SHA256 of redacted secret
    context = Column(Text)  # Surrounding code (redacted)
    severity = Column(Enum(Severity), default=Severity.CRITICAL)
    is_active = Column(Boolean, default=True)  # If the secret is still valid
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    revoked_at = Column(DateTime)
    
    project = relationship("Project", back_populates="secrets")

# ==================== INFRASTRUCTURE GRAPH ====================

class InfrastructureResource(Base):
    """Graph node - individual cloud resources"""
    __tablename__ = "infrastructure_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    resource_id = Column(String(255), unique=True, index=True)
    resource_type = Column(Enum(ResourceType))
    resource_name = Column(String(255))
    aws_arn = Column(String(500))
    region = Column(String(50))
    tags = Column(JSON)
    configuration = Column(JSON)  # Full resource config
    risk_score = Column(Float, default=0.0)  # Calculated security score
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    project = relationship("Project", back_populates="resources")
    outgoing_connections = relationship(
        "ResourceConnection",
        foreign_keys="ResourceConnection.source_id",
        back_populates="source"
    )
    incoming_connections = relationship(
        "ResourceConnection",
        foreign_keys="ResourceConnection.target_id",
        back_populates="target"
    )

class ResourceConnection(Base):
    """Graph edge - connections between resources"""
    __tablename__ = "resource_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("infrastructure_resources.id"), index=True)
    target_id = Column(Integer, ForeignKey("infrastructure_resources.id"), index=True)
    connection_type = Column(String(100))  # e.g., "network", "iam_policy", "data_flow"
    protocol = Column(String(50))  # tcp, https, etc
    ports = Column(JSON)  # List of ports if applicable
    is_public = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    risk_level = Column(Enum(Severity), default=Severity.LOW)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    source = relationship("InfrastructureResource", foreign_keys=[source_id], back_populates="outgoing_connections")
    target = relationship("InfrastructureResource", foreign_keys=[target_id], back_populates="incoming_connections")

# ==================== AUDIT & COMPLIANCE ====================

class AuditLog(Base):
    """Audit trail for all actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), index=True)  # scan_triggered, drift_detected, pr_created, etc
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class ComplianceReport(Base):
    """Compliance framework tracking (SOC2, ISO27001, HIPAA)"""
    __tablename__ = "compliance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    framework = Column(String(100))  # SOC2, ISO27001, HIPAA, PCI-DSS
    control_id = Column(String(100))  # e.g., "AC-1", "SI-3"
    status = Column(String(50))  # compliant, non_compliant, not_applicable
    evidence = Column(JSON)
    last_assessed = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserSettings(Base):
    """User settings and encrypted credentials"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # AWS Credentials (encrypted)
    aws_access_key_encrypted = Column(Text, nullable=True)
    aws_secret_key_encrypted = Column(Text, nullable=True)
    aws_region = Column(String(50), default="us-east-1")
    
    # GitHub Integration
    github_token_encrypted = Column(Text, nullable=True)
    
    # Preferences
    dark_mode = Column(Boolean, default=False)
    email_notifications = Column(Boolean, default=True)
    
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="settings")
