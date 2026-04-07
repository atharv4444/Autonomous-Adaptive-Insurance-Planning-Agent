"""Shared data models for the insurance planning prototype."""

from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, Field, field_validator


InsuranceGoal = Literal["family_protection", "health_security", "wealth_protection", "tax_savings"]


class UserInput(BaseModel):
    """Raw user input accepted by the API and CLI."""

    age: int = Field(default=30, ge=18, le=70)
    income: float = Field(default=600000, ge=0)
    dependents: int = Field(default=0, ge=0, le=10)
    assets: float = Field(default=0, ge=0)
    liabilities: float = Field(default=0, ge=0)
    insurance_goal: InsuranceGoal = "family_protection"

    @field_validator("income", "assets", "liabilities", mode="before")
    @classmethod
    def numeric_defaults(cls, value: object) -> float:
        """Treat missing or blank numeric values as zero-like defaults."""
        if value in (None, ""):
            return 0
        return float(value)


class UserProfile(BaseModel):
    """Structured user profile derived from raw inputs."""

    age: int
    income: float
    dependents: int
    assets: float
    liabilities: float
    insurance_goal: InsuranceGoal
    net_worth: float
    affordability_band: Literal["low", "medium", "high"]
    life_stage: Literal["early_career", "family_builder", "pre_retirement"]
    liability_ratio: float


class Policy(BaseModel):
    """Local insurance policy definition."""

    policy_name: str
    policy_type: str
    coverage: float
    premium: float
    target_profile: List[str]
    notes: str


class RankedPolicy(BaseModel):
    """Policy plus evaluation details."""

    policy: Policy
    total_score: float
    suitability_score: float
    affordability_score: float
    coverage_score: float
    utility_score: float
    premium_ratio: float
    coverage_gap: float
    tradeoff_summary: str
    explanation_points: List[str]


class ScenarioBreakdown(BaseModel):
    """Expected impact for an individual simulated scenario."""

    scenario_name: str
    probability: float
    cost: float
    expected_impact: float


class ScenarioSimulationResult(BaseModel):
    """Output returned by the scenario simulation agent."""

    expected_loss: float
    scenario_breakdown: List[ScenarioBreakdown]


class CriticResult(BaseModel):
    """Validation result returned by the critic agent."""

    validated_policy: RankedPolicy
    issues: List[str]
    confidence_score: float


class MemorySnapshot(BaseModel):
    """Minimal memory payload included for traceability."""

    profile_signature: str
    previous_recommendations: List[Dict[str, object]]


class RecommendationResponse(BaseModel):
    """Final output returned by the recommender."""

    user_profile: UserProfile
    risk_score: float
    risk_label: Literal["low", "moderate", "high"]
    expected_loss: float
    scenario_breakdown: List[ScenarioBreakdown]
    best_policy: RankedPolicy
    final_recommendation: RankedPolicy
    top_policies: List[RankedPolicy]
    critic_issues: List[str]
    confidence_score: float
    memory_snapshot: MemorySnapshot
    explanation: str
