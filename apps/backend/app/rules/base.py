from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SecurityIssue(BaseModel):
    rule_id: str
    severity: Severity
    message: str
    line_number: Optional[int] = None
    fix_suggestion: Optional[str] = None

class SecurityRule(ABC):
    rule_id: str
    severity: Severity
    description: str

    @abstractmethod
    def check(self, resource: Dict[str, Any]) -> Optional[SecurityIssue]:
        """
        Analyzes a Terraform resource and returns a SecurityIssue if a violation is found.
        """
        pass
