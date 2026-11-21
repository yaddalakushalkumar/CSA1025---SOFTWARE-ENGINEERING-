"""
Multi-Objective Societal Impact-Based Maintenance Optimization Framework
========================================================================
Implements:
1. Multi-Objective Genetic Algorithm (Pareto-optimal maintenance scheduling)
2. TOPSIS Multi-Criteria Decision Analysis for asset prioritization
3. Dynamic Budget-Constrained Resource Allocation under labor & safety constraints
"""

import math
import random
from typing import List, Dict, Tuple, Any
from core.models import (
    InfrastructureAsset,
    MaintenanceActionType,
    RecommendedAction,
    OptimizationSummary,
    AssetRiskAssessment
)
from core.societal_impact_engine import CompositeRiskAssessor
from core.degradation_engine import PredictiveDegradationEngine
from config import MAINTENANCE_ACTIONS, DEFAULT_OPTIMIZATION_CONFIG


class MaintenanceOptimizer:
    """
    Constrained Multi-Objective Evolutionary & MCDA Optimization Engine.
    """

    def __init__(self, risk_assessor: CompositeRiskAssessor):
        self.risk_assessor = risk_assessor
        self.degradation_engine = PredictiveDegradationEngine()

    def evaluate_action_outcome(
        self,
        asset: InfrastructureAsset,
        action: MaintenanceActionType,
        base_assessment: AssetRiskAssessment
    ) -> Dict[str, Any]:
        """
        Simulates the post-intervention state of an asset given a candidate action.
        """
        act_info = MAINTENANCE_ACTIONS[action.value]
        cost = act_info["base_cost"]
        crew_days = act_info["crew_days"]
        shi_boost = act_info["shi_restoration"]
        pf_reduction = act_info["pf_reduction_factor"]

        # Post-intervention SHI capped at 100
        post_shi = min(100.0, asset.structural_health_index + shi_boost)
        post_pf = max(0.002, base_assessment.failure_probability_1yr * pf_reduction)

        # Post-intervention composite risk
        post_cri = post_pf * base_assessment.composite_societal_impact * (
            1.0 + 0.60 * (self.risk_assessor.network.calculate_asset_criticality_index(asset.id) if self.risk_assessor.network else 0.4)
        )

        risk_reduction = max(0.0, base_assessment.composite_risk_index - post_cri)
        societal_benefit = risk_reduction * (base_assessment.composite_societal_impact / 50.0)

        # Benefit-Cost Ratio (BCR)
        bcr = (societal_benefit * 100_000.0) / max(50_000.0, cost)

        return {
            "action": action,
            "cost": cost,
            "crew_days": crew_days,
            "post_shi": round(post_shi, 1),
            "post_pf": round(post_pf, 4),
            "post_cri": round(post_cri, 2),
            "risk_reduction": round(risk_reduction, 2),
            "societal_benefit": round(societal_benefit, 2),
            "bcr": round(bcr, 2)
        }

    def run_topsis_prioritization(
        self,
        assets: List[InfrastructureAsset],
        assessments: Dict[str, AssetRiskAssessment]
    ) -> List[Tuple[str, float]]:
        """
        Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS).
        Ranks assets by urgency of maintenance intervention based on:
        Criteria: [CRI (+), Societal Impact (+), Failure Prob (+), Current SHI (-), SVI (+)]
        """
        matrix = []
        asset_ids = []

        for asset in assets:
            ass = assessments[asset.id]
            # Criteria vector: [CRI, Societal, Pf, 100-SHI, SVI] (all positive-oriented)
            vec = [
                ass.composite_risk_index,
                ass.composite_societal_impact,
                ass.failure_probability_1yr * 100.0,
                100.0 - asset.structural_health_index,
                asset.societal.social_vulnerability_index * 100.0
            ]
            matrix.append(vec)
            asset_ids.append(asset.id)

        n_rows = len(matrix)
        n_cols = len(matrix[0])
        if n_rows == 0:
            return []

        # Step 1: Normalize decision matrix
        sq_sums = [math.sqrt(sum(matrix[i][j] ** 2 for i in range(n_rows))) for j in range(n_cols)]
        norm_matrix = [
            [(matrix[i][j] / sq_sums[j] if sq_sums[j] > 0 else 0.0) for j in range(n_cols)]
            for i in range(n_rows)
        ]

        # Step 2: Weight normalized matrix
        weights = [0.30, 0.25, 0.20, 0.15, 0.10]
        weighted_matrix = [
            [norm_matrix[i][j] * weights[j] for j in range(n_cols)]
            for i in range(n_rows)
        ]

        # Step 3: Determine Ideal (A*) and Negative-Ideal (A-) solutions
        ideal_pos = [max(weighted_matrix[i][j] for i in range(n_rows)) for j in range(n_cols)]
        ideal_neg = [min(weighted_matrix[i][j] for i in range(n_rows)) for j in range(n_cols)]

        # Step 4: Calculate separation measures
        topsis_scores = []
        for i in range(n_rows):
            d_pos = math.sqrt(sum((weighted_matrix[i][j] - ideal_pos[j]) ** 2 for j in range(n_cols)))
            d_neg = math.sqrt(sum((weighted_matrix[i][j] - ideal_neg[j]) ** 2 for j in range(n_cols)))
            closeness = d_neg / (d_pos + d_neg) if (d_pos + d_neg) > 0 else 0.0
            topsis_scores.append((asset_ids[i], round(closeness, 4)))

        # Sort descending by closeness score
        topsis_scores.sort(key=lambda x: x[1], reverse=True)
        return topsis_scores

    def optimize_schedule(
        self,
        assets: List[InfrastructureAsset],
        budget_limit: float = None,
        max_crew_days: int = None,
        weights_override: Dict[str, float] = None
    ) -> OptimizationSummary:
        """
        Executes Multi-Objective Evolutionary Algorithm to discover optimal
        maintenance interventions balancing budget, labor, network risk, and equity.
        """
        budget_limit = budget_limit or DEFAULT_OPTIMIZATION_CONFIG["annual_budget"]
        max_crew_days = max_crew_days or DEFAULT_OPTIMIZATION_CONFIG["max_crew_days"]

        # Step 1: Pre-assess all assets
        assessments: Dict[str, AssetRiskAssessment] = {
            a.id: self.risk_assessor.assess_asset_risk(a, weights_override)
            for a in assets
        }

        # Candidate actions pool
        action_options = list(MaintenanceActionType)

        # Precompute outcome matrix for fast genetic evaluation
        precomputed_outcomes: Dict[str, Dict[MaintenanceActionType, Dict[str, Any]]] = {}
        for a in assets:
            precomputed_outcomes[a.id] = {}
            for act in action_options:
                precomputed_outcomes[a.id][act] = self.evaluate_action_outcome(a, act, assessments[a.id])

        # Step 2: Evolutionary Algorithm Hyperparameters
        ga_cfg = DEFAULT_OPTIMIZATION_CONFIG["genetic_algorithm"]
        pop_size = ga_cfg["population_size"]
        generations = ga_cfg["generations"]
        crossover_rate = ga_cfg["crossover_rate"]
        mutation_rate = ga_cfg["mutation_rate"]
        n_assets = len(assets)

        def generate_chromosome() -> List[MaintenanceActionType]:
            # Biased initialization: higher risk assets get more aggressive treatments
            chrom = []
            for a in assets:
                ass = assessments[a.id]
                if ass.composite_risk_index > 35.0:
                    choices = [MaintenanceActionType.MAJOR_RETROFIT, MaintenanceActionType.COMPLETE_RECONSTRUCTION, MaintenanceActionType.MINOR_REHABILITATION]
                    weights = [0.45, 0.35, 0.20]
                elif ass.composite_risk_index > 18.0:
                    choices = [MaintenanceActionType.MINOR_REHABILITATION, MaintenanceActionType.ROUTINE_PREVENTIVE, MaintenanceActionType.MAJOR_RETROFIT]
                    weights = [0.50, 0.35, 0.15]
                else:
                    choices = [MaintenanceActionType.DO_NOTHING, MaintenanceActionType.ROUTINE_PREVENTIVE]
                    weights = [0.70, 0.30]
                chrom.append(random.choices(choices, weights=weights)[0])
            return chrom

        def evaluate_fitness(chrom: List[MaintenanceActionType]) -> Tuple[float, float, int, float]:
            """
            Evaluates objective fitness:
            Maximize (Total Risk Reduction - Budget/Labor Penalties)
            """
            total_cost = 0.0
            total_crew = 0
            total_risk_reduction = 0.0
            total_shi_gain = 0.0

            for i, a in enumerate(assets):
                act = chrom[i]
                res = precomputed_outcomes[a.id][act]
                total_cost += res["cost"]
                total_crew += res["crew_days"]
                total_risk_reduction += res["risk_reduction"]
                total_shi_gain += (res["post_shi"] - a.structural_health_index)

            # Constraint penalty calculation
            penalty = 0.0
            if total_cost > budget_limit:
                penalty += ((total_cost - budget_limit) / budget_limit) * 800.0
            if total_crew > max_crew_days:
                penalty += ((total_crew - max_crew_days) / max_crew_days) * 600.0

            # Mandatory Critical Safety constraint: Critical assets (SHI < 35) must not be DO_NOTHING
            for i, a in enumerate(assets):
                if a.structural_health_index < 35.0 and chrom[i] == MaintenanceActionType.DO_NOTHING:
                    penalty += 150.0

            fitness = total_risk_reduction + 0.5 * (total_shi_gain / max(1, n_assets)) - penalty
            return fitness, total_cost, total_crew, total_risk_reduction

        # Initialize population
        population = [generate_chromosome() for _ in range(pop_size)]

        # Run Generations
        for gen in range(generations):
            scored_pop = [(chrom, evaluate_fitness(chrom)) for chrom in population]
            # Sort descending by fitness score
            scored_pop.sort(key=lambda x: x[1][0], reverse=True)

            # Elitism: retain top 10%
            n_elite = max(2, int(pop_size * ga_cfg["elite_fraction"]))
            next_generation = [item[0] for item in scored_pop[:n_elite]]

            # Tournament Selection and Crossover
            while len(next_generation) < pop_size:
                # Tournament selection for parent 1
                t1, t2 = random.sample(scored_pop, 2)
                parent1 = t1[0] if t1[1][0] > t2[1][0] else t2[0]
                t3, t4 = random.sample(scored_pop, 2)
                parent2 = t3[0] if t3[1][0] > t4[1][0] else t4[0]

                # Uniform Crossover
                if random.random() < crossover_rate:
                    child = [
                        parent1[i] if random.random() < 0.5 else parent2[i]
                        for i in range(n_assets)
                    ]
                else:
                    child = parent1[:]

                # Mutation
                for i in range(n_assets):
                    if random.random() < mutation_rate:
                        child[i] = random.choice(action_options)

                next_generation.append(child)

            population = next_generation

        # Evaluate best chromosome
        best_chrom = max(population, key=lambda c: evaluate_fitness(c)[0])
        _, best_cost, best_crew, _ = evaluate_fitness(best_chrom)

        # If best solution still exceeds budget, apply greedy repair heuristic
        if best_cost > budget_limit or best_crew > max_crew_days:
            # Downgrade actions with lowest risk reduction per cost
            action_indices = list(range(n_assets))
            # Sort by risk reduction efficiency
            action_indices.sort(
                key=lambda idx: (
                    precomputed_outcomes[assets[idx].id][best_chrom[idx]]["risk_reduction"] /
                    max(1.0, precomputed_outcomes[assets[idx].id][best_chrom[idx]]["cost"])
                )
            )
            for idx in action_indices:
                if best_cost <= budget_limit and best_crew <= max_crew_days:
                    break
                # Demote action
                curr_act = best_chrom[idx]
                if curr_act == MaintenanceActionType.COMPLETE_RECONSTRUCTION:
                    best_chrom[idx] = MaintenanceActionType.MAJOR_RETROFIT
                elif curr_act == MaintenanceActionType.MAJOR_RETROFIT:
                    best_chrom[idx] = MaintenanceActionType.MINOR_REHABILITATION
                elif curr_act == MaintenanceActionType.MINOR_REHABILITATION:
                    best_chrom[idx] = MaintenanceActionType.ROUTINE_PREVENTIVE
                elif curr_act == MaintenanceActionType.ROUTINE_PREVENTIVE:
                    best_chrom[idx] = MaintenanceActionType.DO_NOTHING

                # Recompute costs
                _, best_cost, best_crew, _ = evaluate_fitness(best_chrom)

        # Step 3: Build Schedule & Summary
        schedule: List[RecommendedAction] = []
        treated_count = 0
        sum_shi_before = sum(a.structural_health_index for a in assets)
        sum_shi_after = 0.0
        sum_risk_before = sum(assessments[a.id].composite_risk_index for a in assets)
        sum_risk_after = 0.0

        for i, a in enumerate(assets):
            chosen_act = best_chrom[i]
            res = precomputed_outcomes[a.id][chosen_act]
            sum_shi_after += res["post_shi"]
            sum_risk_after += res["post_cri"]

            if chosen_act != MaintenanceActionType.DO_NOTHING:
                treated_count += 1

            schedule.append(RecommendedAction(
                asset_id=a.id,
                asset_name=a.name,
                recommended_action=chosen_act,
                action_label=MAINTENANCE_ACTIONS[chosen_act.value]["name"],
                estimated_cost_usd=res["cost"],
                required_crew_days=res["crew_days"],
                expected_post_shi=res["post_shi"],
                post_failure_probability_1yr=res["post_pf"],
                risk_reduction_achieved=res["risk_reduction"],
                societal_benefit_score=res["societal_benefit"],
                benefit_cost_ratio=res["bcr"]
            ))

        # Sort schedule by risk reduction achieved descending
        schedule.sort(key=lambda s: s.risk_reduction_achieved, reverse=True)

        risk_red_pct = ((sum_risk_before - sum_risk_after) / sum_risk_before * 100.0) if sum_risk_before > 0 else 0.0

        return OptimizationSummary(
            total_budget_allocated_usd=round(best_cost, 2),
            budget_limit_usd=budget_limit,
            budget_utilization_pct=round((best_cost / budget_limit) * 100.0, 1),
            total_crew_days_used=best_crew,
            crew_days_limit=max_crew_days,
            assets_treated_count=treated_count,
            total_assets=n_assets,
            average_network_shi_before=round(sum_shi_before / max(1, n_assets), 1),
            average_network_shi_after=round(sum_shi_after / max(1, n_assets), 1),
            total_societal_risk_before=round(sum_risk_before, 2),
            total_societal_risk_after=round(sum_risk_after, 2),
            aggregate_risk_reduction_pct=round(risk_red_pct, 1),
            schedule=schedule
        )
