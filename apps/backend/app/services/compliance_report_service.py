from typing import List, Dict, Any

class ComplianceReportService:
    """
    Service to generate compliance reports based on security standards.
    """

    FRAMEWORKS = {
        "SOC2": {
            "name": "SOC 2 Type II",
            "description": "Service Organization Control 2",
            "controls": [
                {"id": "CC6.1", "name": "Logical Access Security", "status": "PASS", "details": "MFA enforced for all users"},
                {"id": "CC6.3", "name": "Data Encryption", "status": "FAIL", "details": "Unencrypted EBS volumes detected"},
                {"id": "CC7.1", "name": "Vulnerability Scanning", "status": "PASS", "details": "Daily scans enabled"},
                {"id": "A1.2", "name": "Data Retention", "status": "PASS", "details": "S3 Lifecycle policies active"}
            ]
        },
        "ISO27001": {
            "name": "ISO/IEC 27001:2013",
            "description": "Information Security Management",
            "controls": [
                {"id": "A.9.2.1", "name": "User Registration", "status": "PASS", "details": "Centralized IAM management"},
                {"id": "A.10.1.1", "name": "Cryptographic Controls", "status": "FAIL", "details": "Missing rotation for some KMS keys"},
                {"id": "A.12.3.1", "name": "Information Backup", "status": "PASS", "details": "Automated RDS backups enabled"}
            ]
        },
        "GDPR": {
            "name": "GDPR",
            "description": "General Data Protection Regulation",
            "controls": [
                {"id": "Art. 32", "name": "Security of Processing", "status": "WARNING", "details": "Review encryption at rest for PII"},
                {"id": "Art. 25", "name": "Data Protection by Design", "status": "PASS", "details": "Privacy reviews integrated in CI/CD"}
            ]
        }
    }

    def get_compliance_overview(self) -> List[Dict[str, Any]]:
        """
        Get high-level compliance status for all frameworks.
        """
        overview = []
        for key, data in self.FRAMEWORKS.items():
            total = len(data["controls"])
            passed = sum(1 for c in data["controls"] if c["status"] == "PASS")
            score = int((passed / total) * 100)
            
            overview.append({
                "id": key,
                "name": data["name"],
                "description": data["description"],
                "score": score,
                "status": "COMPLIANT" if score == 100 else "NON_COMPLIANT" if score < 70 else "AT_RISK",
                "controls_count": total,
                "passing_count": passed
            })
        return overview

    def get_framework_details(self, framework_id: str) -> Dict[str, Any]:
        """
        Get detailed controls for a specific framework.
        """
        return self.FRAMEWORKS.get(framework_id, {})
