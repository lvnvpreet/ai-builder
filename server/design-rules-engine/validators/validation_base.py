from typing import List, Dict, Any
from pydantic import BaseModel

class ValidationIssue(BaseModel):
    rule_id: str
    severity: str
    message: str
    location: str
    suggestions: List[str] = []

class ValidationBase:
    """Base class for all validators."""
    
    def validate(self, content: Dict[str, Any], **kwargs) -> List[ValidationIssue]:
        """Main validation method to be implemented by subclasses."""
        raise NotImplementedError
    
    def calculate_score(self, issues: List[ValidationIssue]) -> float:
        """Calculate a score based on validation issues."""
        if not issues:
            return 1.0
        
        # Weight issues by severity
        weights = {
            "error": 3,
            "warning": 2,
            "info": 1
        }
        
        total_weight = sum(weights.get(issue.severity, 1) for issue in issues)
        max_possible_weight = len(issues) * 3  # If all were errors
        
        # Score from 0 to 1, where 1 is perfect (no issues)
        score = 1 - (total_weight / max_possible_weight)
        return max(0, min(1, score))