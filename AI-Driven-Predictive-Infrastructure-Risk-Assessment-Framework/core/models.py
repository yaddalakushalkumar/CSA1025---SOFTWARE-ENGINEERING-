"""
Core Data Models and Schemas for InfraRisk-AI
==============================================
Contains domain entity models, Pydantic validation schemas, and calculation wrappers.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    BRIDGE = "BRIDGE"
    HIGHWAY_CORRIDOR = "HIGHWAY_CORRIDOR"
    TUNNEL = "TUNNEL"
    WATER_PIPELINE = "WATER_PIPELINE"
    ELECTRICAL_SUBSTATION = "ELECTRICAL_SUBSTATION"
    CULVERT_DRAINAGE = "CULVERT_DRAINAGE"


class ConditionState(str, Enum):
    EXCELLENT = "EXCELLENT"  # SHI: 90 - 100
    GOOD = "GOOD"            # SHI: 75 - 89
    FAIR = "FAIR"            # SHI: 55 - 74
    POOR = "POOR"            # SHI: 35 - 54
    CRITICAL = "CRITICAL"    # SHI: 0 - 34


class MaintenanceActionType(str, Enum):
    DO_NOTHING = "DO_NOTHING"
    ROUTINE_PREVENTIVE = "ROUTINE_PREVENTIVE"
    MINOR_REHABILITATION = "MINOR_REHABILITATION"
    MAJOR_RETROFIT = "MAJOR_RETROFIT"
    COMPLETE_RECONSTRUCTION = "COMPLETE_RECONSTRUCTION"


class SensorTelemetry(BaseModel):
    vibration_rms_g: float = Field(..., description="Vibration root-mean-square in g")
    strain_microstrain: float = Field(..., description="Peak structural microstrain")
    corrosion_rate_mpy: float = Field(..., description="Corrosion rate in mils per year")
    acoustic_energy_db: float = Field(..., description="Micro-crack acoustic emission energy in dB")
    telemetry_anomaly_score: float = Field(0.0, ge=0.0, le=1.0, description="Normalized sensor anomaly indicator")


class SocietalProfile(BaseModel):
    hospital_proximity_km: float = Field(..., ge=0.1, description="Distance to nearest major trauma/medical center")
    emergency_corridor_weight: float = Field(..., ge=0.0, le=1.0, description="Designated emergency primary response corridor weight")
    social_vulnerability_index: float = Field(..., ge=0.0, le=1.0, description="CDC Social Vulnerability Index (SVI) score")
    served_population: int = Field(..., ge=1, description="Resident population directly served or reliant on asset")
    detour_length_km: float = Field(..., ge=0.0, description="Average detour detour distance in event of failure")
    transit_dependency_ratio: float = Field(..., ge=0.0, le=1.0, description="Fraction of population dependent on public/shared transit")
    economic_throughput_daily_usd: float = Field(..., ge=0.0, description="Daily goods & commercial transaction value traversing link")
    environmental_spillover_risk: float = Field(..., ge=0.0, le=1.0, description="Hazardous runoff/flood containment spillover potential")


class InfrastructureAsset(BaseModel):
    id: str = Field(..., description="Unique alphanumeric identifier (e.g. BR-101)")
    name: str = Field(..., description="Human-readable asset descriptor")
    asset_type: AssetType
    district: str
    latitude: float
    longitude: float
    year_built: int
    expected_lifespan_years: int = 75
    structural_health_index: float = Field(..., ge=0.0, le=100.0, description="Current Structural Health Index (0-100)")
    daily_traffic_volume_aadt: int = Field(..., ge=0, description="Annual Average Daily Traffic")
    material_type: str = Field("Prestressed Concrete", description="Primary structural material")
    environmental_exposure_index: float = Field(..., ge=0.0, le=1.0, description="Freeze-thaw, salt, humidity exposure index")
    seismic_risk_zone: int = Field(..., ge=1, le=5, description="Seismic hazard zone tier (1=low, 5=very high)")
    connected_nodes: List[str] = Field(default_factory=list, description="IDs of topologically adjacent network nodes")
    telemetry: SensorTelemetry
    societal: SocietalProfile

    @property
    def age(self) -> int:
        return max(1, 2026 - self.year_built)

    @property
    def condition_state(self) -> ConditionState:
        shi = self.structural_health_index
        if shi >= 90:
            return ConditionState.EXCELLENT
        elif shi >= 75:
            return ConditionState.GOOD
        elif shi >= 55:
            return ConditionState.FAIR
        elif shi >= 35:
            return ConditionState.POOR
        else:
            return ConditionState.CRITICAL


class AssetRiskAssessment(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: AssetType
    current_shi: float
    condition_state: ConditionState
    failure_probability_1yr: float = Field(..., description="Probability of functional failure within 1 year")
    failure_probability_5yr: float = Field(..., description="Cumulative probability of functional failure over 5 years")
    degradation_rate_annual: float = Field(..., description="Estimated annual points of SHI deterioration without intervention")
    emergency_impact_score: float = Field(..., ge=0.0, le=100.0)
    economic_impact_score: float = Field(..., ge=0.0, le=100.0)
    equity_vulnerability_score: float = Field(..., ge=0.0, le=100.0)
    environmental_impact_score: float = Field(..., ge=0.0, le=100.0)
    composite_societal_impact: float = Field(..., ge=0.0, le=100.0)
    composite_risk_index: float = Field(..., ge=0.0, description="CRI = P_f * Societal_Impact * Criticality")
    priority_tier: str = Field("P3", description="P1 (Urgent Emergency), P2 (High), P3 (Medium), P4 (Routine)")


class RecommendedAction(BaseModel):
    asset_id: str
    asset_name: str
    recommended_action: MaintenanceActionType
    action_label: str
    estimated_cost_usd: float
    required_crew_days: int
    expected_post_shi: float
    post_failure_probability_1yr: float
    risk_reduction_achieved: float
    societal_benefit_score: float
    benefit_cost_ratio: float


class OptimizationSummary(BaseModel):
    total_budget_allocated_usd: float
    budget_limit_usd: float
    budget_utilization_pct: float
    total_crew_days_used: int
    crew_days_limit: int
    assets_treated_count: int
    total_assets: int
    average_network_shi_before: float
    average_network_shi_after: float
    total_societal_risk_before: float
    total_societal_risk_after: float
    aggregate_risk_reduction_pct: float
    schedule: List[RecommendedAction]


class ScenarioRequest(BaseModel):
    budget_limit_usd: float = Field(15_000_000.0, ge=1_000_000.0, le=100_000_000.0)
    max_crew_days: int = Field(1800, ge=200, le=5000)
    extreme_weather_multiplier: float = Field(1.0, ge=1.0, le=3.0, description="Simulate flood/freeze climate shock degradation boost")
    equity_weight_boost: float = Field(1.0, ge=0.5, le=3.0, description="Adjust weighting placed on Social Vulnerability Index")
    emergency_route_weight_boost: float = Field(1.0, ge=0.5, le=3.0, description="Adjust weighting placed on emergency medical transit")
    planning_horizon_years: int = Field(5, ge=1, le=10)
