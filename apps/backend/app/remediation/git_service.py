"""
Git Service - Abstraction over PyGithub

Handles all GitHub operations for auto-remediation.
"""

from typing import Optional, Dict, Any
from github import Github, GithubException
from github.Repository import Repository
from github.PullRequest import PullRequest
import base64

class GitService:
    """
    Abstraction layer for GitHub operations.
    
    Manages branch creation, file updates, and PR creation.
    """
    
    def __init__(self, github_token: str, repository_name: str):
        """
        Initialize GitHub service.
        
        Args:
            github_token: GitHub personal access token
            repository_name: Full repo name (e.g., 'user/repo')
        """
        self.gh = Github(github_token)
        self.repo: Repository = self.gh.get_repo(repository_name)
    
    def create_fix_branch(
        self,
        base_branch: str,
        fix_branch_name: str
    ) -> bool:
        """
        Create a new branch for the fix.
        
        Args:
            base_branch: Base branch name (e.g., 'main')
            fix_branch_name: New branch name (e.g., 'fix/s3-encryption-123')
        
        Returns:
            True if branch created successfully
        
        Raises:
            GithubException: If branch already exists or base not found
        """
        try:
            # Get the latest commit SHA from base branch
            base_ref = self.repo.get_git_ref(f"heads/{base_branch}")
            base_sha = base_ref.object.sha
            
            # Create new branch
            self.repo.create_git_ref(
                ref=f"refs/heads/{fix_branch_name}",
                sha=base_sha
            )
            return True
            
        except GithubException as e:
            if e.status == 422:  # Branch already exists
                print(f"Branch {fix_branch_name} already exists")
                return False
            raise
    
    def get_file_content(
        self,
        file_path: str,
        branch: str = "main"
    ) -> Optional[str]:
        """
        Read file content from repository.
        
        Args:
            file_path: Path to file in repo (e.g., 'infra/s3.tf')
            branch: Branch name
        
        Returns:
            File content as string, or None if not found
        """
        try:
            file_content = self.repo.get_contents(file_path, ref=branch)
            
            # GitHub returns base64-encoded content
            if isinstance(file_content, list):
                # It's a directory, not a file
                return None
            
            decoded_content = base64.b64decode(file_content.content).decode('utf-8')
            return decoded_content
            
        except GithubException as e:
            if e.status == 404:
                print(f"File {file_path} not found")
                return None
            raise
    
    def commit_file(
        self,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str
    ) -> bool:
        """
        Commit file changes to a branch.
        
        Args:
            file_path: File path in repo
            content: New file content
            commit_message: Commit message
            branch: Target branch
        
        Returns:
            True if committed successfully
        """
        try:
            # Get current file to obtain SHA (required for updates)
            file_obj = self.repo.get_contents(file_path, ref=branch)
            
            self.repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=file_obj.sha,
                branch=branch
            )
            return True
            
        except GithubException as e:
            print(f"Failed to commit file: {e}")
            return False
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> Optional[PullRequest]:
        """
        Create a pull request.
        
        Args:
            title: PR title
            body: PR description (markdown supported)
            head_branch: Source branch with changes
            base_branch: Target branch
        
        Returns:
            PullRequest object or None if failed
        """
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            # Add labels for categorization
            pr.add_to_labels("security", "auto-remediation")
            
            return pr
            
        except GithubException as e:
            print(f"Failed to create PR: {e}")
            return None
    
    def get_file_sha(self, file_path: str, branch: str) -> Optional[str]:
        """
        Get the SHA hash of a file (for conflict detection).
        
        Args:
            file_path: File path in repo
            branch: Branch name
        
        Returns:
            SHA hash or None if not found
        """
        try:
            file_obj = self.repo.get_contents(file_path, ref=branch)
            return file_obj.sha
        except GithubException:
            return None
