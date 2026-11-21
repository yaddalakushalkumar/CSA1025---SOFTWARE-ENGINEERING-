"""
InfraRisk-AI Configuration Settings
===================================
Centralized configurations for degradation modeling, societal impact quantification,
multi-objective maintenance optimization, and web server parameters.
"""

import os
from pathlib import Path

# Ensure loopback traffic bypasses sandbox proxy
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
WEB_DIR = BASE_DIR / "web"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'infrarisk.db'}"

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
DEBUG = True

# Societal Impact Weights (default normalized weights)
DEFAULT_SOCIETAL_WEIGHTS = {
    "emergency_accessibility": 0.35,  # Healthcare & emergency service continuity
    "economic_disruption": 0.25,      # Commuter & freight delays, detour costs
    "equity_vulnerability": 0.25,     # Social Vulnerability Index (SVI) & transit dependency
    "environmental_hazard": 0.15      # Emissions, flood spillover & structural collapse hazard
}

# Maintenance Optimization Parameters
DEFAULT_OPTIMIZATION_CONFIG = {
    "annual_budget": 15_000_000.0,       # Default budget ($15M)
    "max_crew_days": 1800,               # Maximum available labor crew-days per year
    "min_acceptable_shi": 40.0,          # Minimum structural health index threshold
    "planning_horizon_years": 5,         # Multi-year planning horizon
    "discount_rate": 0.04,               # 4% annual economic discount rate
    "genetic_algorithm": {
        "population_size": 80,
        "generations": 60,
        "crossover_rate": 0.85,
        "mutation_rate": 0.12,
        "elite_fraction": 0.10
    }
}

# Deterioration Model Hyperparameters
DEGRADATION_CONFIG = {
    "weibull_shape_beta": 2.2,          # Accelerated wear-out shape factor (> 1)
    "characteristic_life_years": 60.0,  # Baseline characteristic life
    "traffic_stress_factor": 0.30,      # Sensitivity to AADT load
    "environmental_stress_factor": 0.25,# Sensitivity to climate & seismic stressors
    "anomaly_risk_boost": 0.45          # Telemetry anomaly boost multiplier
}

# Standard Maintenance Action Cost & Improvement Lookup (Unit costs in USD)
MAINTENANCE_ACTIONS = {
    "DO_NOTHING": {
        "name": "Do Nothing (Routine Monitoring)",
        "base_cost": 0.0,
        "crew_days": 0,
        "shi_restoration": 0.0,
        "pf_reduction_factor": 1.0,
        "downtime_days": 0
    },
    "ROUTINE_PREVENTIVE": {
        "name": "Routine Preventive Maintenance",
        "base_cost": 75_000.0,
        "crew_days": 10,
        "shi_restoration": 8.0,
        "pf_reduction_factor": 0.70,
        "downtime_days": 2
    },
    "MINOR_REHABILITATION": {
        "name": "Minor Structural Rehabilitation",
        "base_cost": 320_000.0,
        "crew_days": 35,
        "shi_restoration": 22.0,
        "pf_reduction_factor": 0.40,
        "downtime_days": 12
    },
    "MAJOR_RETROFIT": {
        "name": "Major Retrofit & Seismic Strengthening",
        "base_cost": 1_250_000.0,
        "crew_days": 90,
        "shi_restoration": 45.0,
        "pf_reduction_factor": 0.18,
        "downtime_days": 45
    },
    "COMPLETE_RECONSTRUCTION": {
        "name": "Complete Reconstruction / Replacement",
        "base_cost": 4_800_000.0,
        "crew_days": 240,
        "shi_restoration": 95.0,
        "pf_reduction_factor": 0.02,
        "downtime_days": 120
    }
}
