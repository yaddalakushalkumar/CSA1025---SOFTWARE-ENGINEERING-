"""
AI-Driven Predictive Degradation & Structural Health Assessment Engine
======================================================================
Implements physics-informed Weibull hazard survival modeling, non-linear
gradient deterioration curves, and Markov Chain state-transition matrices
to estimate structural condition and failure probability over multi-year horizons.
"""

import math
from typing import Dict, List, Tuple
from core.models import InfrastructureAsset, ConditionState, AssetType
from config import DEGRADATION_CONFIG


class MarkovDegradationModel:
    """
    Markov Chain state-transition deterioration model for civil infrastructure.
    States: [1: Excellent, 2: Good, 3: Fair, 4: Poor, 5: Critical]
    """

    STATE_NAMES = [
        ConditionState.EXCELLENT,
        ConditionState.GOOD,
        ConditionState.FAIR,
        ConditionState.POOR,
        ConditionState.CRITICAL
    ]

    @staticmethod
    def get_base_transition_matrix(asset: InfrastructureAsset) -> List[List[float]]:
        """
        Builds dynamic transition probability matrix tailored to the asset's
        operational stressors (traffic volume, age, environmental exposure, material).
        """
        # Environmental and load acceleration factor
        traffic_ratio = asset.daily_traffic_volume_aadt / 40_000.0
        env_factor = asset.environmental_exposure_index
        seismic_factor = (asset.seismic_risk_zone - 1) * 0.08
        age_factor = (asset.age / asset.expected_lifespan_years) ** 1.3

        # Base annual probability of dropping from State i to State i+1
        # Adjusted by operational stressors
        stress_multiplier = 1.0 + (
            DEGRADATION_CONFIG["traffic_stress_factor"] * traffic_ratio +
            DEGRADATION_CONFIG["environmental_stress_factor"] * env_factor +
            seismic_factor +
            0.20 * age_factor
        )

        # Baseline step-down transition probabilities
        p12 = min(0.25, 0.05 * stress_multiplier)
        p23 = min(0.35, 0.08 * stress_multiplier)
        p34 = min(0.45, 0.12 * stress_multiplier)
        p45 = min(0.60, 0.18 * stress_multiplier)

        # 5x5 Transition matrix (absorbing state at 5 without maintenance)
        matrix = [
            [1.0 - p12, p12, 0.0, 0.0, 0.0],
            [0.0, 1.0 - p23, p23, 0.0, 0.0],
            [0.0, 0.0, 1.0 - p34, p34, 0.0],
            [0.0, 0.0, 0.0, 1.0 - p45, p45],
            [0.0, 0.0, 0.0, 0.0, 1.0]
        ]
        return matrix

    @classmethod
    def project_state_distribution(cls, asset: InfrastructureAsset, years: int = 5) -> List[List[float]]:
        """
        Calculates the state probability distribution over the given horizon: pi(t) = pi(0) * P^t
        """
        # Determine initial state vector
        shi = asset.structural_health_index
        if shi >= 90:
            init_vec = [1.0, 0.0, 0.0, 0.0, 0.0]
        elif shi >= 75:
            init_vec = [0.0, 1.0, 0.0, 0.0, 0.0]
        elif shi >= 55:
            init_vec = [0.0, 0.0, 1.0, 0.0, 0.0]
        elif shi >= 35:
            init_vec = [0.0, 0.0, 0.0, 1.0, 0.0]
        else:
            init_vec = [0.0, 0.0, 0.0, 0.0, 1.0]

        P = cls.get_base_transition_matrix(asset)
        history = [init_vec]

        curr_vec = init_vec
        for _ in range(years):
            next_vec = [0.0] * 5
            for j in range(5):
                next_vec[j] = sum(curr_vec[i] * P[i][j] for i in range(5))
            history.append(next_vec)
            curr_vec = next_vec

        return history


class PredictiveDegradationEngine:
    """
    Combines physics-based Weibull survival distributions with live sensor telemetry
    to assess current deterioration velocity and future failure probabilities.
    """

    def __init__(self):
        self.beta = DEGRADATION_CONFIG["weibull_shape_beta"]
        self.eta_base = DEGRADATION_CONFIG["characteristic_life_years"]

    def calculate_effective_characteristic_life(self, asset: InfrastructureAsset) -> float:
        """
        Computes asset-specific characteristic life (eta) adjusted for structural material,
        traffic volume, environmental weathering, and seismic ratings.
        """
        # Material durability multipliers
        material_durability = {
            "Prestressed Concrete": 1.10,
            "Structural Steel": 0.95,
            "Reinforced Concrete": 1.00,
            "Asphalt Composite": 0.70,
            "Cast Iron": 0.85
        }
        mat_factor = material_durability.get(asset.material_type, 1.0)

        # Operational stress factor
        traffic_norm = max(0.2, asset.daily_traffic_volume_aadt / 35_000.0)
        stress_factor = (
            1.0 +
            0.25 * math.log(1.0 + traffic_norm) +
            0.30 * asset.environmental_exposure_index +
            0.05 * asset.seismic_risk_zone
        )

        eta_effective = (self.eta_base * mat_factor) / stress_factor
        return max(15.0, eta_effective)

    def calculate_failure_probability(self, asset: InfrastructureAsset, horizon_years: float = 1.0) -> float:
        """
        Calculates functional failure probability over a given horizon using
        Weibull cumulative hazard with sensor telemetry anomaly scaling.
        """
        eta = self.calculate_effective_characteristic_life(asset)
        age = asset.age
        
        # Current condition attenuation: Low SHI accelerates the effective apparent age
        shi_penalty = max(0.0, (80.0 - asset.structural_health_index) / 10.0)
        effective_age = age + shi_penalty * 3.5

        # Weibull baseline cumulative hazard
        prob_base = 1.0 - math.exp(-((effective_age + horizon_years) / eta) ** self.beta + (effective_age / eta) ** self.beta)
        prob_base = max(0.001, min(0.95, prob_base))

        # Sensor telemetry adjustment
        anomaly_score = asset.telemetry.telemetry_anomaly_score
        corrosion_penalty = min(0.20, (asset.telemetry.corrosion_rate_mpy / 15.0) * 0.15)
        vibration_penalty = min(0.25, (asset.telemetry.vibration_rms_g / 2.0) * 0.20)

        total_telemetry_risk = anomaly_score * DEGRADATION_CONFIG["anomaly_risk_boost"] + corrosion_penalty + vibration_penalty
        
        # Combined failure probability
        adjusted_pf = 1.0 - (1.0 - prob_base) * (1.0 - total_telemetry_risk)
        return round(max(0.005, min(0.99, adjusted_pf)), 4)

    def estimate_annual_degradation_rate(self, asset: InfrastructureAsset) -> float:
        """
        Estimates the annual points of Structural Health Index (SHI) lost if no maintenance is performed.
        Typically between 0.8 and 8.5 points/year depending on stressors.
        """
        base_rate = 1.2
        traffic_boost = (asset.daily_traffic_volume_aadt / 25_000.0) * 0.85
        env_boost = asset.environmental_exposure_index * 1.40
        seismic_boost = (asset.seismic_risk_zone - 1) * 0.35
        anomaly_boost = asset.telemetry.telemetry_anomaly_score * 2.20

        # Accelerated degradation for assets already in poor condition
        if asset.structural_health_index < 50:
            condition_multiplier = 1.5
        elif asset.structural_health_index < 70:
            condition_multiplier = 1.2
        else:
            condition_multiplier = 1.0

        rate = (base_rate + traffic_boost + env_boost + seismic_boost + anomaly_boost) * condition_multiplier
        return round(min(12.0, max(0.5, rate)), 2)

    def simulate_future_trajectory(self, asset: InfrastructureAsset, years: int = 10) -> List[Dict[str, float]]:
        """
        Generates annual projection of SHI and Failure Probability under 'Do Nothing' scenario.
        """
        trajectory = []
        curr_shi = asset.structural_health_index
        annual_drop = self.estimate_annual_degradation_rate(asset)

        for yr in range(1, years + 1):
            curr_shi = max(5.0, curr_shi - annual_drop * (1.0 + 0.03 * yr))
            # Temporary asset snapshot for Pf evaluation
            temp_asset = asset.model_copy(update={
                "structural_health_index": curr_shi,
                "year_built": asset.year_built - yr
            })
            pf = self.calculate_failure_probability(temp_asset, horizon_years=1.0)
            trajectory.append({
                "year": yr,
                "projected_shi": round(curr_shi, 2),
                "failure_probability": round(pf, 4)
            })
        return trajectory
