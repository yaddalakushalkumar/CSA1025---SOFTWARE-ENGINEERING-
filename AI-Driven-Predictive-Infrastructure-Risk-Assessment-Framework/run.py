"""
InfraRisk-AI: Master Execution Entrypoint
========================================
Executes an end-to-end demonstration of the framework:
1. Loads Metropolitan Infrastructure Asset Dataset
2. Executes AI Deterioration & Survival Models (Weibull & Markov)
3. Computes Multi-Dimensional Societal Impact & SVI Equity Indices
4. Runs TOPSIS Multi-Criteria Decision Prioritization
5. Solves Multi-Objective Evolutionary Maintenance Optimization
6. Simulates Climate Shock Stress-Test Scenario
7. Boots Interactive Web Dashboard & RESTful API Service
"""

import sys
import argparse
from pathlib import Path
import uvicorn

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.seed_generator import load_metropolitan_dataset
from core.graph_network import InfrastructureGraphNetwork
from core.societal_impact_engine import CompositeRiskAssessor
from core.maintenance_optimizer import MaintenanceOptimizer
from core.scenario_simulator import ScenarioSimulator
from core.models import ScenarioRequest
from config import SERVER_HOST, SERVER_PORT, DEFAULT_OPTIMIZATION_CONFIG


def run_cli_demonstration():
    print("=" * 80)
    print("  INFRASTRUCTURE RISK ASSESSMENT & SOCIETAL IMPACT OPTIMIZATION FRAMEWORK")
    print("=" * 80)
    print("Initializing regional infrastructure network...")

    assets = load_metropolitan_dataset()
    print(f" Loaded {len(assets)} metropolitan infrastructure assets across 5 districts.\n")

    network = InfrastructureGraphNetwork(assets)
    centrality = network.calculate_betweenness_centrality()
    print(f" Topological network mapped: {len(network.adjacency)} interconnected nodes.")

    # Step 1: AI Predictive Risk Assessment
    print("\n" + "-" * 80)
    print(" STEP 1: AI PREDICTIVE DETERIORATION & COMPOSITE RISK ASSESSMENT")
    print("-" * 80)

    assessor = CompositeRiskAssessor(network=network)
    assessments = [assessor.assess_asset_risk(a) for a in assets]
    # Sort descending by Composite Risk Index (CRI)
    assessments.sort(key=lambda x: x.composite_risk_index, reverse=True)

    header = f"{'ID':<8} | {'Asset Name':<38} | {'SHI':<5} | {'Pf (1y)':<7} | {'Soc Imp':<7} | {'CRI':<6} | {'Tier'}"
    print(header)
    print("-" * len(header))
    for ass in assessments[:8]:
        print(f"{ass.asset_id:<8} | {ass.asset_name:<38} | {ass.current_shi:<5.1f} | {ass.failure_probability_1yr*100:<6.1f}% | {ass.composite_societal_impact:<7.1f} | {ass.composite_risk_index:<6.1f} | {ass.priority_tier}")
    print(f"... and {len(assessments) - 8} additional assets evaluated.")

    # Step 2: TOPSIS Decision Prioritization
    print("\n" + "-" * 80)
    print(" STEP 2: TOPSIS MULTI-CRITERIA DECISION PRIORITIZATION")
    print("-" * 80)
    optimizer = MaintenanceOptimizer(risk_assessor=assessor)
    ass_dict = {a.id: assessor.assess_asset_risk(a) for a in assets}
    topsis_ranks = optimizer.run_topsis_prioritization(assets, ass_dict)

    print(f"{'Rank':<5} | {'ID':<8} | {'Asset Name':<38} | {'Closeness C*':<13} | {'CRI'}")
    print("-" * 75)
    for rank, (asset_id, score) in enumerate(topsis_ranks[:5], 1):
        matching = next(a for a in assets if a.id == asset_id)
        cri = ass_dict[asset_id].composite_risk_index
        print(f"#{rank:<4} | {asset_id:<8} | {matching.name:<38} | {score*100:<12.1f}% | {cri:.1f}")

    # Step 3: Multi-Objective Evolutionary Optimization
    print("\n" + "-" * 80)
    print(" STEP 3: CONSTRAINED MULTI-OBJECTIVE EVOLUTIONARY OPTIMIZATION")
    print("-" * 80)
    budget = DEFAULT_OPTIMIZATION_CONFIG["annual_budget"]
    crew = DEFAULT_OPTIMIZATION_CONFIG["max_crew_days"]
    print(f"Running Genetic Algorithm [Budget: ${budget:,.0f} | Labor Limit: {crew:,} crew-days]...")

    summary = optimizer.optimize_schedule(assets, budget_limit=budget, max_crew_days=crew)

    print(f"\nOptimization Results:")
    print(f" - Total Budget Allocated:      ${summary.total_budget_allocated_usd:,.2f} ({summary.budget_utilization_pct:.1f}% utilized)")
    print(f" - Crew Days Utilized:         {summary.total_crew_days_used} of {summary.crew_days_limit} days")
    print(f" - Assets Scheduled:           {summary.assets_treated_count} of {summary.total_assets}")
    print(f" - Average Network SHI:        {summary.average_network_shi_before:.1f} --> {summary.average_network_shi_after:.1f} (+{summary.average_network_shi_after - summary.average_network_shi_before:.1f} points)")
    print(f" - Network Risk Alleviation:   {summary.total_societal_risk_before:.1f} --> {summary.total_societal_risk_after:.1f} (-{summary.aggregate_risk_reduction_pct:.1f}% reduction)\n")

    print(f"{'ID':<8} | {'Scheduled Action':<32} | {'Cost ($USD)':<13} | {'Post SHI':<8} | {'Benefit-Cost'}")
    print("-" * 78)
    for act in summary.schedule[:6]:
        print(f"{act.asset_id:<8} | {act.action_label:<32} | ${act.estimated_cost_usd:<12,.0f} | {act.expected_post_shi:<8.1f} | {act.benefit_cost_ratio:.2f}x")

    # Step 4: Climate Shock What-If Simulation
    print("\n" + "-" * 80)
    print(" STEP 4: WHAT-IF CLIMATE SHOCK & EQUITY STRESS-TEST SCENARIO")
    print("-" * 80)
    sim = ScenarioSimulator(assets, network)
    sim_request = ScenarioRequest(
        budget_limit_usd=18_000_000.0,
        max_crew_days=2000,
        extreme_weather_multiplier=1.8,
        equity_weight_boost=1.6,
        emergency_route_weight_boost=1.4,
        planning_horizon_years=5
    )
    sim_results = sim.run_scenario(sim_request)
    print(f"Simulated 1.8x Extreme Flood/Weather Shock with 1.6x SVI Equity Mandate.")
    print("District Capital Distribution:")
    for dist, stats in sim_results["district_equity_distribution"].items():
        print(f"  * {dist:<30}: ${stats['allocated_investment_usd']:,.0f} (Avg SVI: {stats['avg_svi']*100:.0f}th percentile)")

    print("=" * 80)
    print(" Pipeline demonstration completed successfully!")
    print("=" * 80)


def start_server():
    print(f"\nLaunching InfraRisk-AI Server on http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"Interactive Web UI: http://{SERVER_HOST}:{SERVER_PORT}/")
    print(f"Interactive Swagger Docs: http://{SERVER_HOST}:{SERVER_PORT}/docs\n")
    uvicorn.run("api.main:app", host=SERVER_HOST, port=SERVER_PORT, reload=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InfraRisk-AI Framework Runner")
    parser.add_argument("--demo", action="store_true", help="Run CLI verification & demonstration")
    parser.add_argument("--server", action="store_true", help="Start the FastAPI web server")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help="Port to bind server to")
    args = parser.parse_args()

    # If no flags passed or --demo passed, run demonstration
    if args.demo or not args.server:
        run_cli_demonstration()

    # If --server passed, start uvicorn
    if args.server:
        SERVER_PORT = args.port
        start_server()
