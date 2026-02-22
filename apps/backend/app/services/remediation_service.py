from typing import Dict, List, Optional
import time
import random
from .github_service import GitHubService

class RemediationService:
    """
    Service to provide remediation suggestions and apply fixes via GitHub PRs.
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

    def apply_fix(self, fix_id: str, repo_url: str) -> Dict[str, str]:
        """
        Apply a fix by creating a Pull Request.
        """
        github = GitHubService()
        
        # 1. Parse Repo URL
        import re
        pattern = r"github\.com/([^/]+)/([^/.]+)"
        match = re.search(pattern, repo_url)
        if not match:
            return {"status": "error", "message": "Invalid GitHub URL"}
            
        owner, repo = match.groups()
        
        # 2. Get Remediation Details
        remediation = self.REMEDIATIONS.get(fix_id)
        if not remediation:
            return {"status": "error", "message": "Invalid Fix ID"}
            
        # 3. Create Branch
        timestamp = int(time.time())
        branch_name = f"fix/{fix_id}-{timestamp}"
        
        # Get main branch SHA
        main_ref = github.get_ref(owner, repo, "heads/main")
        if not main_ref:
            # Try master if main fails
            main_ref = github.get_ref(owner, repo, "heads/master")
            
        if not main_ref:
            return {"status": "error", "message": "Could not find main/master branch"}
            
        sha = main_ref["object"]["sha"]
        
        # Create new branch
        github.create_ref(owner, repo, f"refs/heads/{branch_name}", sha)
        
        # 4. Apply Change (Mocking file update on a specific file for demo)
        target_file = "main.tf" 
        
        # Get current content to get SHA (needed for update) or handle new file
        # For this demo, we assume we are appending/creating a file
        current_file = github.get_repository_content(owner, repo, target_file)
        
        file_sha = ""
        current_content_decoded = ""
        
        if current_file and 'content' in current_file:
            import base64
            file_sha = current_file['sha']
            try:
                current_content_decoded = base64.b64decode(current_file['content']).decode('utf-8')
            except:
                pass
        elif isinstance(current_file, list): 
             # It's a directory or something went wrong? content API returns dict for file
             pass
        
        # Append fix code
        new_content = current_content_decoded + "\n\n# Fix for " + fix_id + "\n" + remediation['fix_code']
        
        # Upadte/Create file
        github.update_file(
            owner, 
            repo, 
            target_file, 
            f"Security Fix: {remediation['title']}", 
            new_content, 
            file_sha, 
            branch_name
        )
        
        # 5. Create Pull Request
        pr = github.create_pull_request(
            owner, 
            repo, 
            title=f"Security Fix: {remediation['title']}", 
            body=f"This PR applies a security fix for **{remediation['title']}**.\n\nDescription: {remediation['description']}",
            head=branch_name,
            base="main" # or master, derived from earlier
        )
        
        if pr:
            return {
                "status": "success", 
                "pr_url": pr['html_url'], 
                "message": f"PR Created: {pr['html_url']}"
            }
        else:
             return {"status": "error", "message": "Failed to create PR"}
