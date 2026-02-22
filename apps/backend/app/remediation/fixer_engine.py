"""
Auto-Remediation Engine

Orchestrates the automatic fixing of security vulnerabilities.
"""

from typing import List, Dict, Any, Optional
from .base_strategy import RemediationStrategy, RemediationResult
from .git_service import GitService
from .strategies.s3_encryption import EnforceS3EncryptionStrategy
from ..services.terraform_validator import TerraformValidator
from datetime import datetime, timezone

class FixerEngine:
    """
    Main orchestrator for auto-remediation.
    
    Selects appropriate strategy and coordinates GitHub operations.
    Includes Terraform validation before creating PRs.
    Follows SOLID principles: Open/Closed for new strategies.
    """
    
    def __init__(
        self,
        git_service: GitService,
        terraform_validator: Optional[TerraformValidator] = None
    ):
        """
        Initialize the remediation engine with dependency injection.
        
        Args:
            git_service: Configured GitService instance
            terraform_validator: Optional TerraformValidator for code validation
        """
        self.git_service = git_service
        self.terraform_validator = terraform_validator or TerraformValidator()
        
        # Registry of available strategies
        self.strategies: List[RemediationStrategy] = [
            EnforceS3EncryptionStrategy(),
            # Add more strategies here:
            # EnforceSecurityGroupRestrictionsStrategy(),
            # EnableRDSEncryptionStrategy(),
        ]
    
    def register_strategy(self, strategy: RemediationStrategy) -> None:
        """
        Register a new remediation strategy.
        
        Args:
            strategy: Strategy instance to register
        """
        self.strategies.append(strategy)
    
    def find_strategy(
        self,
        vulnerability: Dict[str, Any]
    ) -> Optional[RemediationStrategy]:
        """
        Find the appropriate strategy for a vulnerability.
        
        Args:
            vulnerability: Vulnerability details
        
        Returns:
            Matching strategy or None
        """
        for strategy in self.strategies:
            if strategy.can_fix(vulnerability):
                return strategy
        return None
    
    def apply_remediation(
        self,
        vulnerability: Dict[str, Any],
        file_path: str,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Apply auto-remediation for a vulnerability.
        
        This is the main entry point. It:
        1. Finds appropriate strategy
        2. Reads file from GitHub
        3. Applies fix
        4. Creates branch and PR
        
        Args:
            vulnerability: Vulnerability details (must include resource_name)
            file_path: Path to Terraform file in repo (e.g., 'infra/s3.tf')
            base_branch: Base branch to fork from
        
        Returns:
            Dictionary with remediation result and PR URL
        """
        # Step 1: Find strategy
        strategy = self.find_strategy(vulnerability)
        if not strategy:
            return {
                "success": False,
                "error": "No strategy available for this vulnerability type",
                "pr_url": None
            }
        
        # Step 2: Read current file content
        file_content = self.git_service.get_file_content(file_path, base_branch)
        if file_content is None:
            return {
                "success": False,
                "error": f"File {file_path} not found in repository",
                "pr_url": None
            }
        
        # Conflict detection: Save original SHA
        original_sha = self.git_service.get_file_sha(file_path, base_branch)
        
        # Step 3: Apply fix
        result: RemediationResult = strategy.apply_fix(file_content, vulnerability)
        
        if not result.success:
            return {
                "success": False,
                "error": result.error or result.description,
                "pr_url": None
            }
        
        # Step 3.5: VALIDATE AND FORMAT the fixed code
        validation_success, formatted_content, validation_error = \
            self.terraform_validator.validate_and_format(result.modified_content)
        
        if not validation_success:
            return {
                "success": False,
                "error": f"Terraform validation failed: {validation_error}",
                "pr_url": None,
                "validation_failed": True
            }
        
        # Use formatted content (properly indented/styled)
        final_content = formatted_content
        
        # Step 4: Create fix branch
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        rule_id = vulnerability.get('rule_id', 'fix').lower().replace('_', '-')
        fix_branch = f"cloudguardian/fix/{rule_id}-{timestamp}"
        
        branch_created = self.git_service.create_fix_branch(base_branch, fix_branch)
        if not branch_created:
            return {
                "success": False,
                "error": "Failed to create fix branch (may already exist)",
                "pr_url": None
            }
        
        # Step 5: Check for conflicts (file changed since scan)
        current_sha = self.git_service.get_file_sha(file_path, base_branch)
        if current_sha != original_sha:
            return {
                "success": False,
                "error": "File was modified since scan. Re-scan required.",
                "pr_url": None
            }
        
        # Step 6: Commit fix (using validated and formatted content)
        commit_message = f"fix(security): {result.description}"
        committed = self.git_service.commit_file(
            file_path=file_path,
            content=final_content,  # ← Validated and formatted
            commit_message=commit_message,
            branch=fix_branch
        )
        
        if not committed:
            return {
                "success": False,
                "error": "Failed to commit changes",
                "pr_url": None
            }
        
        # Step 7: Create Pull Request
        pr_title = f"[CloudGuardian] {result.description}"
        pr_body = strategy.get_fix_description(vulnerability)
        pr_body += f"\n\n---\n*Automated fix by CloudGuardian*\n"
        pr_body += f"📋 Rule: `{vulnerability.get('rule_id')}`\n"
        pr_body += f"📁 File: `{file_path}`"
        
        pr = self.git_service.create_pull_request(
            title=pr_title,
            body=pr_body,
            head_branch=fix_branch,
            base_branch=base_branch
        )
        
        if not pr:
            return {
                "success": False,
                "error": "Failed to create pull request",
                "pr_url": None
            }
        
        return {
            "success": True,
            "pr_url": pr.html_url,
            "pr_number": pr.number,
            "branch": fix_branch,
            "description": result.description
        }
