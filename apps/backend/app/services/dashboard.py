from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta

class SecurityScore(BaseModel):
    score: int
    issues_prevented: int
    active_developers: int

class ScanResult(BaseModel):
    id: str
    filename: str
    timestamp: datetime
    issues_found: int
    status: str

class DashboardService:
    def get_security_score(self) -> SecurityScore:
        return SecurityScore(
            score=85,
            issues_prevented=124,
            active_developers=12
        )

    def get_recent_scans(self) -> List[ScanResult]:
        return [
            ScanResult(
                id="scan-001",
                filename="infra/main.tf",
                timestamp=datetime.now() - timedelta(minutes=5),
                issues_found=2,
                status="BLOCKED"
            ),
            ScanResult(
                id="scan-002",
                filename="apps/backend/s3.tf",
                timestamp=datetime.now() - timedelta(hours=1),
                issues_found=0,
                status="PASSED"
            ),
            ScanResult(
                id="scan-003",
                filename="infra/rds.tf",
                timestamp=datetime.now() - timedelta(hours=2),
                issues_found=5,
                status="BLOCKED"
            )
        ]

    def get_issues_over_time(self) -> Dict[str, List[int]]:
        # Mock data for chart
        return {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "data": [12, 19, 3, 5, 2, 3, 10]
        }
