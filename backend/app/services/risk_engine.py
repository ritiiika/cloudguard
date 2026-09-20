from typing import Any, ClassVar

from app.rules.base import RuleResult


class RiskEngine:
    """Calculates overall security posture score and risk categorizations."""

    SEVERITY_WEIGHTS: ClassVar[dict[str, int]] = {
        "CRITICAL": 25,
        "HIGH": 15,
        "MEDIUM": 7,
        "LOW": 2,
        "INFO": 0,
    }

    @classmethod
    def calculate_score(cls, findings: list[RuleResult]) -> dict[str, Any]:
        """Calculates 0-100 score where 100 is pristine and 0 is severe risk."""
        counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        total_penalty = 0

        for f in findings:
            sev = f.severity.upper()
            if sev in cls.SEVERITY_WEIGHTS:
                total_penalty += cls.SEVERITY_WEIGHTS[sev]
                counts[sev.lower()] = counts.get(sev.lower(), 0) + 1

        final_score = max(0, 100 - total_penalty)

        if final_score >= 90:
            grade = "A"
        elif final_score >= 75:
            grade = "B"
        elif final_score >= 60:
            grade = "C"
        elif final_score >= 40:
            grade = "D"
        else:
            grade = "F"

        return {
            "score": final_score,
            "grade": grade,
            "critical_count": counts["critical"],
            "high_count": counts["high"],
            "medium_count": counts["medium"],
            "low_count": counts["low"],
            "info_count": counts["info"],
            "total_findings": len(findings),
        }
