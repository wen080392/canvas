from typing import Any, Dict, Optional
from app.rules.base import SecurityRule, SecurityIssue, Severity

class S3PublicAccessRule(SecurityRule):
    rule_id = "AWS_S3_001"
    severity = Severity.HIGH
    description = "S3 bucket should not be public"

    def check(self, resource: Dict[str, Any]) -> Optional[SecurityIssue]:
        # Check if resource is aws_s3_bucket
        if resource.get('type') != 'aws_s3_bucket':
            return None

        # Check ACL
        acl = resource.get('values', {}).get('acl')
        if not acl:
            # Sometimes acl is defined in a separate resource, but for this rule we check the bucket resource
            # If acl is missing, it defaults to private in newer providers, but let's be strict or check for 'public-read'
            pass
        
        if acl == 'public-read':
             return SecurityIssue(
                rule_id=self.rule_id,
                severity=self.severity,
                message="S3 bucket has public access enabled via ACL",
                fix_suggestion='acl = "private"'
            )
        
        return None
