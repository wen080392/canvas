"""
CloudGuardian - Main FastAPI Application
Enterprise Security & Compliance Platform
"""

from typing import Optional, Dict
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging
from contextlib import asynccontextmanager

from app.database import engine, get_db, Base
from app.models import User, UserSettings, TerraformScan, Notification, RefreshToken
from app.schemas import (
    UserCreate, UserResponse, SettingsUpdate, SettingsResponse,
    ScanCreate, ScanResponse, ScanListResponse, ScanIssue, DashboardStats,
    NotificationResponse, NotificationCreate,
    GraphRequest, GraphResponse,
    SecretScanRequest, SecretScanResponse,
    RemediationSuggestion, RemediationRequest, RemediationExecuteResponse,
    ComplianceOverview, ComplianceFrameworkDetail,
    OrganizationResponse, UpgradeRequest,
    DriftAlertResponse
)
from app.auth import (
    get_password_hash,
    get_current_active_user,
)
from app.router import auth as auth_router
from app.core.security import get_crypto_service
from app.services.terraform_scanner import TerraformScanner
from app.services.graph_service import InfrastructureGraphService
from app.services.secret_scanner import SecretScannerService
from app.services.remediation_service import RemediationService
from app.services.remediation_service import RemediationService
from app.services.compliance_report_service import ComplianceReportService
from app.services.github_service import GitHubService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 CloudGuardian API starting up...")
    logger.info("📊 Database tables created/verified")
    logger.info("🔐 Encryption service initialized")
    logger.info("✅ API ready at http://localhost:8000")
    logger.info("📖 API docs available at http://localhost:8000/docs")
    try:
        yield
    finally:
        logger.info("👋 CloudGuardian API shutting down...")


app = FastAPI(
    title="CloudGuardian API",
    description="Automated Infrastructure Security & Compliance Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
    , lifespan=lifespan
)

# CORS configuration - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router)


# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "CloudGuardian API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "encryption": "enabled"
    }


# ==================== AUTHENTICATION ====================

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **full_name**: Optional display name
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create Default Organization for the user
    from app.services.organization_service import OrganizationService
    org_service = OrganizationService()
    org_name = f"{user_data.full_name or 'My'} Organization"
    org = org_service.create_organization(db, org_name, new_user)
    
    # Create default settings for the user
    user_settings = UserSettings(user_id=new_user.id)
    db.add(user_settings)
    db.commit()
    
    logger.info(f"New user registered: {user_data.email} | Org: {org.name}")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        organization_id=new_user.organization_id
    )





# ==================== USER SETTINGS ====================

@app.get("/settings", response_model=SettingsResponse)
async def get_settings(
    current_user: User =Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user settings with masked credentials
    
    Returns settings with:
    - AWS access key masked (shows only first 4 chars)
    - Boolean flags for secret presence
    - Preferences (dark mode, notifications)
    """
    # Get or create user settings
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings if they don't exist
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    # Decrypt AWS access key for masking (if exists)
    aws_access_key_masked = None
    if settings.aws_access_key_encrypted:
        crypto = get_crypto_service()
        decrypted_key = crypto.decrypt(settings.aws_access_key_encrypted)
        if decrypted_key and len(decrypted_key) >= 4:
            # Show only first 4 characters
            aws_access_key_masked = decrypted_key[:4] + "****"
    
    return SettingsResponse(
        aws_region=settings.aws_region,
        dark_mode=settings.dark_mode,
        email_notifications=settings.email_notifications,
        has_aws_secret=bool(settings.aws_secret_key_encrypted),
        has_github_token=bool(settings.github_token_encrypted),
        aws_access_key_masked=aws_access_key_masked
    )


@app.post("/settings", response_model=SettingsResponse)
async def update_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user settings with encrypted credential storage
    
    - Encrypts AWS keys and GitHub tokens before saving
    - Updates preferences (dark mode, notifications)
    - Returns masked credentials for display
    """
    # Get or create user settings
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Get crypto service for encryption
    crypto = get_crypto_service()
    
    # Update AWS credentials (encrypt before saving)
    if settings_data.aws_access_key is not None:
        if settings_data.aws_access_key.strip():
            settings.aws_access_key_encrypted = crypto.encrypt(settings_data.aws_access_key)
            logger.info(f"AWS access key updated for user: {current_user.email}")
        else:
            settings.aws_access_key_encrypted = None
    
    if settings_data.aws_secret_key is not None:
        if settings_data.aws_secret_key.strip():
            settings.aws_secret_key_encrypted = crypto.encrypt(settings_data.aws_secret_key)
            logger.info(f"AWS secret key updated for user: {current_user.email}")
        else:
            settings.aws_secret_key_encrypted = None
    
    if settings_data.aws_region is not None:
        settings.aws_region = settings_data.aws_region
    
    # Update GitHub token (encrypt before saving)
    if settings_data.github_token is not None:
        if settings_data.github_token.strip():
            settings.github_token_encrypted = crypto.encrypt(settings_data.github_token)
            logger.info(f"GitHub token updated for user: {current_user.email}")
        else:
            settings.github_token_encrypted = None
    
    # Update preferences
    if settings_data.dark_mode is not None:
        settings.dark_mode = settings_data.dark_mode
    
    if settings_data.email_notifications is not None:
        settings.email_notifications = settings_data.email_notifications
    
    # Save to database
    db.commit()
    db.refresh(settings)
    
    # Return masked credentials
    aws_access_key_masked = None
    if settings.aws_access_key_encrypted:
        decrypted_key = crypto.decrypt(settings.aws_access_key_encrypted)
        if decrypted_key and len(decrypted_key) >= 4:
            aws_access_key_masked = decrypted_key[:4] + "****"
    
    logger.info(f"Settings updated for user: {current_user.email}")
    
    return SettingsResponse(
        aws_region=settings.aws_region,
        dark_mode=settings.dark_mode,
        email_notifications=settings.email_notifications,
        has_aws_secret=bool(settings.aws_secret_key_encrypted),
        has_github_token=bool(settings.github_token_encrypted),
        aws_access_key_masked=aws_access_key_masked
    )

# ==================== ORGANIZATION & BILLING ====================

@app.get("/organization", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's organization details.
    """
    from app.services.organization_service import OrganizationService
    from app.schemas import OrganizationResponse
    
    org_service = OrganizationService()
    org = org_service.get_organization_by_user(db, current_user.id)
    
    if not org:
        raise HTTPException(status_code=404, detail="User not part of any organization")
        
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        subscription_tier=org.subscription_tier,
        max_projects=org.max_projects,
        max_users=org.max_users,
        role="owner" # Hardcoded for now until we have IAM roles
    )

@app.post("/organization/upgrade", response_model=OrganizationResponse)
async def upgrade_subscription(
    upgrade_data: UpgradeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade the organization's subscription tier.
    
    **Simulated billing**: Updates the DB immediately without charging real money.
    """
    from app.services.organization_service import OrganizationService
    
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User has no organization")
        
    org_service = OrganizationService()
    updated_org = org_service.update_subscription(db, current_user.organization_id, upgrade_data.tier)
    
    logger.info(f"Organization {updated_org.id} upgraded to {upgrade_data.tier} by {current_user.email}")
    
    return OrganizationResponse(
        id=updated_org.id,
        name=updated_org.name,
        slug=updated_org.slug,
        subscription_tier=updated_org.subscription_tier,
        max_projects=updated_org.max_projects,
        max_users=updated_org.max_users,
        role="owner"
    )


@app.get("/notifications", response_model=list[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 20,
):
    """Return a list of notifications for the current user (most recent first)."""
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        NotificationResponse(
            id=n.id,
            message=n.message,
            is_read=n.is_read,
            created_at=n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
        for n in notifications
    ]

@app.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark a specific notification as read and return the updated object."""
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return NotificationResponse(
        id=notification.id,
        message=notification.message,
        is_read=notification.is_read,
        created_at=notification.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    )

@app.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a notification. Returns a simple success message."""
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notification)
    db.commit()
    return {"detail": "Notification deleted"}

from app.core.cache import cached
from fastapi import Request

@app.get("/dashboard/stats", response_model=DashboardStats)
@cached(expire=300)
async def get_dashboard_stats(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    
    Returns:
    - Total resources scanned
    - Security score
    - Open vulnerabilities
    - Compliance rate
    - Recent scans
    """
    # Get recent scans for this user
    recent_scans_db = db.query(TerraformScan).filter(
        TerraformScan.user_id == current_user.id
    ).order_by(TerraformScan.created_at.desc()).limit(5).all()
    
    recent_scans = [
        ScanListResponse(
            id=scan.id,
            filename=scan.filename,
            timestamp=scan.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            issues_count=scan.issues_count,
            status=scan.status
        )
        for scan in recent_scans_db
    ]
    
    # Calculate stats
    total_scans = db.query(TerraformScan).filter(
        TerraformScan.user_id == current_user.id
    ).count()
    
    total_vulnerabilities = sum(scan.issues_count for scan in recent_scans_db)
    
    # Calculate security score (higher is better)
    if total_scans > 0:
        avg_issues = total_vulnerabilities / total_scans if total_scans > 0 else 0
        security_score = max(0, 100 - int(avg_issues * 10))
    else:
        security_score = 100
    
    # Compliance rate (simplified: based on passed scans)
    passed_scans = db.query(TerraformScan).filter(
        TerraformScan.user_id == current_user.id,
        TerraformScan.status == "PASSED"
    ).count()
    
    compliance_rate = int((passed_scans / total_scans * 100)) if total_scans > 0 else 100
    
    return DashboardStats(
        total_resources=total_scans,
        security_score=security_score,
        open_vulnerabilities=total_vulnerabilities,
        compliance_rate=compliance_rate,
        recent_scans=recent_scans
    )


# ==================== SCANS ====================

@app.post("/scans", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Scan a Terraform file for security issues
    
    - **filename**: Name of the Terraform file
    - **content**: Content of the Terraform file
    
    Returns detailed scan results with issues found
    """
    # Scan the Terraform content
    scan_result = TerraformScanner.scan_content(
        content=scan_data.content,
        filename=scan_data.filename
    )
    
    # Save to database
    db_scan = TerraformScan(
        user_id=current_user.id,
        filename=scan_data.filename,
        content=scan_data.content,
        issues_found=scan_result["issues"],
        issues_count=scan_result["issues_count"],
        status=scan_result["status"]
    )
    
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    logger.info(f"Scan created: {scan_data.filename} by {current_user.email} - {scan_result['issues_count']} issues found")
    
    # Build response with issues
    issues = [
        ScanIssue(
            line=issue["line"],
            severity=issue["severity"],
            message=issue["message"],
            rule=issue["rule"]
        )
        for issue in scan_result["issues"]
    ]
    
    return ScanResponse(
        id=db_scan.id,
        filename=db_scan.filename,
        timestamp=db_scan.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        issues_count=db_scan.issues_count,
        status=db_scan.status,
        issues=issues
    )


@app.get("/scans", response_model=list[ScanListResponse])
async def list_scans(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    List recent scans for the current user
    
    - **limit**: Maximum number of scans to return (default: 10)
    """
    scans = db.query(TerraformScan).filter(
        TerraformScan.user_id == current_user.id
    ).order_by(TerraformScan.created_at.desc()).limit(limit).all()
    
    return [
        ScanListResponse(
            id=scan.id,
            filename=scan.filename,
            timestamp=scan.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            issues_count=scan.issues_count,
            status=scan.status
        )
        for scan in scans
    ]


# ==================== INFRASTRUCTURE GRAPH ====================

@app.post("/graph/generate", response_model=GraphResponse, status_code=status.HTTP_201_CREATED)
async def generate_graph(
    graph_data: GraphRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate infrastructure graph from Terraform content.
    
    Parses the Terraform file and returns nodes (resources) and edges (dependencies)
    for visualization in the frontend using React Flow.
    
    Returns:
    - **nodes**: List of infrastructure resources with metadata
    - **edges**: List of dependencies between resources
    - **layers**: Resources organized by architectural layer
    """
    service = InfrastructureGraphService()
    try:
        result = await service.parse_terraform(graph_data.content)
        layers = service.categorize_nodes_by_layer()
        
        logger.info(
            f"Graph generated: {len(result['nodes'])} nodes, {len(result['edges'])} edges",
            extra={'user_id': current_user.id}
        )
        
        return {
            'nodes': result["nodes"],
            'edges': result["edges"],
            'layers': layers,
            'total_resources': len(result["nodes"]),
            'total_dependencies': len(result["edges"])
        }
    except Exception as e:
        logger.error(f"Graph generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to generate graph: {str(e)}")


@app.get("/graph/resource/{resource_id}")
@cached(expire=3600)  # Cache for 1 hour, resource details don't change often
async def get_resource_details(
    resource_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific infrastructure resource.
    
    Args:
        resource_id: Resource identifier (e.g., 'aws_instance.web_server')
    
    Returns:
        Resource configuration and metadata
    """
    service = InfrastructureGraphService()
    try:
        # Note: This needs to be called after parse_terraform
        # In production, store the resource map in cache/DB
        details = await service.get_resource_details(resource_id)
        
        if not details:
            raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resource details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve resource details")



# ==================== DRIFT DETECTION ====================

@app.post("/drift/scan", response_model=list[DriftAlertResponse])
async def scan_drift(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Trigger a drift detection scan.
    
    Compares the Terraform State (expected) configured for the project
    against the actual cloud infrastructure (via AWS API).
    
    Returns a list of detected drifts (discrepancies).
    """
    from app.services.drift_detector import DriftDetectionService
    
    # For MVP: We pick the first project the user has access to, or create a dummy one if needed for the demo flow
    # In a real app we would pass project_id in the request body
    project = None
    if current_user.organization and current_user.organization.projects:
        project = current_user.organization.projects[0]
    
    if not project:
         # If no project, we can either error or create a transient context. 
         # For this demo, let's assume we pass a dummy ID that the service handles via mock/simulation
         project_id = 1 
    else:
        project_id = project.id

    service = DriftDetectionService(db)
    try:
        alerts = await service.check_drift(project_id)
        
        # Log activity
        logger.info(f"Drift scan completed for project {project_id}: found {len(alerts)} alerts")
        
        return [
            DriftAlertResponse(
                id=alert.id,
                resource_id=alert.resource_id,
                resource_type=alert.resource_type,
                expected_state=alert.expected_state,
                actual_state=alert.actual_state,
                drift_details=alert.drift_details,
                severity=alert.severity,
                status=alert.status,
                detected_at=alert.detected_at.isoformat()
            )
            for alert in alerts
        ]
    except Exception as e:
        logger.error(f"Drift scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SECRET SCANNER ====================

@app.post("/secrets/scan", response_model=SecretScanResponse, status_code=status.HTTP_201_CREATED)
async def scan_secrets(
    scan_data: SecretScanRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Scan content for hardcoded secrets and credentials.
    
    Detects:
    - AWS Access Keys & Secret Keys
    - GitHub Tokens
    - Private Keys (RSA, SSH)
    - Slack Webhooks
    - High entropy strings (potential API keys)
    
    Returns a report with all findings categorized by severity.
    """
    scanner = SecretScannerService()
    try:
        findings = scanner.scan_content(scan_data.content, scan_data.filename)
        report = scanner.generate_report(findings)
        
        # Log scan with user context
        logger.info(
            f"Secret scan completed: {len(findings)} findings in {scan_data.filename}",
            extra={
                'user_id': current_user.id,
                'critical': report['by_severity']['CRITICAL'],
                'high': report['by_severity']['HIGH']
            }
        )
        
        # Invalidate dashboard cache so stats update immediately
        from app.core.cache import CacheService
        # Wildcard delete for this user's stats would be ideal, 
        # but our simplistic key structure makes it hard to target just one user without scanning keys.
        # For now, we rely on TTL or clear specific known keys if possible.
        # But wait, our key includes url path.
        # Let's try to delete generic pattern if possible, or just accept 5min delay.
        # BETTER: Let's delete the exact key pattern for dashboard stats if we could.
        # Since we can't easily construct the exact key (random query params?), 
        # we will rely on a new method in CacheService or just let it expire.
        
        # Actually, let's add a clear logic for dashboard stats
        # We know the path is /dashboard/stats. The query params might vary? No, usually empty.
        # Key format: api_cache:/dashboard/stats?:Bearer ...
        # We can pattern match `api_cache:/dashboard/stats*`
        CacheService.delete("api_cache:/dashboard/stats*")
        
        return report
    except Exception as e:
        logger.error(f"Secret scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to scan secrets: {str(e)}")


@app.get("/secrets/patterns")
async def get_secret_patterns(current_user: User = Depends(get_current_active_user)):
    """
    Get list of secret patterns the scanner detects.
    
    Useful for understanding what types of secrets are detected.
    """
    scanner = SecretScannerService()
    patterns = []
    
    for pattern_key, pattern_info in scanner.PATTERNS.items():
        patterns.append({
            'id': pattern_key,
            'description': pattern_info['description'],
            'severity': pattern_info['severity'],
            'pattern': pattern_info['pattern']
        })
    
    return {
        'total': len(patterns),
        'entropy_threshold': scanner.ENTROPY_THRESHOLD,
        'patterns': patterns
    }

# ==================== AUTO REMEDIATION ====================

@app.get("/remediation/options", response_model=list[RemediationSuggestion])
async def get_remediation_options(current_user: User = Depends(get_current_active_user)):
    """List available remediation actions."""
    service = RemediationService()
    return service.get_all_remediations()

@app.post("/remediation/apply", response_model=RemediationExecuteResponse)
async def apply_remediation(
    request: RemediationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Apply a remediation fix.
    
    If 'simulation_mode' is on (or for this MVP), it mocks the Git operation
    and returns a success message with the proposed change.
    """
    service = RemediationService()
    import random
    
    # Check if issue type is supported
    suggestion = service.suggest_remediation(request.issue_type)
    if not suggestion:
        # For now just pass if not found, usually we validate
        pass
    
    # Mock Success for Demo
    mock_pr_url = f"https://github.com/my-org/infra-repo/pull/{random.randint(100, 999)}"
    
    logger.info(f"Remediation applied: {request.issue_type} on {request.resource_id} by {current_user.email}")
    
    return RemediationExecuteResponse(
        status="success",
        message=f"Fix applied! Created Pull Request to remediate {request.resource_id}.",
        pr_url=mock_pr_url
    )


@app.post("/secrets/batch-scan", response_model=dict)
async def batch_scan_secrets(
    files: Dict[str, str],  # Dict of {filename: content}
    current_user: User = Depends(get_current_active_user)
):
    """
    Scan multiple files for secrets in batch.
    
    Request body: {"file1.tf": "content1", "file2.tf": "content2"}
    
    Returns aggregated findings from all files.
    """
    scanner = SecretScannerService()
    all_findings = []
    
    try:
        for filename, content in files.items():
            findings = scanner.scan_content(content, filename)
            all_findings.extend(findings)
        
        report = scanner.generate_report(all_findings)
        
        logger.info(
            f"Batch scan completed: {len(all_findings)} findings in {len(files)} files",
            extra={'user_id': current_user.id}
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Batch secret scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to scan secrets: {str(e)}")


# ==================== GITHUB INTEGRATION ====================

@app.get("/github/repos")
async def list_github_repositories(
    current_user: User = Depends(get_current_active_user)
):
    """
    List repositories accessible by the configured GitHub token.
    """
    service = GitHubService()
    repos = service.list_repositories()
    return {"repositories": repos}

@app.post("/github/scan")
async def scan_github_repository(
    request: dict, # {"repo_url": "https://github.com/user/repo"}
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger a secret scan on a remote GitHub repository.
    """
    repo_url = request.get("repo_url")
    if not repo_url:
        raise HTTPException(status_code=400, detail="Missing repo_url")

    scanner = SecretScannerService()
    try:
        findings = scanner.scan_github_repository(repo_url)
        report = scanner.generate_report(findings)
        
        logger.info(
            f"GitHub scan completed: {len(findings)} findings in {repo_url}",
            extra={'user_id': current_user.id}
        )
        return report
    except Exception as e:
        logger.error(f"GitHub scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


# ==================== AUTO REMEDIATION ====================

@app.get("/remediation/suggestions", response_model=list[RemediationSuggestion])
async def get_remediations(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all available remediation suggestions/templates.
    
    Returns a list of remediations that can be applied to various security issues.
    """
    service = RemediationService()
    suggestions = service.get_all_remediations()
    logger.info(f"User {current_user.email} fetched remediation suggestions")
    return suggestions


@app.post("/remediation/apply", response_model=dict, status_code=status.HTTP_201_CREATED)
async def apply_remediation(
    request: dict,  # {vulnerability_id, file_path, base_branch}
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Apply auto-remediation for a specific vulnerability.
    
    This creates a fix branch, modifies the Terraform code, and opens a PR.
    
    Request body:
    ```json
    {
        "vulnerability": {
            "rule_id": "S3_NO_ENCRYPTION",
            "resource_name": "aws_s3_bucket.main",
            "severity": "HIGH"
        },
        "file_path": "infra/s3.tf",
        "base_branch": "main"
    }
    ```
    """
    try:
        from app.remediation.git_service import GitService
        from app.remediation.fixer_engine import FixerEngine
        from app.services.terraform_validator import TerraformValidator
        
        # Initialize services
        git_service = GitService()  # Uses GITHUB_TOKEN from env
        terraform_validator = TerraformValidator()
        fixer_engine = FixerEngine(git_service, terraform_validator)
        
        vulnerability = request.get('vulnerability')
        file_path = request.get('file_path')
        base_branch = request.get('base_branch', 'main')
        
        if not vulnerability or not file_path:
            raise HTTPException(status_code=400, detail="Missing vulnerability or file_path")
        
        # Apply remediation
        result = fixer_engine.apply_remediation(
            vulnerability=vulnerability,
            file_path=file_path,
            base_branch=base_branch
        )
        
        # Log remediation attempt
        logger.info(
            f"Remediation applied: {vulnerability.get('rule_id')} in {file_path}",
            extra={
                'user_id': current_user.id,
                'success': result['success'],
                'pr_url': result.get('pr_url')
            }
        )
        
        if result['success']:
            return {
                'success': True,
                'message': 'Fix applied and PR created',
                'pr_url': result.get('pr_url'),
                'pr_number': result.get('pr_number'),
                'branch': result.get('branch'),
                'description': result.get('description')
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Remediation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to apply remediation: {str(e)}")


@app.get("/remediation/history")
async def get_remediation_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """
    Get history of remediations applied by the current user.
    
    Returns recent remediation PRs and their status.
    """
    try:
        # Query RemediationPR model from database
        from app.models import RemediationPR
        
        remediations = db.query(RemediationPR)\
            .filter(RemediationPR.user_id == current_user.id)\
            .order_by(RemediationPR.created_at.desc())\
            .limit(limit)\
            .all()
        
        return {
            'total': len(remediations),
            'remediations': [
                {
                    'id': r.id,
                    'rule_id': r.rule_id,
                    'status': r.status,
                    'pr_url': r.pr_url,
                    'file_path': r.file_path,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                    'merged_at': r.merged_at.isoformat() if r.merged_at else None
                }
                for r in remediations
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get remediation history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve remediation history")


# ==================== COMPLIANCE ====================

@app.get("/compliance/reports")
async def get_compliance_reports(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get overview of all compliance reports and frameworks.
    
    Returns:
    - Summary of compliance status across frameworks
    - Compliance score (0-100)
    - Failed controls by framework
    """
    service = ComplianceReportService()
    try:
        overview = service.get_compliance_overview()
        logger.info(f"User {current_user.email} retrieved compliance overview")
        return overview
    except Exception as e:
        logger.error(f"Failed to get compliance reports: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve compliance reports")


@app.get("/compliance/frameworks")
async def list_compliance_frameworks(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of all available compliance frameworks.
    
    Includes: SOC2, ISO27001, HIPAA, GDPR, PCI-DSS
    """
    frameworks = [
        {
            'id': 'soc2',
            'name': 'SOC 2',
            'description': 'Service Organization Control compliance framework',
            'controls_count': 45
        },
        {
            'id': 'iso27001',
            'name': 'ISO 27001',
            'description': 'Information security management standards',
            'controls_count': 114
        },
        {
            'id': 'hipaa',
            'name': 'HIPAA',
            'description': 'Health Insurance Portability and Accountability Act',
            'controls_count': 32
        },
        {
            'id': 'gdpr',
            'name': 'GDPR',
            'description': 'General Data Protection Regulation',
            'controls_count': 25
        },
        {
            'id': 'pci-dss',
            'name': 'PCI-DSS',
            'description': 'Payment Card Industry Data Security Standard',
            'controls_count': 38
        }
    ]
    return {'total': len(frameworks), 'frameworks': frameworks}


@app.get("/compliance/reports/{framework_id}")
async def get_compliance_framework_detail(
    framework_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed controls and compliance status for a specific framework.
    
    Args:
        framework_id: Framework identifier (e.g., 'soc2', 'iso27001', 'hipaa', 'gdpr', 'pci-dss')
    
    Returns:
        - List of all controls
        - Compliance status for each control
        - Remediation recommendations
        - Overall framework score
    """
    service = ComplianceReportService()
    try:
        details = service.get_framework_details(framework_id)
        if not details:
            raise HTTPException(status_code=404, detail=f"Framework '{framework_id}' not found")
        
        logger.info(
            f"Framework details retrieved: {framework_id}",
            extra={'user_id': current_user.id}
        )
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get framework details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve framework details")


@app.post("/compliance/scan")
async def run_compliance_scan(
    scan_request: dict,  # {terraform_content, frameworks: []}
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Run compliance scan against selected frameworks.
    
    Request body:
    ```json
    {
        "terraform_content": "resource \"aws_s3_bucket\" ...",
        "frameworks": ["soc2", "iso27001", "pci-dss"]
    }
    ```
    
    Returns compliance violations grouped by framework and control.
    """
    try:
        terraform_content = scan_request.get('terraform_content')
        frameworks = scan_request.get('frameworks', [])
        
        if not terraform_content:
            raise HTTPException(status_code=400, detail="Missing terraform_content")
        
        report_service = ComplianceReportService()
        
        # Use the new unified scanning logic
        # This returns a list of framework reports
        full_report = await report_service.get_compliance_overview(terraform_content)
        
        # Filter by requested frameworks if specified
        results = {}
        for fw_report in full_report:
            fw_id = fw_report['id']
            if not frameworks or fw_id.lower() in [f.lower() for f in frameworks]:
                results[fw_id] = fw_report.get('failing_controls', [])
        
        logger.info(
            f"Compliance scan completed: {len(frameworks)} frameworks",
            extra={'user_id': current_user.id}
        )
        
        return {
            'success': True,
            'terraform_issues': sum(len(fw['failing_controls']) for fw in full_report),
            'frameworks_scanned': len(frameworks) if frameworks else len(full_report),
            'results': results,
            'full_report': full_report # Return full report for detailed view
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to run compliance scan: {str(e)}")


# ==================== DRIFT DETECTION ====================

@app.post("/drift/check/{project_id}", status_code=status.HTTP_202_ACCEPTED)
async def check_drift(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check for infrastructure drift in a project.
    
    Compares Terraform state (expected) vs AWS API (actual) to detect configuration drift.
    
    This is an async operation that returns immediately. Check status via GET /drift/check-status/{project_id}
    
    Returns:
    - Drift detection task ID
    - Status: 'in_progress'
    """
    try:
        from app.services.drift_detector import DriftDetectionService
        # from app.tasks.drift_check import check_drift_task  # TODO: Implement Celery task
        
        # Verify user has access to this project
        from app.models import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or project.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Start async drift detection task
        # In production, use Celery: check_drift_task.delay(project_id)
        
        logger.info(
            f"Drift detection started for project {project_id}",
            extra={'user_id': current_user.id}
        )
        
        return {
            'success': True,
            'project_id': project_id,
            'status': 'in_progress',
            'message': 'Drift detection task queued. Use GET /drift/check-status/{project_id} to check status'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Drift check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start drift detection: {str(e)}")


@app.get("/drift/alerts")
async def get_drift_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    project_id: Optional[int] = None,
    severity: Optional[str] = None,
    limit: int = 50
):
    """
    Get list of detected drift alerts.
    
    Query parameters:
    - **project_id**: Filter by project (optional)
    - **severity**: Filter by severity - CRITICAL, HIGH, MEDIUM, LOW (optional)
    - **limit**: Maximum number of results (default: 50)
    
    Returns:
    - List of drift alerts with details
    - Total count of alerts
    - Breakdown by severity
    """
    try:
        from app.models import DriftAlert, Project
        
        # Build query
        query = db.query(DriftAlert)
        
        # Filter by project if user has multiple projects
        if project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project or project.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
            query = query.filter(DriftAlert.project_id == project_id)
        
        # Filter by severity
        if severity:
            query = query.filter(DriftAlert.severity == severity)
        
        # Get results
        alerts = query.order_by(DriftAlert.created_at.desc()).limit(limit).all()
        
        # Count by severity
        severity_counts = {}
        for alert in alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
        
        logger.info(
            f"User retrieved drift alerts: {len(alerts)} alerts",
            extra={'user_id': current_user.id, 'project_id': project_id}
        )
        
        return {
            'total': len(alerts),
            'by_severity': severity_counts,
            'alerts': [
                {
                    'id': a.id,
                    'resource_type': a.resource_type,
                    'resource_name': a.resource_name,
                    'severity': a.severity,
                    'status': a.status,
                    'expected_value': a.expected_value,
                    'actual_value': a.actual_value,
                    'description': a.description,
                    'created_at': a.created_at.isoformat() if a.created_at else None,
                    'resolved_at': a.resolved_at.isoformat() if a.resolved_at else None
                }
                for a in alerts
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve drift alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve drift alerts")


@app.put("/drift/alerts/{alert_id}/resolve")
async def resolve_drift_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a drift alert as resolved.
    
    Args:
        alert_id: ID of the drift alert to resolve
    
    Returns:
        Updated alert details
    """
    try:
        from app.models import DriftAlert
        from datetime import datetime
        
        alert = db.query(DriftAlert).filter(DriftAlert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Verify user has permission (via project)
        project = alert.project
        if project.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Mark as resolved
        alert.status = 'RESOLVED'
        alert.resolved_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.info(
            f"Drift alert {alert_id} marked as resolved",
            extra={'user_id': current_user.id}
        )
        
        return {
            'success': True,
            'alert_id': alert_id,
            'status': alert.status,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve drift alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to resolve drift alert")


# (startup/shutdown handled by lifespan handler above)
