from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class RuleResult(BaseModel):
    passed: bool
    rule_id: str
    resource_id: str
    resource_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title: str
    description: str
    remediation: str
    raw_details: Optional[Dict[str, Any]] = None


class BaseRule(ABC):
    rule_id: str = "BASE_RULE"
    name: str = "Base Rule"
    category: str = "General"  # S3, IAM, EC2, RDS
    severity: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    description: str = ""
    remediation: str = ""

    @abstractmethod
    def evaluate(self, resource: Dict[str, Any]) -> List[RuleResult]:
        """Evaluates a discovered resource and returns a list of RuleResult (failed findings or passes)."""
        pass
