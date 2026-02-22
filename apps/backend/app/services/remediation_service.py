from typing import Dict, List, Optional

class RemediationService:
    """
    Service to provide remediation suggestions for security issues.
    """

    # Knowledge base of remediations
    REMEDIATIONS = {
        "aws_s3_bucket_public": {
            "title": "Make S3 Bucket Private",
            "description": "S3 buckets should not be publicly accessible to prevent data leaks.",
            "fix_code": """
resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
""",
            "complexity": "Low"
        },
        "aws_security_group_open_ssh": {
            "title": "Restrict SSH Access",
            "description": "Security groups should not allow SSH (port 22) from 0.0.0.0/0.",
            "fix_code": """
resource "aws_security_group" "example" {
  # ... other configuration ...
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"] # Restrict to internal network or VPN
  }
}
""",
            "complexity": "Medium"
        },
        "aws_instance_unencrypted_root": {
            "title": "Encrypt EBS Volume",
            "description": "EC2 instances should have encrypted root volumes.",
            "fix_code": """
resource "aws_instance" "example" {
  # ...
  root_block_device {
    encrypted = true
  }
}
""",
            "complexity": "Low"
        },
        "aws_db_instance_public": {
            "title": "Disable Public RDS Access",
            "description": "Database instances should not be publicly accessible.",
            "fix_code": """
resource "aws_db_instance" "example" {
  # ...
  publicly_accessible = false
  # ...
}
""",
            "complexity": "Low"
        }
    }

    def suggest_remediation(self, issue_type: str) -> Optional[Dict[str, str]]:
        """
        Get remediation suggestion for a specific issue type.
        """
        return self.REMEDIATIONS.get(issue_type)

    def get_all_remediations(self) -> List[Dict[str, str]]:
        """
        Get all available remediations.
        """
        return [
            {"id": k, **v} for k, v in self.REMEDIATIONS.items()
        ]
