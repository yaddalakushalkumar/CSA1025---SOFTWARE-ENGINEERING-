"""
Societal Impact Quantification & Composite Risk Assessment Engine
==================================================================
Quantifies non-engineering societal externalities of infrastructure failure:
1. Emergency & Healthcare Accessibility Loss
2. Economic Commuter & Freight Interruption Cost
3. Equity & Social Vulnerability Index (SVI) Disproportionate Impact
4. Environmental Spillover & Carbon Hazard
Couples deterioration probabilities with societal consequences into a Composite Risk Index (CRI).
"""

import math
from typing import Dict, Tuple
from core.models import InfrastructureAsset, AssetRiskAssessment, ConditionState
from core.degradation_engine import PredictiveDegradationEngine
from core.graph_network import InfrastructureGraphNetwork
from config import DEFAULT_SOCIETAL_WEIGHTS


class SocietalImpactEngine:
    """
    Evaluates multi-dimensional societal consequences of infrastructure asset failure.
    """

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or DEFAULT_SOCIETAL_WEIGHTS
        # Normalize weights to sum to 1.0
        total_w = sum(self.weights.values())
        self.weights = {k: v / total_w for k, v in self.weights.items()}

    def evaluate_emergency_accessibility(self, asset: InfrastructureAsset) -> float:
        """
        Quantifies delay in emergency medical response, fire rescue, and disaster evacuations.
        Higher score (0-100) indicates catastrophic emergency vulnerability.
        """
        soc = asset.societal
        # Hospital proximity factor (closer to hospital means higher criticality if route fails)
        proximity_factor = 1.0 / (1.0 + 0.20 * soc.hospital_proximity_km)
        
        # Detour delay: Average emergency vehicle speed = 50 km/h -> delay = (detour / 50) * 60 mins
        detour_penalty = min(1.0, soc.detour_length_km / 10.0)

        raw_score = (
            50.0 * soc.emergency_corridor_weight +
            30.0 * proximity_factor +
            20.0 * detour_penalty
        )
        return round(min(100.0, max(0.0, raw_score)), 2)

    def evaluate_economic_disruption(self, asset: InfrastructureAsset) -> float:
        """
        Calculates daily commuter detour expense, lost productive hours, and commercial freight blockage.
        """
        soc = asset.societal
        aadt = asset.daily_traffic_volume_aadt
        detour_km = soc.detour_length_km
        daily_throughput = soc.economic_throughput_daily_usd

        # Commuter operating cost ($0.55/km fuel/wear) + Time delay (avg 40 km/h -> hours * $25/hr VOT)
        travel_time_hours = detour_km / 40.0
        daily_detour_expense = aadt * (detour_km * 0.55 + travel_time_hours * 25.0)

        # Freight & economic transaction delay (1.5% daily economic loss per detour day)
        economic_loss = daily_detour_expense + 0.015 * daily_throughput

        # Logarithmic normalization to 0 - 100 scale ($5,000/day -> 10, $500,000/day -> 90+)
        if economic_loss <= 1000:
            score = 5.0
        else:
            score = 15.0 * math.log10(economic_loss / 800.0)

        return round(min(100.0, max(0.0, score)), 2)

    def evaluate_equity_vulnerability(self, asset: InfrastructureAsset) -> float:
        """
        Evaluates equity and social vulnerability using CDC SVI and public transit reliance.
        Protects disadvantaged communities with fewer alternative travel options from being deprioritized.
        """
        soc = asset.societal
        svi = soc.social_vulnerability_index
        transit_dep = soc.transit_dependency_ratio
        pop_density_factor = min(1.0, soc.served_population / 50_000.0)

        raw_score = (
            45.0 * svi +
            35.0 * transit_dep +
            20.0 * pop_density_factor
        )
        return round(min(100.0, max(0.0, raw_score)), 2)

    def evaluate_environmental_hazard(self, asset: InfrastructureAsset) -> float:
        """
        Quantifies detour greenhouse gas emissions, flood containment spillover,
        and waterway contamination potential.
        """
        soc = asset.societal
        aadt = asset.daily_traffic_volume_aadt
        detour_km = soc.detour_length_km

        # Carbon emissions: avg 0.18 kg CO2 / passenger km
        daily_excess_co2_kg = aadt * detour_km * 0.18
        carbon_factor = min(1.0, daily_excess_co2_kg / 40_000.0)

        spillover = soc.environmental_spillover_risk

        raw_score = 55.0 * spillover + 45.0 * carbon_factor
        return round(min(100.0, max(0.0, raw_score)), 2)

    def calculate_composite_societal_impact(
        self,
        asset: InfrastructureAsset,
        weights_override: Dict[str, float] = None
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculates holistic composite societal impact score on a [0 - 100] scale.
        """
        w = weights_override or self.weights
        total_w = sum(w.values())
        norm_w = {k: v / total_w for k, v in w.items()}

        s_emerg = self.evaluate_emergency_accessibility(asset)
        s_econ = self.evaluate_economic_disruption(asset)
        s_equity = self.evaluate_equity_vulnerability(asset)
        s_env = self.evaluate_environmental_hazard(asset)

        composite = (
            norm_w.get("emergency_accessibility", 0.35) * s_emerg +
            norm_w.get("economic_disruption", 0.25) * s_econ +
            norm_w.get("equity_vulnerability", 0.25) * s_equity +
            norm_w.get("environmental_hazard", 0.15) * s_env
        )

        breakdown = {
            "emergency_score": s_emerg,
            "economic_score": s_econ,
            "equity_score": s_equity,
            "environmental_score": s_env
        }
        return round(min(100.0, max(0.0, composite)), 2), breakdown


class CompositeRiskAssessor:
    """
    Couples predictive degradation probabilities, societal impact scores,
    and topological network criticality to produce Composite Risk Indexes (CRI).
    """

    def __init__(self, network: InfrastructureGraphNetwork = None):
        self.degradation_engine = PredictiveDegradationEngine()
        self.societal_engine = SocietalImpactEngine()
        self.network = network

    def assess_asset_risk(
        self,
        asset: InfrastructureAsset,
        weights_override: Dict[str, float] = None
    ) -> AssetRiskAssessment:
        """
        Conducts full risk assessment for an asset.
        """
        pf_1yr = self.degradation_engine.calculate_failure_probability(asset, horizon_years=1.0)
        pf_5yr = self.degradation_engine.calculate_failure_probability(asset, horizon_years=5.0)
        deg_rate = self.degradation_engine.estimate_annual_degradation_rate(asset)

        soc_score, breakdown = self.societal_engine.calculate_composite_societal_impact(
            asset, weights_override=weights_override
        )

        # Network criticality factor (defaults to 0.4 if network graph not supplied)
        net_crit = self.network.calculate_asset_criticality_index(asset.id) if self.network else 0.40

        # Composite Risk Index (CRI) formula:
        # CRI = Failure_Probability * Societal_Impact * (1 + 0.60 * Network_Criticality)
        cri = pf_1yr * soc_score * (1.0 + 0.60 * net_crit)

        # Determine priority tier
        if cri >= 45.0 or (pf_1yr > 0.40 and soc_score > 60.0):
            tier = "P1 - Urgent Intervention"
        elif cri >= 25.0 or pf_1yr > 0.25:
            tier = "P2 - High Priority"
        elif cri >= 12.0:
            tier = "P3 - Medium Scheduled"
        else:
            tier = "P4 - Routine Monitoring"

        return AssetRiskAssessment(
            asset_id=asset.id,
            asset_name=asset.name,
            asset_type=asset.asset_type,
            current_shi=asset.structural_health_index,
            condition_state=asset.condition_state,
            failure_probability_1yr=pf_1yr,
            failure_probability_5yr=pf_5yr,
            degradation_rate_annual=deg_rate,
            emergency_impact_score=breakdown["emergency_score"],
            economic_impact_score=breakdown["economic_score"],
            equity_vulnerability_score=breakdown["equity_score"],
            environmental_impact_score=breakdown["environmental_score"],
            composite_societal_impact=soc_score,
            composite_risk_index=round(cri, 2),
            priority_tier=tier
        )
