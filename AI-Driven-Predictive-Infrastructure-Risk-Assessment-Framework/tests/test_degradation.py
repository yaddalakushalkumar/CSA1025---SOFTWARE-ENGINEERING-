"""
Unit Tests for AI Predictive Degradation Engine
================================================
Validates Weibull hazard calculations, Markov Chain state transition probabilities,
and trajectory forecasting.
"""

import unittest
from core.models import InfrastructureAsset, AssetType, SensorTelemetry, SocietalProfile, ConditionState
from core.degradation_engine import PredictiveDegradationEngine, MarkovDegradationModel


class TestDegradationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PredictiveDegradationEngine()
        self.asset_good = InfrastructureAsset(
            id="TEST-01",
            name="Test Suspension Bridge",
            asset_type=AssetType.BRIDGE,
            district="Test District",
            latitude=40.71,
            longitude=-74.00,
            year_built=2015,
            expected_lifespan_years=75,
            structural_health_index=88.0,
            daily_traffic_volume_aadt=40000,
            material_type="Prestressed Concrete",
            environmental_exposure_index=0.30,
            seismic_risk_zone=2,
            telemetry=SensorTelemetry(
                vibration_rms_g=0.4,
                strain_microstrain=250.0,
                corrosion_rate_mpy=1.5,
                acoustic_energy_db=20.0,
                telemetry_anomaly_score=0.1
            ),
            societal=SocietalProfile(
                hospital_proximity_km=2.0,
                emergency_corridor_weight=0.8,
                social_vulnerability_index=0.4,
                served_population=50000,
                detour_length_km=5.0,
                transit_dependency_ratio=0.5,
                economic_throughput_daily_usd=1000000.0,
                environmental_spillover_risk=0.3
            )
        )

        self.asset_critical = InfrastructureAsset(
            id="TEST-02",
            name="Test Aging Viaduct",
            asset_type=AssetType.HIGHWAY_CORRIDOR,
            district="Test District",
            latitude=40.72,
            longitude=-74.01,
            year_built=1958,
            expected_lifespan_years=60,
            structural_health_index=32.0,
            daily_traffic_volume_aadt=85000,
            material_type="Structural Steel",
            environmental_exposure_index=0.90,
            seismic_risk_zone=4,
            telemetry=SensorTelemetry(
                vibration_rms_g=1.8,
                strain_microstrain=920.0,
                corrosion_rate_mpy=12.5,
                acoustic_energy_db=78.0,
                telemetry_anomaly_score=0.85
            ),
            societal=SocietalProfile(
                hospital_proximity_km=1.0,
                emergency_corridor_weight=0.9,
                social_vulnerability_index=0.75,
                served_population=120000,
                detour_length_km=10.0,
                transit_dependency_ratio=0.7,
                economic_throughput_daily_usd=5000000.0,
                environmental_spillover_risk=0.8
            )
        )

    def test_condition_state_classification(self):
        self.assertEqual(self.asset_good.condition_state, ConditionState.GOOD)
        self.assertEqual(self.asset_critical.condition_state, ConditionState.CRITICAL)

    def test_weibull_failure_probability(self):
        pf_good = self.engine.calculate_failure_probability(self.asset_good, horizon_years=1.0)
        pf_crit = self.engine.calculate_failure_probability(self.asset_critical, horizon_years=1.0)

        self.assertGreater(pf_crit, pf_good)
        self.assertGreaterEqual(pf_good, 0.0)
        self.assertLessEqual(pf_good, 1.0)
        self.assertGreater(pf_crit, 0.20)

    def test_markov_state_distribution(self):
        dist = MarkovDegradationModel.project_state_distribution(self.asset_critical, years=5)
        self.assertEqual(len(dist), 6)  # Yr 0 to Yr 5
        # Each distribution vector should sum to 1.0
        for vec in dist:
            self.assertAlmostEqual(sum(vec), 1.0, places=4)

    def test_trajectory_simulation(self):
        traj = self.engine.simulate_future_trajectory(self.asset_good, years=10)
        self.assertEqual(len(traj), 10)
        # Structural health index should strictly decline over time without intervention
        for i in range(len(traj) - 1):
            self.assertGreaterEqual(traj[i]["projected_shi"], traj[i+1]["projected_shi"])


if __name__ == "__main__":
    unittest.main()
