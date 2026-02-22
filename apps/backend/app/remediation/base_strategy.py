"""
Base Strategy Interface for Auto-Remediation

Defines the contract for all remediation strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class RemediationResult:
    """Result of a remediation attempt"""
    success: bool
    modified_content: Optional[str]
    description: str
    error: Optional[str] = None

class RemediationStrategy(ABC):
    """
    Abstract base class for remediation strategies.
    
    Each vulnerability type should have its own concrete implementation.
    Follows the Strategy Pattern for extensibility.
    """
    
    @abstractmethod
    def can_fix(self, vulnerability: Dict[str, Any]) -> bool:
        """
        Determine if this strategy can fix the given vulnerability.
        
        Args:
            vulnerability: Dictionary containing vulnerability details
                          (rule_id, resource_type, severity, etc.)
        
        Returns:
            True if this strategy can handle the vulnerability
        """
        pass
    
    @abstractmethod
    def apply_fix(
        self,
        file_content: str,
        vulnerability: Dict[str, Any]
    ) -> RemediationResult:
        """
        Apply the fix to the file content.
        
        Args:
            file_content: Original HCL/Terraform file content
            vulnerability: Vulnerability details
        
        Returns:
            RemediationResult with success status and modified content
        """
        pass
    
    @abstractmethod
    def get_fix_description(self, vulnerability: Dict[str, Any]) -> str:
        """
        Generate human-readable description of the fix for PR body.
        
        Args:
            vulnerability: Vulnerability details
        
        Returns:
            Markdown-formatted description
        """
        pass
