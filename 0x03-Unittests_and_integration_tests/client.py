#!/usr/bin/env python3
"""
GitHub organization client
"""
from typing import List, Dict, Optional
from utils import get_json, memoize


class GithubOrgClient:
    """GitHub organization client"""
    
    ORG_URL = "https://api.github.com/orgs/{org}"
    
    def __init__(self, org_name: str) -> None:
        """
        Initialize client with organization name
        
        Args:
            org_name: Name of the GitHub organization
        """
        self._org_name = org_name
    
    @memoize
    def org(self) -> Dict:
        """
        Get organization information
        
        Returns:
            Dictionary containing organization data
        """
        return get_json(self.ORG_URL.format(org=self._org_name))
    
    @property
    def _public_repos_url(self) -> str:
        """
        Get public repos URL for the organization
        
        Returns:
            URL string for public repositories
        """
        return self.org["repos_url"]
    
    def public_repos(self, license: Optional[str] = None) -> List[str]:
        """
        Get list of public repositories
        
        Args:
            license: Optional license filter
            
        Returns:
            List of repository names
        """
        repos = get_json(self._public_repos_url)
        if license:
            return [
                repo["name"] for repo in repos
                if self.has_license(repo, license)
            ]
        return [repo["name"] for repo in repos]
    
    @staticmethod
    def has_license(repo: Dict, license_key: str) -> bool:
        """
        Check if repository has specific license
        
        Args:
            repo: Repository dictionary
            license_key: License key to check for
            
        Returns:
            True if repo has the license, False otherwise
        """
        license_info = repo.get("license")
        if license_info:
            return license_info.get("key") == license_key
        return False