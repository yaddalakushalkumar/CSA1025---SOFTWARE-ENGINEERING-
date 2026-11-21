"""
FastAPI Route Endpoints for InfraRisk-AI
========================================
Exposes REST endpoints for asset management, deterioration predictions,
societal impact scoring, network topology, and multi-objective optimization.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from core.models import (
    InfrastructureAsset,
    AssetRiskAssessment,
    OptimizationSummary,
    ScenarioRequest,
    AssetType,
    ConditionState
)
from core.graph_network import InfrastructureGraphNetwork
from core.degradation_engine import PredictiveDegradationEngine, MarkovDegradationModel
from core.societal_impact_engine import CompositeRiskAssessor, SocietalImpactEngine
from core.maintenance_optimizer import MaintenanceOptimizer
from core.scenario_simulator import ScenarioSimulator
from data.seed_generator import load_metropolitan_dataset
from config import DEFAULT_SOCIETAL_WEIGHTS, DEFAULT_OPTIMIZATION_CONFIG

router = APIRouter()

# In-memory shared state initialized from persistent JSON seed
ASSETS_CACHE: List[InfrastructureAsset] = load_metropolitan_dataset()
NETWORK_GRAPH = InfrastructureGraphNetwork(ASSETS_CACHE)
RISK_ASSESSOR = CompositeRiskAssessor(network=NETWORK_GRAPH)
OPTIMIZER = MaintenanceOptimizer(risk_assessor=RISK_ASSESSOR)
DEGRADATION_ENGINE = PredictiveDegradationEngine()


@router.get("/health")
def get_health_status():
    return {
        "status": "healthy",
        "service": "InfraRisk-AI Framework",
        "version": "1.0.0",
        "loaded_assets_count": len(ASSETS_CACHE)
    }


@router.get("/assets", response_model=List[InfrastructureAsset])
def list_assets(
    district: Optional[str] = Query(None, description="Filter by district name"),
    asset_type: Optional[AssetType] = Query(None, description="Filter by asset category"),
    min_shi: Optional[float] = Query(None, description="Filter assets with SHI >= min_shi"),
    max_shi: Optional[float] = Query(None, description="Filter assets with SHI <= max_shi")
):
    results = ASSETS_CACHE
    if district:
        results = [a for a in results if a.district.lower() == district.lower()]
    if asset_type:
        results = [a for a in results if a.asset_type == asset_type]
    if min_shi is not None:
        results = [a for a in results if a.structural_health_index >= min_shi]
    if max_shi is not None:
        results = [a for a in results if a.structural_health_index <= max_shi]
    return results


@router.get("/assets/{asset_id}", response_model=InfrastructureAsset)
def get_asset_by_id(asset_id: str):
    asset = next((a for a in ASSETS_CACHE if a.id == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found.")
    return asset


@router.get("/assets/{asset_id}/risk", response_model=AssetRiskAssessment)
def get_single_asset_risk(asset_id: str):
    asset = next((a for a in ASSETS_CACHE if a.id == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found.")
    return RISK_ASSESSOR.assess_asset_risk(asset)


@router.get("/assets/{asset_id}/trajectory")
def get_asset_trajectory(asset_id: str, years: int = Query(10, ge=1, le=20)):
    asset = next((a for a in ASSETS_CACHE if a.id == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found.")
    return {
        "asset_id": asset.id,
        "asset_name": asset.name,
        "initial_shi": asset.structural_health_index,
        "annual_degradation_rate": DEGRADATION_ENGINE.estimate_annual_degradation_rate(asset),
        "trajectory": DEGRADATION_ENGINE.simulate_future_trajectory(asset, years=years)
    }


@router.get("/assets/{asset_id}/markov")
def get_asset_markov_projections(asset_id: str, years: int = Query(5, ge=1, le=10)):
    asset = next((a for a in ASSETS_CACHE if a.id == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found.")
    
    matrix = MarkovDegradationModel.get_base_transition_matrix(asset)
    dist = MarkovDegradationModel.project_state_distribution(asset, years=years)
    
    return {
        "asset_id": asset.id,
        "transition_matrix": matrix,
        "states": ["EXCELLENT", "GOOD", "FAIR", "POOR", "CRITICAL"],
        "yearly_state_probabilities": dist
    }


@router.get("/risk-assessment", response_model=List[AssetRiskAssessment])
def assess_all_assets(
    sort_by: str = Query("composite_risk_index", description="Sort field"),
    order: str = Query("desc", description="asc or desc")
):
    assessments = [RISK_ASSESSOR.assess_asset_risk(a) for a in ASSETS_CACHE]
    reverse = (order.lower() == "desc")
    if hasattr(assessments[0], sort_by):
        assessments.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
    return assessments


@router.get("/network/topology")
def get_network_topology():
    centrality_map = NETWORK_GRAPH.calculate_betweenness_centrality()
    nodes = []
    for a in ASSETS_CACHE:
        crit = NETWORK_GRAPH.calculate_asset_criticality_index(a.id)
        ass = RISK_ASSESSOR.assess_asset_risk(a)
        nodes.append({
            "id": a.id,
            "name": a.name,
            "type": a.asset_type.value,
            "district": a.district,
            "lat": a.latitude,
            "lng": a.longitude,
            "shi": a.structural_health_index,
            "condition": a.condition_state.value,
            "cri": ass.composite_risk_index,
            "failure_prob": ass.failure_probability_1yr,
            "societal_impact": ass.composite_societal_impact,
            "centrality": centrality_map.get(a.id, 0.2),
            "criticality": crit
        })

    edges = []
    seen = set()
    for u, neighbors in NETWORK_GRAPH.adjacency.items():
        for v in neighbors:
            edge_key = tuple(sorted([u, v]))
            if edge_key not in seen:
                seen.add(edge_key)
                edges.append({"source": u, "target": v})

    return {"nodes": nodes, "edges": edges}


@router.post("/optimize", response_model=OptimizationSummary)
def run_optimization(
    budget_limit: Optional[float] = Query(None, description="Max budget in USD"),
    max_crew_days: Optional[int] = Query(None, description="Max labor crew-days"),
    emergency_weight: Optional[float] = Query(0.35),
    economic_weight: Optional[float] = Query(0.25),
    equity_weight: Optional[float] = Query(0.25),
    environmental_weight: Optional[float] = Query(0.15)
):
    weights = {
        "emergency_accessibility": emergency_weight,
        "economic_disruption": economic_weight,
        "equity_vulnerability": equity_weight,
        "environmental_hazard": environmental_weight
    }
    
    summary = OPTIMIZER.optimize_schedule(
        assets=ASSETS_CACHE,
        budget_limit=budget_limit or DEFAULT_OPTIMIZATION_CONFIG["annual_budget"],
        max_crew_days=max_crew_days or DEFAULT_OPTIMIZATION_CONFIG["max_crew_days"],
        weights_override=weights
    )
    return summary


@router.get("/prioritization/topsis")
def get_topsis_rankings():
    assessments = {a.id: RISK_ASSESSOR.assess_asset_risk(a) for a in ASSETS_CACHE}
    rankings = OPTIMIZER.run_topsis_prioritization(ASSETS_CACHE, assessments)
    results = []
    for rank, (asset_id, score) in enumerate(rankings, 1):
        asset = next(a for a in ASSETS_CACHE if a.id == asset_id)
        ass = assessments[asset_id]
        results.append({
            "rank": rank,
            "asset_id": asset_id,
            "asset_name": asset.name,
            "district": asset.district,
            "topsis_closeness_score": score,
            "cri": ass.composite_risk_index,
            "failure_probability_1yr": ass.failure_probability_1yr,
            "societal_impact": ass.composite_societal_impact,
            "svi": asset.societal.social_vulnerability_index
        })
    return results


@router.post("/simulate")
def run_simulation(request: ScenarioRequest):
    simulator = ScenarioSimulator(assets=ASSETS_CACHE, network=NETWORK_GRAPH)
    return simulator.run_scenario(request)


@router.get("/analytics/overview")
def get_analytics_overview():
    total_assets = len(ASSETS_CACHE)
    assessments = [RISK_ASSESSOR.assess_asset_risk(a) for a in ASSETS_CACHE]
    
    avg_shi = sum(a.structural_health_index for a in ASSETS_CACHE) / max(1, total_assets)
    avg_cri = sum(ass.composite_risk_index for ass in assessments) / max(1, total_assets)
    avg_pf = sum(ass.failure_probability_1yr for ass in assessments) / max(1, total_assets)
    total_econ_daily = sum(a.societal.economic_throughput_daily_usd for a in ASSETS_CACHE)
    total_pop_served = sum(a.societal.served_population for a in ASSETS_CACHE)

    # Condition distribution
    cond_counts = {c.value: 0 for c in ConditionState}
    tier_counts = {"P1 - Urgent Intervention": 0, "P2 - High Priority": 0, "P3 - Medium Scheduled": 0, "P4 - Routine Monitoring": 0}
    district_risk: Dict[str, List[float]] = {}

    for a, ass in zip(ASSETS_CACHE, assessments):
        cond_counts[a.condition_state.value] += 1
        tier_counts[ass.priority_tier] = tier_counts.get(ass.priority_tier, 0) + 1
        
        if a.district not in district_risk:
            district_risk[a.district] = []
        district_risk[a.district].append(ass.composite_risk_index)

    district_avg_risk = {
        d: round(sum(scores) / len(scores), 2)
        for d, scores in district_risk.items()
    }

    return {
        "kpis": {
            "total_assets": total_assets,
            "average_network_shi": round(avg_shi, 1),
            "average_composite_risk": round(avg_cri, 2),
            "average_failure_probability": round(avg_pf, 4),
            "total_daily_economic_throughput_usd": total_econ_daily,
            "total_served_population": total_pop_served,
            "critical_assets_count": cond_counts.get(ConditionState.CRITICAL.value, 0)
        },
        "condition_distribution": cond_counts,
        "priority_tier_distribution": tier_counts,
        "district_risk_breakdown": district_avg_risk
    }
