from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    organization_id: Optional[int] = None

    class Config:
        from_attributes = True

class RefreshRequest(BaseModel):
    refresh_token: str

class SettingsUpdate(BaseModel):
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    aws_region: Optional[str] = None
    github_token: Optional[str] = None
    dark_mode: Optional[bool] = None
    email_notifications: Optional[bool] = None

class SettingsResponse(BaseModel):
    aws_region: Optional[str] = None
    dark_mode: bool = False
    email_notifications: bool = True
    has_aws_secret: bool = False
    has_github_token: bool = False
    aws_access_key_masked: Optional[str] = None

class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: str

class NotificationCreate(BaseModel):
    message: str

# ==================== SCANS ====================

class ScanCreate(BaseModel):
    filename: str
    content: str

class ScanIssue(BaseModel):
    line: int
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    message: str
    rule: str

class ScanResponse(BaseModel):
    id: int
    filename: str
    timestamp: str
    issues_count: int
    status: str  # PASSED, WARNING, BLOCKED, CRITICAL
    issues: List[ScanIssue] = []

class ScanListResponse(BaseModel):
    id: int
    filename: str
    timestamp: str
    issues_count: int
    status: str

# ==================== DASHBOARD ====================

class DashboardStats(BaseModel):
    total_resources: int
    security_score: int  # 0-100
    open_vulnerabilities: int
    compliance_rate: int  # 0-100
    recent_scans: List[ScanListResponse] = []

# ==================== GRAPH ====================

class GraphRequest(BaseModel):
    content: str

class GraphNodeData(BaseModel):
    label: str
    resource_type: str
    resource_name: str
    category: str
    icon: str
    color: str
    config: Dict[str, Any]

class GraphNode(BaseModel):
    id: str
    type: str
    data: GraphNodeData
    position: Dict[str, float]

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    animated: bool = True
    type: str = "smoothstep"
    style: Dict[str, str]

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# ==================== SECRET SCANNER ====================

class SecretScanRequest(BaseModel):
    content: str
    filename: Optional[str] = "unknown"

class SecretFinding(BaseModel):
    file: str
    line: int
    severity: str
    type: str
    description: str
    snippet: str

class SecretScanResponse(BaseModel):
    total_findings: int
    by_severity: Dict[str, int]
    findings: List[SecretFinding]

# ==================== AUTO REMEDIATION ====================

class RemediationSuggestion(BaseModel):
    id: str
    title: str
    description: str
    fix_code: str
    complexity: str

class RemediationRequest(BaseModel):
    issue_type: str
    resource_id: str
    repo_url: Optional[str] = "https://github.com/my-org/my-infra-repo"

class RemediationExecuteResponse(BaseModel):
    status: str
    message: str
    pr_url: Optional[str] = None

# ==================== COMPLIANCE ====================

class ComplianceOverview(BaseModel):
    id: str
    name: str
    description: str
    score: int
    status: str
    controls_count: int
    passing_count: int

class ComplianceControl(BaseModel):
    id: str
    name: str
    status: str
    details: str

class ComplianceFrameworkDetail(BaseModel):
    name: str
    description: str
    controls: List[ComplianceControl]

# ==================== ORGANIZATION & BILLING ====================

class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    subscription_tier: str
    max_projects: int
    max_users: int
    role: str = "owner" # For UI display

class SubscriptionInfo(BaseModel):
    current_tier: str
    features: List[str]
    next_billing_date: str

class UpgradeRequest(BaseModel):
    tier: str # pro, enterprise


# ==================== DRIFT DETECTION ====================

class DriftAlertResponse(BaseModel):
    id: int
    resource_id: str
    resource_type: str
    expected_state: Dict[str, Any]
    actual_state: Dict[str, Any]
    drift_details: Dict[str, Any]
    severity: str
    status: str
    detected_at: str
