"""
Unit Tests for Societal Impact Quantification Engine
=====================================================
Validates emergency accessibility, economic interruption, SVI equity weighting,
and Composite Risk Index (CRI) calculations.
"""

import unittest
from core.models import InfrastructureAsset, AssetType, SensorTelemetry, SocietalProfile
from core.societal_impact_engine import SocietalImpactEngine, CompositeRiskAssessor


class TestSocietalImpactEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SocietalImpactEngine()
        self.assessor = CompositeRiskAssessor()
        self.asset = InfrastructureAsset(
            id="TEST-SOC-01",
            name="Test Urban Corridor",
            asset_type=AssetType.HIGHWAY_CORRIDOR,
            district="Downtown",
            latitude=40.71,
            longitude=-74.00,
            year_built=1975,
            expected_lifespan_years=70,
            structural_health_index=50.0,
            daily_traffic_volume_aadt=65000,
            material_type="Reinforced Concrete",
            environmental_exposure_index=0.70,
            seismic_risk_zone=2,
            telemetry=SensorTelemetry(
                vibration_rms_g=1.1,
                strain_microstrain=550.0,
                corrosion_rate_mpy=6.0,
                acoustic_energy_db=45.0,
                telemetry_anomaly_score=0.4
            ),
            societal=SocietalProfile(
                hospital_proximity_km=0.8,
                emergency_corridor_weight=0.95,
                social_vulnerability_index=0.85,
                served_population=150000,
                detour_length_km=7.5,
                transit_dependency_ratio=0.75,
                economic_throughput_daily_usd=4000000.0,
                environmental_spillover_risk=0.60
            )
        )

    def test_emergency_accessibility(self):
        score = self.engine.evaluate_emergency_accessibility(self.asset)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        self.assertGreater(score, 50.0, "Emergency corridor with close hospital should score high")

    def test_equity_vulnerability(self):
        score = self.engine.evaluate_equity_vulnerability(self.asset)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        self.assertGreater(score, 60.0, "High SVI (0.85) and transit dependency should yield high score")

    def test_composite_risk_assessment(self):
        assessment = self.assessor.assess_asset_risk(self.asset)
        self.assertIsNotNone(assessment.composite_risk_index)
        self.assertGreater(assessment.composite_risk_index, 0.0)
        self.assertIn("P", assessment.priority_tier)


if __name__ == "__main__":
    unittest.main()
