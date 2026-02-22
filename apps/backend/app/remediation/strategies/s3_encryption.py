"""
S3 Encryption Remediation Strategy

Adds server-side encryption to S3 buckets missing encryption.
"""

import re
from typing import Dict, Any
from .base_strategy import RemediationStrategy, RemediationResult

class EnforceS3EncryptionStrategy(RemediationStrategy):
    """
    Remediation strategy for S3 buckets without encryption.
    
    Adds server_side_encryption_configuration block with AES256.
    """
    
    ENCRYPTION_BLOCK = '''  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }'''
    
    def can_fix(self, vulnerability: Dict[str, Any]) -> bool:
        """Check if vulnerability is S3 encryption-related"""
        return (
            vulnerability.get('rule_id') == 'S3_NO_ENCRYPTION' or
            vulnerability.get('resource_type') == 'aws_s3_bucket' and
            'encryption' in vulnerability.get('description', '').lower()
        )
    
    def apply_fix(
        self,
        file_content: str,
        vulnerability: Dict[str, Any]
    ) -> RemediationResult:
        """
        Add encryption block to S3 bucket resource.
        
        Args:
            file_content: Terraform file content
            vulnerability: Must contain 'resource_name' (e.g., 'my_bucket')
        
        Returns:
            RemediationResult with modified content
        """
        try:
            resource_name = vulnerability.get('resource_name')
            if not resource_name:
                return RemediationResult(
                    success=False,
                    modified_content=None,
                    description="Missing resource_name in vulnerability",
                    error="Cannot identify which S3 bucket to fix"
                )
            
            # Pattern to find the S3 bucket resource block
            # Matches: resource "aws_s3_bucket" "bucket_name" { ... }
            pattern = rf'(resource\s+"aws_s3_bucket"\s+"{resource_name}"\s*\{{)'
            
            if not re.search(pattern, file_content):
                return RemediationResult(
                    success=False,
                    modified_content=None,
                    description=f"Resource aws_s3_bucket.{resource_name} not found",
                    error="Bucket resource not found in file"
                )
            
            # Check if encryption already exists (idempotency)
            if 'server_side_encryption_configuration' in file_content:
                return RemediationResult(
                    success=False,
                    modified_content=None,
                    description="Encryption already configured",
                    error=None
                )
            
            # Insert encryption block after opening brace
            # This finds the resource block and adds encryption as first statement
            modified_content = re.sub(
                pattern,
                rf'\1\n{self.ENCRYPTION_BLOCK}\n',
                file_content
            )
            
            # Validate we actually made a change
            if modified_content == file_content:
                return RemediationResult(
                    success=False,
                    modified_content=None,
                    description="Failed to insert encryption block",
                    error="Pattern matching failed"
                )
            
            return RemediationResult(
                success=True,
                modified_content=modified_content,
                description=f"Added AES256 encryption to {resource_name}",
                error=None
            )
            
        except Exception as e:
            return RemediationResult(
                success=False,
                modified_content=None,
                description="Exception during fix application",
                error=str(e)
            )
    
    def get_fix_description(self, vulnerability: Dict[str, Any]) -> str:
        """Generate PR description"""
        resource_name = vulnerability.get('resource_name', 'unknown')
        return f"""## 🔒 Security Fix: Enable S3 Encryption

**Vulnerability**: S3 bucket `{resource_name}` lacks server-side encryption

**Fix Applied**:
- Added `server_side_encryption_configuration` block
- Enabled AES256 encryption by default
- All objects uploaded to this bucket will now be encrypted at rest

**Security Impact**:
- ✅ Data protection at rest
- ✅ Compliance with data security standards
- ✅ Prevents unauthorized data access

**References**:
- [AWS S3 Encryption Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html)
"""
