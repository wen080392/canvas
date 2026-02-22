"""
CloudGuardian - Main FastAPI Application
Enterprise Security & Compliance Platform
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.database import engine, get_db, Base
from app.models import User, UserSettings, TerraformScan, Notification
from app.schemas import (
    UserCreate, UserResponse, SettingsUpdate, SettingsResponse, Token,
    ScanCreate, ScanResponse, ScanListResponse, ScanIssue, DashboardStats,
    NotificationResponse, NotificationCreate,
    GraphRequest, GraphResponse,
    SecretScanRequest, SecretScanResponse,
    RemediationSuggestion,
    ComplianceOverview, ComplianceFrameworkDetail
)
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.security import get_crypto_service
from app.services.terraform_scanner import TerraformScanner
from app.services.graph_service import InfrastructureGraphService
from app.services.secret_scanner import SecretScannerService
from app.services.remediation_service import RemediationService
from app.services.compliance_report_service import ComplianceReportService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="CloudGuardian API",
    description="Automated Infrastructure Security & Compliance Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    
    # Create default settings for the user
    user_settings = UserSettings(user_id=new_user.id)
    db.add(user_settings)
    db.commit()
    
    logger.info(f"New user registered: {user_data.email}")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active
    )


@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login
    
    Use username (email) and password to get an access token
    """
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active
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

@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
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

@app.post("/graph/generate", response_model=GraphResponse)
async def generate_graph(
    graph_data: GraphRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate infrastructure graph from Terraform content.
    
    Parses the Terraform file and returns nodes (resources) and edges (dependencies)
    for visualization in the frontend.
    """
    service = InfrastructureGraphService()
    try:
        result = await service.parse_terraform(graph_data.content)
        return GraphResponse(nodes=result["nodes"], edges=result["edges"])
    except Exception as e:
        logger.error(f"Graph generation failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to generate graph: {str(e)}")


# ==================== SECRET SCANNER ====================

@app.post("/secrets/scan", response_model=SecretScanResponse)
async def scan_secrets(
    scan_data: SecretScanRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Scan content for hardcoded secrets and credentials.
    
    Detects:
    - AWS Access Keys & Secret Keys
    - GitHub Tokens
    - Private Keys (RSA, SSH)
    - Slack Webhooks
    - High entropy strings (potential API keys)
    """
    scanner = SecretScannerService()
    try:
        findings = scanner.scan_content(scan_data.content, scan_data.filename)
        report = scanner.generate_report(findings)
        return report
    except Exception as e:
        logger.error(f"Secret scan failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to scan secrets: {str(e)}")


# ==================== AUTO REMEDIATION ====================

@app.get("/remediation/suggestions", response_model=list[RemediationSuggestion])
async def get_remediations(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all available remediation suggestions.
    """
    service = RemediationService()
    return service.get_all_remediations()


# ==================== COMPLIANCE ====================

@app.get("/compliance/reports", response_model=list[ComplianceOverview])
async def get_compliance_reports(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get overview of all compliance reports.
    """
    service = ComplianceReportService()
    return service.get_compliance_overview()

@app.get("/compliance/reports/{framework_id}", response_model=ComplianceFrameworkDetail)
async def get_compliance_framework_detail(
    framework_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed controls for a specific framework.
    """
    service = ComplianceReportService()
    details = service.get_framework_details(framework_id)
    if not details:
        raise HTTPException(status_code=404, detail="Framework not found")
    return details


# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 CloudGuardian API starting up...")
    logger.info("📊 Database tables created/verified")
    logger.info("🔐 Encryption service initialized")
    logger.info("✅ API ready at http://localhost:8000")
    logger.info("📖 API docs available at http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 CloudGuardian API shutting down...")
