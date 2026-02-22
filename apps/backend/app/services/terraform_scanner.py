"""
Terraform Security Scanner
Simple vulnerability detection for Terraform files
"""

import re
from typing import List, Dict
from datetime import datetime


class TerraformScanner:
    """Simple Terraform security scanner based on regex patterns"""
    
    # Security rules
    RULES = {
        "S3_PUBLIC_READ": {
            "pattern": r'acl\s*=\s*"public-read"',
            "severity": "CRITICAL",
            "message": "S3 bucket is publicly readable - potential data leak",
        },
        "S3_PUBLIC_WRITE": {
            "pattern": r'acl\s*=\s*"public-read-write"',
            "severity": "CRITICAL",
            "message": "S3 bucket has public write access - critical security risk",
        },
        "RDS_PUBLICLY_ACCESSIBLE": {
            "pattern": r'publicly_accessible\s*=\s*true',
            "severity": "HIGH",
            "message": "RDS instance is publicly accessible",
        },
        "SG_INGRESS_ALL": {
            "pattern": r'cidr_blocks\s*=\s*\["0\.0\.0\.0/0"\]',
            "severity": "HIGH",
            "message": "Security group allows traffic from anywhere (0.0.0.0/0)",
        },
        "MISSING_ENCRYPTION": {
            "pattern": r'resource\s+"aws_(s3_bucket|rds|ebs)"(?!.*encryption)',
            "severity": "MEDIUM",
            "message": "Resource may not have encryption enabled",
        },
        "NO_VERSIONING": {
            "pattern": r'resource\s+"aws_s3_bucket"(?!.*versioning)',
            "severity": "LOW",
            "message": "S3 bucket versioning not explicitly enabled",
        },
        "DEFAULT_KMS_KEY": {
            "pattern": r'kms_key_id\s*=\s*"alias/aws/s3"',
            "severity": "MEDIUM",
            "message": "Using default AWS KMS key instead of customer-managed key",
        },
        "NO_MFA_DELETE": {
            "pattern": r'versioning\s*{(?!.*mfa_delete)',
            "severity": "LOW",
            "message": "MFA Delete not enabled for versioned bucket",
        },
    }
    
    @staticmethod
    def scan_content(content: str, filename: str = "main.tf") -> Dict:
        """
        Scan Terraform content for security issues
        
        Args:
            content: Terraform file content
            filename: Name of the file being scanned
            
        Returns:
            Dict with scan results including issues found
        """
        issues = []
        lines = content.split('\n')
        
        for rule_id, rule_config in TerraformScanner.RULES.items():
            pattern = rule_config["pattern"]
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                # Find line number
                line_number = content[:match.start()].count('\n') + 1
                
                issues.append({
                    "line": line_number,
                    "severity": rule_config["severity"],
                    "message": rule_config["message"],
                    "rule": rule_id,
                    "snippet": lines[line_number - 1].strip() if line_number <= len(lines) else ""
                })
        
        # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        issues.sort(key=lambda x: (severity_order.get(x["severity"], 4), x["line"]))
        
        # Determine overall status
        status = TerraformScanner._determine_status(issues)
        
        # Count resources
        resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"'
        resources = re.findall(resource_pattern, content)
        
        return {
            "filename": filename,
            "issues": issues,
            "issues_count": len(issues),
            "status": status,
            "resources_found": len(resources),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _determine_status(issues: List[Dict]) -> str:
        """Determine scan status based on issues found"""
        if not issues:
            return "PASSED"
        
        severities = [issue["severity"] for issue in issues]
        
        if "CRITICAL" in severities:
            return "CRITICAL"
        elif "HIGH" in severities:
            return "BLOCKED"
        elif "MEDIUM" in severities:
            return "WARNING"
        else:
            return "WARNING"
    
    @staticmethod
    def calculate_security_score(issues_count: int, resources_count: int) -> int:
        """
        Calculate a security score (0-100)
        
        Args:
            issues_count: Number of issues found
            resources_count: Number of resources scanned
            
        Returns:
            Security score (0-100, higher is better)
        """
        if resources_count == 0:
            return 100
        
        # Simple formula: reduce score based on issues
        penalty_per_issue = 100 / max(resources_count, 1)
        score = max(0, 100 - (issues_count * penalty_per_issue))
        
        return int(score)
