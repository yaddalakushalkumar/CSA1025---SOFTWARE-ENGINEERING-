"""
Integration Tests for FastAPI REST Endpoints
=============================================
Tests API routing, schema validation, data retrieval, and optimization execution.
"""

import unittest
from fastapi.testclient import TestClient
from api.main import app


class TestApiRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertGreater(data["loaded_assets_count"], 0)

    def test_list_assets(self):
        res = self.client.get("/api/assets")
        self.assertEqual(res.status_code, 200)
        assets = res.json()
        self.assertGreaterEqual(len(assets), 20)

    def test_get_single_asset(self):
        res = self.client.get("/api/assets/BR-101")
        self.assertEqual(res.status_code, 200)
        asset = res.json()
        self.assertEqual(asset["id"], "BR-101")

    def test_get_risk_assessment(self):
        res = self.client.get("/api/risk-assessment")
        self.assertEqual(res.status_code, 200)
        assessments = res.json()
        self.assertGreaterEqual(len(assessments), 20)
        self.assertIn("composite_risk_index", assessments[0])

    def test_network_topology(self):
        res = self.client.get("/api/network/topology")
        self.assertEqual(res.status_code, 200)
        top = res.json()
        self.assertIn("nodes", top)
        self.assertIn("edges", top)

    def test_optimize_endpoint(self):
        res = self.client.post("/api/optimize?budget_limit=10000000&max_crew_days=1500")
        self.assertEqual(res.status_code, 200)
        summary = res.json()
        self.assertIn("total_budget_allocated_usd", summary)
        self.assertIn("schedule", summary)

    def test_scenario_simulation(self):
        body = {
            "budget_limit_usd": 12000000,
            "max_crew_days": 1600,
            "extreme_weather_multiplier": 1.2,
            "equity_weight_boost": 1.5,
            "emergency_route_weight_boost": 1.2,
            "planning_horizon_years": 5
        }
        res = self.client.post("/api/simulate", json=body)
        self.assertEqual(res.status_code, 200)
        sim = res.json()
        self.assertIn("district_equity_distribution", sim)


if __name__ == "__main__":
    unittest.main()
