import os
import requests
from typing import List, Dict, Optional, Any

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _get(self, endpoint: str) -> Optional[Any]:
        if not self.token:
            print("⚠️ GITHUB_TOKEN not configured")
            return None
            
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ GitHub API Error: {e}")
            return None

    def list_repositories(self) -> List[Dict[str, Any]]:
        """List repositories for the authenticated user"""
        repos = self._get("user/repos?sort=updated&per_page=100")
        if not repos:
            return []
            
        return [
            {
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "html_url": repo["html_url"],
                "visibility": "private" if repo["private"] else "public",
                "updated_at": repo["updated_at"]
            }
            for repo in repos
        ]

    def get_repository_content(self, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        """Get content of a file or directory in a repository"""
        return self._get(f"repos/{owner}/{repo}/contents/{path}")

    def get_ref(self, owner: str, repo: str, ref: str) -> Optional[Dict[str, Any]]:
        """Get a reference (e.g., heads/main)"""
        return self._get(f"repos/{owner}/{repo}/git/ref/{ref}")

    def create_ref(self, owner: str, repo: str, ref: str, sha: str) -> Optional[Dict[str, Any]]:
        """Create a reference (breanch)"""
        url = f"{self.base_url}/repos/{owner}/{repo}/git/refs"
        try:
            response = requests.post(url, headers=self.headers, json={"ref": ref, "sha": sha})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ GitHub API Error (create_ref): {e}")
            return None

    def update_file(self, owner: str, repo: str, path: str, message: str, content: str, sha: str, branch: str) -> Optional[Dict[str, Any]]:
        """Create or update a file"""
        import base64
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        data = {
            "message": message,
            "content": encoded_content,
            "sha": sha,
            "branch": branch
        }
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ GitHub API Error (update_file): {e}")
            return None

    def create_pull_request(self, owner: str, repo: str, title: str, body: str, head: str, base: str) -> Optional[Dict[str, Any]]:
        """Create a pull request"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ GitHub API Error (create_pull_request): {e}")
            # print details if available
            try:
                print(e.response.json())
            except:
                pass
            return None
