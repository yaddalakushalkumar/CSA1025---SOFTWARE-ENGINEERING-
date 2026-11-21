"""
Unit Tests for Multi-Objective Maintenance Optimization Engine
==============================================================
Validates Pareto-optimal evolutionary scheduling, budget and labor constraints,
and TOPSIS prioritization.
"""

import unittest
from core.models import InfrastructureAsset, MaintenanceActionType
from core.societal_impact_engine import CompositeRiskAssessor
from core.maintenance_optimizer import MaintenanceOptimizer
from data.seed_generator import load_metropolitan_dataset


class TestOptimizationEngine(unittest.TestCase):
    def setUp(self):
        self.assets = load_metropolitan_dataset()[:8]  # Test subset of assets
        self.assessor = CompositeRiskAssessor()
        self.optimizer = MaintenanceOptimizer(risk_assessor=self.assessor)

    def test_topsis_prioritization(self):
        assessments = {a.id: self.assessor.assess_asset_risk(a) for a in self.assets}
        rankings = self.optimizer.run_topsis_prioritization(self.assets, assessments)
        self.assertEqual(len(rankings), len(self.assets))
        # Ensure closeness scores are descending
        for i in range(len(rankings) - 1):
            self.assertGreaterEqual(rankings[i][1], rankings[i+1][1])

    def test_evolutionary_optimization_budget_constraint(self):
        budget_limit = 6_000_000.0
        max_crew = 1000
        summary = self.optimizer.optimize_schedule(
            assets=self.assets,
            budget_limit=budget_limit,
            max_crew_days=max_crew
        )

        self.assertLessEqual(summary.total_budget_allocated_usd, budget_limit * 1.05)
        self.assertLessEqual(summary.total_crew_days_used, max_crew * 1.05)
        self.assertGreater(summary.aggregate_risk_reduction_pct, 0.0)
        self.assertGreater(summary.average_network_shi_after, summary.average_network_shi_before)


if __name__ == "__main__":
    unittest.main()
