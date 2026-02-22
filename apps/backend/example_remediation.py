"""
Usage Example for Auto-Remediation Engine

Demonstrates how to use the FixerEngine to fix vulnerabilities.
"""

import os
from app.remediation import FixerEngine, GitService

def example_fix_s3_encryption():
    """
    Example: Fix S3 bucket without encryption
    """
    # Step 1: Initialize GitService
    github_token = os.getenv("GITHUB_TOKEN")
    repository_name = "your-org/infrastructure-repo"  # Replace with actual repo
    
    git_service = GitService(
        github_token=github_token,
        repository_name=repository_name
    )
    
    # Step 2: Initialize FixerEngine
    fixer = FixerEngine(git_service)
    
    # Step 3: Define vulnerability (typically from scan results)
    vulnerability = {
        "rule_id": "S3_NO_ENCRYPTION",
        "resource_type": "aws_s3_bucket",
        "resource_name": "my_data_bucket",  # Must match Terraform resource name
        "severity": "HIGH",
        "description": "S3 bucket lacks server-side encryption"
    }
    
    # Step 4: Apply remediation
    result = fixer.apply_remediation(
        vulnerability=vulnerability,
        file_path="terraform/s3.tf",  # Path in repo
        base_branch="main"
    )
    
    # Step 5: Check result
    if result["success"]:
        print(f"✅ Fix applied successfully!")
        print(f"📋 PR URL: {result['pr_url']}")
        print(f"🌿 Branch: {result['branch']}")
    else:
        print(f"❌ Fix failed: {result['error']}")

def example_batch_remediation():
    """
    Example: Fix multiple vulnerabilities in batch
    """
    github_token = os.getenv("GITHUB_TOKEN")
    git_service = GitService(github_token, "your-org/infra")
    fixer = FixerEngine(git_service)
    
    # List of vulnerabilities from scan
    vulnerabilities = [
        {
            "rule_id": "S3_NO_ENCRYPTION",
            "resource_name": "logs_bucket",
            "file_path": "terraform/logging.tf"
        },
        {
            "rule_id": "S3_NO_ENCRYPTION",
            "resource_name": "data_bucket",
            "file_path": "terraform/storage.tf"
        }
    ]
    
    results = []
    for vuln in vulnerabilities:
        file_path = vuln.pop("file_path")  # Extract file path
        result = fixer.apply_remediation(vuln, file_path)
        results.append(result)
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    print(f"\n🎯 Remediation Summary:")
    print(f"   Total: {len(results)}")
    print(f"   Success: {successful}")
    print(f"   Failed: {len(results) - successful}")

if __name__ == "__main__":
    print("🤖 Auto-Remediation Engine - Usage Examples\n")
    
    # Check for GitHub token
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️  Set GITHUB_TOKEN environment variable first!")
        print("   export GITHUB_TOKEN='your-github-token'")
    else:
        example_fix_s3_encryption()
