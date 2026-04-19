"""
IRDAI Compliance Checker — implements the 'Defined Environment' for regulatory rules.
This agent performs deterministic checks and flags compliance issues.
"""

from __future__ import annotations
from typing import List, Dict, Any
from app.models import RankedPolicy, UserProfile

class IRDAIComplianceChecker:
    """
    Acts as a specialized verification layer for Indian regulatory standards (IRDAI).
    It ensures that recommendations adhere to disclosure and protection standards.
    """

    def __init__(self):
        self.regulations_version = "2024.1 (Protection of Policyholders' Interests)"

    def check_compliance(self, profile: UserProfile, policy: RankedPolicy) -> Dict[str, Any]:
        """
        Runs a suite of deterministic compliance checks.
        """
        issues = []
        is_compliant = True

        # Check 1: Premium to Income Ratio
        if profile.income < 1000000 and policy.premium_ratio > 0.15:
            issues.append("Premium exceeds 15% of annual income for a moderate-income profile; suitability warning.")
            is_compliant = False

        # Check 2: Minimum coverage check
        if "term" in policy.policy.policy_type.lower() or "life" in policy.policy.policy_type.lower():
            if policy.policy.coverage < (profile.income * 5):
                issues.append("Sum assured is below 5x annual income; potentially inadequate protection.")
                is_compliant = False

        return {
            "is_compliant": is_compliant,
            "issues": issues,
            "regulations_referenced": [
                "IRDAI Insurance Advertisements and Disclosure Regulations, 2021",
                "Master Circular on Protection of Policyholders' Interests, 2024"
            ]
        }
