"""
Scenario Simulator & Stress-Testing Engine
===========================================
Enables stress-testing infrastructure resilience under climate shocks,
budget austerity, and alternative equity/emergency policy weighting mandates.
"""

from typing import List, Dict, Any
from core.models import InfrastructureAsset, ScenarioRequest, OptimizationSummary
from core.graph_network import InfrastructureGraphNetwork
from core.societal_impact_engine import CompositeRiskAssessor
from core.maintenance_optimizer import MaintenanceOptimizer
from config import DEFAULT_SOCIETAL_WEIGHTS


class ScenarioSimulator:
    """
    Simulates policy shifts, environmental shocks, and fiscal constraints.
    """

    def __init__(self, assets: List[InfrastructureAsset], network: InfrastructureGraphNetwork):
        self.raw_assets = assets
        self.network = network

    def run_scenario(self, request: ScenarioRequest) -> Dict[str, Any]:
        """
        Executes policy simulation with specified environmental multipliers and budget thresholds.
        """
        # Apply environmental shock multipliers if specified (> 1.0)
        simulated_assets: List[InfrastructureAsset] = []
        for asset in self.raw_assets:
            clone = asset.model_copy(deep=True)
            if request.extreme_weather_multiplier > 1.0:
                # Environmental shock accelerates corrosion, strain, and effective exposure
                shock = request.extreme_weather_multiplier
                clone.environmental_exposure_index = min(1.0, clone.environmental_exposure_index * (1.0 + 0.25 * (shock - 1.0)))
                clone.telemetry.telemetry_anomaly_score = min(1.0, clone.telemetry.telemetry_anomaly_score * shock)
                # Potential direct damage to already degraded assets
                if clone.structural_health_index < 45.0:
                    clone.structural_health_index = max(10.0, clone.structural_health_index - 4.5 * (shock - 1.0))

            simulated_assets.append(clone)

        # Recalculate weights based on policy boosts
        sim_weights = dict(DEFAULT_SOCIETAL_WEIGHTS)
        if request.equity_weight_boost != 1.0:
            sim_weights["equity_vulnerability"] *= request.equity_weight_boost
        if request.emergency_route_weight_boost != 1.0:
            sim_weights["emergency_accessibility"] *= request.emergency_route_weight_boost

        # Normalize weights
        total_w = sum(sim_weights.values())
        norm_weights = {k: v / total_w for k, v in sim_weights.items()}

        # Instantiate simulator assessor & optimizer
        assessor = CompositeRiskAssessor(network=self.network)
        optimizer = MaintenanceOptimizer(risk_assessor=assessor)

        # Baseline unmaintained projection vs. optimized intervention
        optimization_result: OptimizationSummary = optimizer.optimize_schedule(
            assets=simulated_assets,
            budget_limit=request.budget_limit_usd,
            max_crew_days=request.max_crew_days,
            weights_override=norm_weights
        )

        # Compute district-level equity breakdown
        district_summary: Dict[str, Dict[str, Any]] = {}
        for asset in simulated_assets:
            d = asset.district
            if d not in district_summary:
                district_summary[d] = {
                    "asset_count": 0,
                    "avg_svi": 0.0,
                    "allocated_investment_usd": 0.0,
                    "pre_risk": 0.0,
                    "post_risk": 0.0
                }
            district_summary[d]["asset_count"] += 1
            district_summary[d]["avg_svi"] += asset.societal.social_vulnerability_index

        for d, stats in district_summary.items():
            if stats["asset_count"] > 0:
                stats["avg_svi"] = round(stats["avg_svi"] / stats["asset_count"], 2)

        for item in optimization_result.schedule:
            matching = next(a for a in simulated_assets if a.id == item.asset_id)
            d = matching.district
            district_summary[d]["allocated_investment_usd"] += item.estimated_cost_usd

        return {
            "scenario_parameters": request.model_dump(),
            "applied_weights": norm_weights,
            "optimization_summary": optimization_result.model_dump(),
            "district_equity_distribution": district_summary
        }
