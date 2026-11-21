"""
Metropolitan Infrastructure Dataset Generator & Seeder
=======================================================
Generates realistic civil infrastructure assets for a major metropolitan region.
Includes bridges, highway viaducts, tunnels, water pipelines, and power substations
with multi-sensor telemetry, structural degradation indicators, and CDC SVI profiles.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
from typing import List
from core.models import (
    InfrastructureAsset,
    AssetType,
    SensorTelemetry,
    SocietalProfile
)
from config import DATA_DIR


def generate_metropolitan_dataset() -> List[InfrastructureAsset]:
    """
    Creates 35 metropolitan assets spanning 5 distinct urban districts:
    - Downtown Metro Core
    - Riverfront Industrial Belt
    - Eastside High-Density Residential
    - North Transit & Innovation Corridor
    - South Harbor & Logistics Hub
    """
    raw_assets = [
        # Downtown Core Bridges & Viaducts
        {
            "id": "BR-101",
            "name": "Metropolitan Suspension River Bridge",
            "asset_type": AssetType.BRIDGE,
            "district": "Downtown Metro Core",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "year_built": 1968,
            "expected_lifespan_years": 80,
            "structural_health_index": 48.5,
            "daily_traffic_volume_aadt": 88000,
            "material_type": "Structural Steel",
            "environmental_exposure_index": 0.78,
            "seismic_risk_zone": 3,
            "connected_nodes": ["HW-201", "TU-401"],
            "telemetry": {
                "vibration_rms_g": 1.45,
                "strain_microstrain": 780.0,
                "corrosion_rate_mpy": 8.4,
                "acoustic_energy_db": 62.0,
                "telemetry_anomaly_score": 0.65
            },
            "societal": {
                "hospital_proximity_km": 1.2,
                "emergency_corridor_weight": 0.95,
                "social_vulnerability_index": 0.58,
                "served_population": 140000,
                "detour_length_km": 8.5,
                "transit_dependency_ratio": 0.62,
                "economic_throughput_daily_usd": 4500000.0,
                "environmental_spillover_risk": 0.70
            }
        },
        {
            "id": "HW-201",
            "name": "Central Expressway Elevated Viaduct",
            "asset_type": AssetType.HIGHWAY_CORRIDOR,
            "district": "Downtown Metro Core",
            "latitude": 40.7180,
            "longitude": -74.0010,
            "year_built": 1974,
            "expected_lifespan_years": 70,
            "structural_health_index": 54.0,
            "daily_traffic_volume_aadt": 115000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.65,
            "seismic_risk_zone": 2,
            "connected_nodes": ["BR-101", "HW-202", "ES-501"],
            "telemetry": {
                "vibration_rms_g": 1.10,
                "strain_microstrain": 620.0,
                "corrosion_rate_mpy": 5.8,
                "acoustic_energy_db": 48.0,
                "telemetry_anomaly_score": 0.40
            },
            "societal": {
                "hospital_proximity_km": 0.8,
                "emergency_corridor_weight": 0.90,
                "social_vulnerability_index": 0.52,
                "served_population": 185000,
                "detour_length_km": 6.2,
                "transit_dependency_ratio": 0.55,
                "economic_throughput_daily_usd": 6800000.0,
                "environmental_spillover_risk": 0.45
            }
        },
        {
            "id": "TU-401",
            "name": "Midtown Sub-River Transit Tunnel",
            "asset_type": AssetType.TUNNEL,
            "district": "Downtown Metro Core",
            "latitude": 40.7250,
            "longitude": -74.0090,
            "year_built": 1956,
            "expected_lifespan_years": 100,
            "structural_health_index": 38.2,
            "daily_traffic_volume_aadt": 65000,
            "material_type": "Cast Iron",
            "environmental_exposure_index": 0.88,
            "seismic_risk_zone": 3,
            "connected_nodes": ["BR-101", "WP-301"],
            "telemetry": {
                "vibration_rms_g": 1.72,
                "strain_microstrain": 910.0,
                "corrosion_rate_mpy": 11.2,
                "acoustic_energy_db": 74.0,
                "telemetry_anomaly_score": 0.82
            },
            "societal": {
                "hospital_proximity_km": 1.5,
                "emergency_corridor_weight": 0.85,
                "social_vulnerability_index": 0.64,
                "served_population": 120000,
                "detour_length_km": 11.4,
                "transit_dependency_ratio": 0.78,
                "economic_throughput_daily_usd": 5200000.0,
                "environmental_spillover_risk": 0.88
            }
        },
        {
            "id": "WP-301",
            "name": "Central High-Pressure Water Aqueduct Trunk",
            "asset_type": AssetType.WATER_PIPELINE,
            "district": "Downtown Metro Core",
            "latitude": 40.7160,
            "longitude": -74.0040,
            "year_built": 1962,
            "expected_lifespan_years": 75,
            "structural_health_index": 32.5,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Prestressed Concrete",
            "environmental_exposure_index": 0.70,
            "seismic_risk_zone": 3,
            "connected_nodes": ["TU-401", "ES-501"],
            "telemetry": {
                "vibration_rms_g": 0.60,
                "strain_microstrain": 450.0,
                "corrosion_rate_mpy": 13.5,
                "acoustic_energy_db": 81.0,
                "telemetry_anomaly_score": 0.88
            },
            "societal": {
                "hospital_proximity_km": 0.5,
                "emergency_corridor_weight": 0.98,
                "social_vulnerability_index": 0.72,
                "served_population": 260000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.60,
                "economic_throughput_daily_usd": 3800000.0,
                "environmental_spillover_risk": 0.92
            }
        },
        {
            "id": "ES-501",
            "name": "Downtown Civic Grid Substation 115kV",
            "asset_type": AssetType.ELECTRICAL_SUBSTATION,
            "district": "Downtown Metro Core",
            "latitude": 40.7210,
            "longitude": -74.0030,
            "year_built": 1982,
            "expected_lifespan_years": 60,
            "structural_health_index": 68.0,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Structural Steel",
            "environmental_exposure_index": 0.50,
            "seismic_risk_zone": 2,
            "connected_nodes": ["HW-201", "WP-301"],
            "telemetry": {
                "vibration_rms_g": 0.45,
                "strain_microstrain": 280.0,
                "corrosion_rate_mpy": 3.2,
                "acoustic_energy_db": 35.0,
                "telemetry_anomaly_score": 0.22
            },
            "societal": {
                "hospital_proximity_km": 0.6,
                "emergency_corridor_weight": 0.95,
                "social_vulnerability_index": 0.50,
                "served_population": 190000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.50,
                "economic_throughput_daily_usd": 7500000.0,
                "environmental_spillover_risk": 0.60
            }
        },

        # Eastside High-Density Residential (High SVI, Equity Critical)
        {
            "id": "BR-102",
            "name": "East River Avenue Pedestrian & Transit Bridge",
            "asset_type": AssetType.BRIDGE,
            "district": "Eastside Residential",
            "latitude": 40.7310,
            "longitude": -73.9820,
            "year_built": 1971,
            "expected_lifespan_years": 70,
            "structural_health_index": 41.0,
            "daily_traffic_volume_aadt": 42000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.82,
            "seismic_risk_zone": 2,
            "connected_nodes": ["HW-203", "CU-601"],
            "telemetry": {
                "vibration_rms_g": 1.38,
                "strain_microstrain": 720.0,
                "corrosion_rate_mpy": 9.1,
                "acoustic_energy_db": 58.0,
                "telemetry_anomaly_score": 0.70
            },
            "societal": {
                "hospital_proximity_km": 2.1,
                "emergency_corridor_weight": 0.80,
                "social_vulnerability_index": 0.88,
                "served_population": 115000,
                "detour_length_km": 7.8,
                "transit_dependency_ratio": 0.84,
                "economic_throughput_daily_usd": 1800000.0,
                "environmental_spillover_risk": 0.55
            }
        },
        {
            "id": "HW-202",
            "name": "Grand Boulevard East Arterial",
            "asset_type": AssetType.HIGHWAY_CORRIDOR,
            "district": "Eastside Residential",
            "latitude": 40.7280,
            "longitude": -73.9850,
            "year_built": 1985,
            "expected_lifespan_years": 50,
            "structural_health_index": 72.5,
            "daily_traffic_volume_aadt": 58000,
            "material_type": "Asphalt Composite",
            "environmental_exposure_index": 0.55,
            "seismic_risk_zone": 2,
            "connected_nodes": ["HW-201", "BR-102", "WP-302"],
            "telemetry": {
                "vibration_rms_g": 0.85,
                "strain_microstrain": 410.0,
                "corrosion_rate_mpy": 2.8,
                "acoustic_energy_db": 32.0,
                "telemetry_anomaly_score": 0.20
            },
            "societal": {
                "hospital_proximity_km": 1.8,
                "emergency_corridor_weight": 0.75,
                "social_vulnerability_index": 0.82,
                "served_population": 98000,
                "detour_length_km": 4.5,
                "transit_dependency_ratio": 0.79,
                "economic_throughput_daily_usd": 2100000.0,
                "environmental_spillover_risk": 0.35
            }
        },
        {
            "id": "CU-601",
            "name": "Eastside Creek Stormwater Drainage Culvert",
            "asset_type": AssetType.CULVERT_DRAINAGE,
            "district": "Eastside Residential",
            "latitude": 40.7340,
            "longitude": -73.9790,
            "year_built": 1965,
            "expected_lifespan_years": 60,
            "structural_health_index": 28.0,
            "daily_traffic_volume_aadt": 18000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.90,
            "seismic_risk_zone": 2,
            "connected_nodes": ["BR-102"],
            "telemetry": {
                "vibration_rms_g": 0.95,
                "strain_microstrain": 550.0,
                "corrosion_rate_mpy": 12.0,
                "acoustic_energy_db": 68.0,
                "telemetry_anomaly_score": 0.85
            },
            "societal": {
                "hospital_proximity_km": 3.2,
                "emergency_corridor_weight": 0.65,
                "social_vulnerability_index": 0.91,
                "served_population": 85000,
                "detour_length_km": 5.2,
                "transit_dependency_ratio": 0.82,
                "economic_throughput_daily_usd": 950000.0,
                "environmental_spillover_risk": 0.95
            }
        },
        {
            "id": "WP-302",
            "name": "East District Domestic Water Feeder Line",
            "asset_type": AssetType.WATER_PIPELINE,
            "district": "Eastside Residential",
            "latitude": 40.7290,
            "longitude": -73.9810,
            "year_built": 1978,
            "expected_lifespan_years": 70,
            "structural_health_index": 62.0,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Prestressed Concrete",
            "environmental_exposure_index": 0.60,
            "seismic_risk_zone": 2,
            "connected_nodes": ["HW-202", "ES-502"],
            "telemetry": {
                "vibration_rms_g": 0.35,
                "strain_microstrain": 310.0,
                "corrosion_rate_mpy": 4.5,
                "acoustic_energy_db": 40.0,
                "telemetry_anomaly_score": 0.28
            },
            "societal": {
                "hospital_proximity_km": 2.0,
                "emergency_corridor_weight": 0.70,
                "social_vulnerability_index": 0.85,
                "served_population": 130000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.80,
                "economic_throughput_daily_usd": 1200000.0,
                "environmental_spillover_risk": 0.65
            }
        },
        {
            "id": "ES-502",
            "name": "Eastside Community Power Substation",
            "asset_type": AssetType.ELECTRICAL_SUBSTATION,
            "district": "Eastside Residential",
            "latitude": 40.7260,
            "longitude": -73.9870,
            "year_built": 1989,
            "expected_lifespan_years": 60,
            "structural_health_index": 79.0,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Structural Steel",
            "environmental_exposure_index": 0.45,
            "seismic_risk_zone": 2,
            "connected_nodes": ["WP-302"],
            "telemetry": {
                "vibration_rms_g": 0.30,
                "strain_microstrain": 220.0,
                "corrosion_rate_mpy": 2.1,
                "acoustic_energy_db": 25.0,
                "telemetry_anomaly_score": 0.15
            },
            "societal": {
                "hospital_proximity_km": 2.4,
                "emergency_corridor_weight": 0.65,
                "social_vulnerability_index": 0.84,
                "served_population": 110000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.76,
                "economic_throughput_daily_usd": 2400000.0,
                "environmental_spillover_risk": 0.40
            }
        },

        # Riverfront Industrial Belt (Hazmat, Heavy Loads)
        {
            "id": "BR-103",
            "name": "Ironclad Industrial Freight Rail & Road Bridge",
            "asset_type": AssetType.BRIDGE,
            "district": "Riverfront Industrial Belt",
            "latitude": 40.7010,
            "longitude": -74.0200,
            "year_built": 1952,
            "expected_lifespan_years": 85,
            "structural_health_index": 33.8,
            "daily_traffic_volume_aadt": 34000,
            "material_type": "Structural Steel",
            "environmental_exposure_index": 0.92,
            "seismic_risk_zone": 3,
            "connected_nodes": ["HW-204", "WP-303"],
            "telemetry": {
                "vibration_rms_g": 1.88,
                "strain_microstrain": 950.0,
                "corrosion_rate_mpy": 14.8,
                "acoustic_energy_db": 79.0,
                "telemetry_anomaly_score": 0.90
            },
            "societal": {
                "hospital_proximity_km": 4.5,
                "emergency_corridor_weight": 0.60,
                "social_vulnerability_index": 0.60,
                "served_population": 45000,
                "detour_length_km": 14.2,
                "transit_dependency_ratio": 0.35,
                "economic_throughput_daily_usd": 8500000.0,
                "environmental_spillover_risk": 0.96
            }
        },
        {
            "id": "HW-204",
            "name": "Riverfront Heavy Freight Bypass Corridor",
            "asset_type": AssetType.HIGHWAY_CORRIDOR,
            "district": "Riverfront Industrial Belt",
            "latitude": 40.6980,
            "longitude": -74.0150,
            "year_built": 1978,
            "expected_lifespan_years": 60,
            "structural_health_index": 52.0,
            "daily_traffic_volume_aadt": 48000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.80,
            "seismic_risk_zone": 2,
            "connected_nodes": ["BR-103", "CU-602", "ES-503"],
            "telemetry": {
                "vibration_rms_g": 1.25,
                "strain_microstrain": 690.0,
                "corrosion_rate_mpy": 7.4,
                "acoustic_energy_db": 55.0,
                "telemetry_anomaly_score": 0.48
            },
            "societal": {
                "hospital_proximity_km": 4.8,
                "emergency_corridor_weight": 0.50,
                "social_vulnerability_index": 0.55,
                "served_population": 38000,
                "detour_length_km": 9.8,
                "transit_dependency_ratio": 0.30,
                "economic_throughput_daily_usd": 7200000.0,
                "environmental_spillover_risk": 0.85
            }
        },
        {
            "id": "WP-303",
            "name": "Chemical Basin Industrial Wastewater Syphon",
            "asset_type": AssetType.WATER_PIPELINE,
            "district": "Riverfront Industrial Belt",
            "latitude": 40.7040,
            "longitude": -74.0180,
            "year_built": 1969,
            "expected_lifespan_years": 65,
            "structural_health_index": 39.0,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Cast Iron",
            "environmental_exposure_index": 0.89,
            "seismic_risk_zone": 3,
            "connected_nodes": ["BR-103"],
            "telemetry": {
                "vibration_rms_g": 0.75,
                "strain_microstrain": 580.0,
                "corrosion_rate_mpy": 12.6,
                "acoustic_energy_db": 66.0,
                "telemetry_anomaly_score": 0.75
            },
            "societal": {
                "hospital_proximity_km": 5.2,
                "emergency_corridor_weight": 0.40,
                "social_vulnerability_index": 0.58,
                "served_population": 52000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.25,
                "economic_throughput_daily_usd": 4100000.0,
                "environmental_spillover_risk": 0.98
            }
        },
        {
            "id": "CU-602",
            "name": "Basin Flood Gate & Tidal Drainage Canal",
            "asset_type": AssetType.CULVERT_DRAINAGE,
            "district": "Riverfront Industrial Belt",
            "latitude": 40.6950,
            "longitude": -74.0220,
            "year_built": 1980,
            "expected_lifespan_years": 60,
            "structural_health_index": 57.5,
            "daily_traffic_volume_aadt": 12000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.85,
            "seismic_risk_zone": 2,
            "connected_nodes": ["HW-204"],
            "telemetry": {
                "vibration_rms_g": 0.65,
                "strain_microstrain": 420.0,
                "corrosion_rate_mpy": 6.8,
                "acoustic_energy_db": 42.0,
                "telemetry_anomaly_score": 0.35
            },
            "societal": {
                "hospital_proximity_km": 5.5,
                "emergency_corridor_weight": 0.45,
                "social_vulnerability_index": 0.62,
                "served_population": 42000,
                "detour_length_km": 6.0,
                "transit_dependency_ratio": 0.32,
                "economic_throughput_daily_usd": 2800000.0,
                "environmental_spillover_risk": 0.94
            }
        },
        {
            "id": "ES-503",
            "name": "Riverfront Grid Heavy Switching Yard",
            "asset_type": AssetType.ELECTRICAL_SUBSTATION,
            "district": "Riverfront Industrial Belt",
            "latitude": 40.6990,
            "longitude": -74.0120,
            "year_built": 1984,
            "expected_lifespan_years": 60,
            "structural_health_index": 64.0,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Structural Steel",
            "environmental_exposure_index": 0.70,
            "seismic_risk_zone": 2,
            "connected_nodes": ["HW-204"],
            "telemetry": {
                "vibration_rms_g": 0.50,
                "strain_microstrain": 340.0,
                "corrosion_rate_mpy": 4.8,
                "acoustic_energy_db": 38.0,
                "telemetry_anomaly_score": 0.30
            },
            "societal": {
                "hospital_proximity_km": 4.2,
                "emergency_corridor_weight": 0.55,
                "social_vulnerability_index": 0.52,
                "served_population": 65000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.28,
                "economic_throughput_daily_usd": 6500000.0,
                "environmental_spillover_risk": 0.72
            }
        },

        # North Transit & Innovation Corridor
        {
            "id": "BR-104",
            "name": "University Campus Viaduct & Skyway",
            "asset_type": AssetType.BRIDGE,
            "district": "North Transit Corridor",
            "latitude": 40.7550,
            "longitude": -73.9850,
            "year_built": 1995,
            "expected_lifespan_years": 75,
            "structural_health_index": 82.0,
            "daily_traffic_volume_aadt": 52000,
            "material_type": "Prestressed Concrete",
            "environmental_exposure_index": 0.45,
            "seismic_risk_zone": 1,
            "connected_nodes": ["HW-205", "TU-402"],
            "telemetry": {
                "vibration_rms_g": 0.42,
                "strain_microstrain": 260.0,
                "corrosion_rate_mpy": 1.8,
                "acoustic_energy_db": 22.0,
                "telemetry_anomaly_score": 0.12
            },
            "societal": {
                "hospital_proximity_km": 1.1,
                "emergency_corridor_weight": 0.88,
                "social_vulnerability_index": 0.32,
                "served_population": 125000,
                "detour_length_km": 3.8,
                "transit_dependency_ratio": 0.72,
                "economic_throughput_daily_usd": 3900000.0,
                "environmental_spillover_risk": 0.25
            }
        },
        {
            "id": "HW-205",
            "name": "North Metro High-Speed Commuter Highway",
            "asset_type": AssetType.HIGHWAY_CORRIDOR,
            "district": "North Transit Corridor",
            "latitude": 40.7620,
            "longitude": -73.9810,
            "year_built": 1998,
            "expected_lifespan_years": 60,
            "structural_health_index": 76.5,
            "daily_traffic_volume_aadt": 74000,
            "material_type": "Asphalt Composite",
            "environmental_exposure_index": 0.50,
            "seismic_risk_zone": 1,
            "connected_nodes": ["BR-104", "ES-504"],
            "telemetry": {
                "vibration_rms_g": 0.60,
                "strain_microstrain": 380.0,
                "corrosion_rate_mpy": 2.2,
                "acoustic_energy_db": 28.0,
                "telemetry_anomaly_score": 0.18
            },
            "societal": {
                "hospital_proximity_km": 1.4,
                "emergency_corridor_weight": 0.82,
                "social_vulnerability_index": 0.35,
                "served_population": 145000,
                "detour_length_km": 4.2,
                "transit_dependency_ratio": 0.65,
                "economic_throughput_daily_usd": 5100000.0,
                "environmental_spillover_risk": 0.30
            }
        },
        {
            "id": "TU-402",
            "name": "North Innovation Rapid Transit Tunnel",
            "asset_type": AssetType.TUNNEL,
            "district": "North Transit Corridor",
            "latitude": 40.7580,
            "longitude": -73.9880,
            "year_built": 2004,
            "expected_lifespan_years": 100,
            "structural_health_index": 89.0,
            "daily_traffic_volume_aadt": 45000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.35,
            "seismic_risk_zone": 1,
            "connected_nodes": ["BR-104", "WP-304"],
            "telemetry": {
                "vibration_rms_g": 0.38,
                "strain_microstrain": 210.0,
                "corrosion_rate_mpy": 1.2,
                "acoustic_energy_db": 18.0,
                "telemetry_anomaly_score": 0.08
            },
            "societal": {
                "hospital_proximity_km": 0.9,
                "emergency_corridor_weight": 0.92,
                "social_vulnerability_index": 0.28,
                "served_population": 160000,
                "detour_length_km": 5.5,
                "transit_dependency_ratio": 0.88,
                "economic_throughput_daily_usd": 6200000.0,
                "environmental_spillover_risk": 0.20
            }
        },
        {
            "id": "WP-304",
            "name": "North Reservoir Feed Line & Booster Station",
            "asset_type": AssetType.WATER_PIPELINE,
            "district": "North Transit Corridor",
            "latitude": 40.7640,
            "longitude": -73.9920,
            "year_built": 1991,
            "expected_lifespan_years": 70,
            "structural_health_index": 71.0,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Prestressed Concrete",
            "environmental_exposure_index": 0.40,
            "seismic_risk_zone": 1,
            "connected_nodes": ["TU-402"],
            "telemetry": {
                "vibration_rms_g": 0.28,
                "strain_microstrain": 240.0,
                "corrosion_rate_mpy": 2.5,
                "acoustic_energy_db": 26.0,
                "telemetry_anomaly_score": 0.14
            },
            "societal": {
                "hospital_proximity_km": 1.6,
                "emergency_corridor_weight": 0.78,
                "social_vulnerability_index": 0.30,
                "served_population": 115000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.58,
                "economic_throughput_daily_usd": 2200000.0,
                "environmental_spillover_risk": 0.35
            }
        },
        {
            "id": "ES-504",
            "name": "Innovation Tech Park Renewable Substation",
            "asset_type": AssetType.ELECTRICAL_SUBSTATION,
            "district": "North Transit Corridor",
            "latitude": 40.7680,
            "longitude": -73.9840,
            "year_built": 2012,
            "expected_lifespan_years": 60,
            "structural_health_index": 93.5,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Structural Steel",
            "environmental_exposure_index": 0.25,
            "seismic_risk_zone": 1,
            "connected_nodes": ["HW-205"],
            "telemetry": {
                "vibration_rms_g": 0.18,
                "strain_microstrain": 150.0,
                "corrosion_rate_mpy": 0.9,
                "acoustic_energy_db": 12.0,
                "telemetry_anomaly_score": 0.04
            },
            "societal": {
                "hospital_proximity_km": 1.2,
                "emergency_corridor_weight": 0.85,
                "social_vulnerability_index": 0.25,
                "served_population": 95000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.60,
                "economic_throughput_daily_usd": 8900000.0,
                "environmental_spillover_risk": 0.15
            }
        },

        # South Harbor & Logistics Hub (Port, Coastal Exposure, Storm Surge Risk)
        {
            "id": "BR-105",
            "name": "Oceanic Gateway Container Causeway Bridge",
            "asset_type": AssetType.BRIDGE,
            "district": "South Harbor Logistics",
            "latitude": 40.6710,
            "longitude": -74.0350,
            "year_built": 1964,
            "expected_lifespan_years": 75,
            "structural_health_index": 35.0,
            "daily_traffic_volume_aadt": 62000,
            "material_type": "Structural Steel",
            "environmental_exposure_index": 0.95,
            "seismic_risk_zone": 4,
            "connected_nodes": ["HW-206", "CU-603"],
            "telemetry": {
                "vibration_rms_g": 1.65,
                "strain_microstrain": 880.0,
                "corrosion_rate_mpy": 13.8,
                "acoustic_energy_db": 72.0,
                "telemetry_anomaly_score": 0.86
            },
            "societal": {
                "hospital_proximity_km": 6.8,
                "emergency_corridor_weight": 0.70,
                "social_vulnerability_index": 0.78,
                "served_population": 72000,
                "detour_length_km": 16.5,
                "transit_dependency_ratio": 0.45,
                "economic_throughput_daily_usd": 12500000.0,
                "environmental_spillover_risk": 0.95
            }
        },
        {
            "id": "HW-206",
            "name": "Harbor Intermodal Freeway Feeder",
            "asset_type": AssetType.HIGHWAY_CORRIDOR,
            "district": "South Harbor Logistics",
            "latitude": 40.6750,
            "longitude": -74.0300,
            "year_built": 1976,
            "expected_lifespan_years": 60,
            "structural_health_index": 46.0,
            "daily_traffic_volume_aadt": 78000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.88,
            "seismic_risk_zone": 3,
            "connected_nodes": ["BR-105", "WP-305"],
            "telemetry": {
                "vibration_rms_g": 1.35,
                "strain_microstrain": 710.0,
                "corrosion_rate_mpy": 8.9,
                "acoustic_energy_db": 60.0,
                "telemetry_anomaly_score": 0.55
            },
            "societal": {
                "hospital_proximity_km": 6.2,
                "emergency_corridor_weight": 0.65,
                "social_vulnerability_index": 0.74,
                "served_population": 68000,
                "detour_length_km": 11.2,
                "transit_dependency_ratio": 0.40,
                "economic_throughput_daily_usd": 10200000.0,
                "environmental_spillover_risk": 0.80
            }
        },
        {
            "id": "CU-603",
            "name": "South Harbor Tidal Inundation Culvert",
            "asset_type": AssetType.CULVERT_DRAINAGE,
            "district": "South Harbor Logistics",
            "latitude": 40.6680,
            "longitude": -74.0380,
            "year_built": 1970,
            "expected_lifespan_years": 60,
            "structural_health_index": 31.0,
            "daily_traffic_volume_aadt": 22000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.98,
            "seismic_risk_zone": 4,
            "connected_nodes": ["BR-105"],
            "telemetry": {
                "vibration_rms_g": 1.15,
                "strain_microstrain": 650.0,
                "corrosion_rate_mpy": 14.5,
                "acoustic_energy_db": 75.0,
                "telemetry_anomaly_score": 0.89
            },
            "societal": {
                "hospital_proximity_km": 7.5,
                "emergency_corridor_weight": 0.55,
                "social_vulnerability_index": 0.82,
                "served_population": 55000,
                "detour_length_km": 8.0,
                "transit_dependency_ratio": 0.48,
                "economic_throughput_daily_usd": 3200000.0,
                "environmental_spillover_risk": 0.98
            }
        },
        {
            "id": "WP-305",
            "name": "Port Cryogenic & Fire Hydrant Pressure Main",
            "asset_type": AssetType.WATER_PIPELINE,
            "district": "South Harbor Logistics",
            "latitude": 40.6780,
            "longitude": -74.0250,
            "year_built": 1983,
            "expected_lifespan_years": 65,
            "structural_health_index": 58.0,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Cast Iron",
            "environmental_exposure_index": 0.85,
            "seismic_risk_zone": 3,
            "connected_nodes": ["HW-206", "ES-505"],
            "telemetry": {
                "vibration_rms_g": 0.55,
                "strain_microstrain": 410.0,
                "corrosion_rate_mpy": 7.2,
                "acoustic_energy_db": 46.0,
                "telemetry_anomaly_score": 0.42
            },
            "societal": {
                "hospital_proximity_km": 6.0,
                "emergency_corridor_weight": 0.80,
                "social_vulnerability_index": 0.70,
                "served_population": 48000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.35,
                "economic_throughput_daily_usd": 4800000.0,
                "environmental_spillover_risk": 0.88
            }
        },
        {
            "id": "ES-505",
            "name": "South Port Maritime Terminal Grid Substation",
            "asset_type": AssetType.ELECTRICAL_SUBSTATION,
            "district": "South Harbor Logistics",
            "latitude": 40.6800,
            "longitude": -74.0220,
            "year_built": 1990,
            "expected_lifespan_years": 60,
            "structural_health_index": 67.5,
            "daily_traffic_volume_aadt": 0,
            "material_type": "Structural Steel",
            "environmental_exposure_index": 0.80,
            "seismic_risk_zone": 3,
            "connected_nodes": ["WP-305"],
            "telemetry": {
                "vibration_rms_g": 0.48,
                "strain_microstrain": 310.0,
                "corrosion_rate_mpy": 5.4,
                "acoustic_energy_db": 34.0,
                "telemetry_anomaly_score": 0.28
            },
            "societal": {
                "hospital_proximity_km": 5.8,
                "emergency_corridor_weight": 0.75,
                "social_vulnerability_index": 0.68,
                "served_population": 62000,
                "detour_length_km": 0.0,
                "transit_dependency_ratio": 0.38,
                "economic_throughput_daily_usd": 9100000.0,
                "environmental_spillover_risk": 0.65
            }
        },

        # Additional Key Regional Connecting Links & Tunnels
        {
            "id": "BR-106",
            "name": "Southwest Bypass Arch River Crossing",
            "asset_type": AssetType.BRIDGE,
            "district": "Riverfront Industrial Belt",
            "latitude": 40.6850,
            "longitude": -74.0280,
            "year_built": 1960,
            "expected_lifespan_years": 80,
            "structural_health_index": 44.0,
            "daily_traffic_volume_aadt": 51000,
            "material_type": "Structural Steel",
            "environmental_exposure_index": 0.85,
            "seismic_risk_zone": 3,
            "connected_nodes": ["HW-204", "HW-206"],
            "telemetry": {
                "vibration_rms_g": 1.48,
                "strain_microstrain": 810.0,
                "corrosion_rate_mpy": 9.8,
                "acoustic_energy_db": 64.0,
                "telemetry_anomaly_score": 0.62
            },
            "societal": {
                "hospital_proximity_km": 5.0,
                "emergency_corridor_weight": 0.70,
                "social_vulnerability_index": 0.65,
                "served_population": 78000,
                "detour_length_km": 12.0,
                "transit_dependency_ratio": 0.42,
                "economic_throughput_daily_usd": 6100000.0,
                "environmental_spillover_risk": 0.75
            }
        },
        {
            "id": "HW-207",
            "name": "Northeast Beltway Interchange",
            "asset_type": AssetType.HIGHWAY_CORRIDOR,
            "district": "North Transit Corridor",
            "latitude": 40.7720,
            "longitude": -73.9750,
            "year_built": 2001,
            "expected_lifespan_years": 60,
            "structural_health_index": 85.0,
            "daily_traffic_volume_aadt": 82000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.40,
            "seismic_risk_zone": 1,
            "connected_nodes": ["HW-205"],
            "telemetry": {
                "vibration_rms_g": 0.40,
                "strain_microstrain": 230.0,
                "corrosion_rate_mpy": 1.5,
                "acoustic_energy_db": 20.0,
                "telemetry_anomaly_score": 0.10
            },
            "societal": {
                "hospital_proximity_km": 2.2,
                "emergency_corridor_weight": 0.75,
                "social_vulnerability_index": 0.30,
                "served_population": 110000,
                "detour_length_km": 3.5,
                "transit_dependency_ratio": 0.52,
                "economic_throughput_daily_usd": 4700000.0,
                "environmental_spillover_risk": 0.22
            }
        },
        {
            "id": "TU-403",
            "name": "Harbor Freight Commercial Underpass",
            "asset_type": AssetType.TUNNEL,
            "district": "South Harbor Logistics",
            "latitude": 40.6650,
            "longitude": -74.0410,
            "year_built": 1972,
            "expected_lifespan_years": 80,
            "structural_health_index": 42.0,
            "daily_traffic_volume_aadt": 38000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.92,
            "seismic_risk_zone": 4,
            "connected_nodes": ["BR-105"],
            "telemetry": {
                "vibration_rms_g": 1.50,
                "strain_microstrain": 840.0,
                "corrosion_rate_mpy": 10.5,
                "acoustic_energy_db": 67.0,
                "telemetry_anomaly_score": 0.72
            },
            "societal": {
                "hospital_proximity_km": 7.2,
                "emergency_corridor_weight": 0.60,
                "social_vulnerability_index": 0.80,
                "served_population": 46000,
                "detour_length_km": 14.0,
                "transit_dependency_ratio": 0.38,
                "economic_throughput_daily_usd": 8900000.0,
                "environmental_spillover_risk": 0.85
            }
        },
        {
            "id": "CU-604",
            "name": "North Valley Storm Drainage Canal",
            "asset_type": AssetType.CULVERT_DRAINAGE,
            "district": "North Transit Corridor",
            "latitude": 40.7690,
            "longitude": -73.9960,
            "year_built": 1996,
            "expected_lifespan_years": 60,
            "structural_health_index": 77.0,
            "daily_traffic_volume_aadt": 14000,
            "material_type": "Reinforced Concrete",
            "environmental_exposure_index": 0.45,
            "seismic_risk_zone": 1,
            "connected_nodes": ["WP-304"],
            "telemetry": {
                "vibration_rms_g": 0.35,
                "strain_microstrain": 220.0,
                "corrosion_rate_mpy": 2.0,
                "acoustic_energy_db": 19.0,
                "telemetry_anomaly_score": 0.12
            },
            "societal": {
                "hospital_proximity_km": 2.5,
                "emergency_corridor_weight": 0.50,
                "social_vulnerability_index": 0.32,
                "served_population": 62000,
                "detour_length_km": 2.8,
                "transit_dependency_ratio": 0.45,
                "economic_throughput_daily_usd": 750000.0,
                "environmental_spillover_risk": 0.40
            }
        },
        {
            "id": "BR-107",
            "name": "Eastside Inter-Community Overpass",
            "asset_type": AssetType.BRIDGE,
            "district": "Eastside Residential",
            "latitude": 40.7380,
            "longitude": -73.9720,
            "year_built": 1975,
            "expected_lifespan_years": 70,
            "structural_health_index": 49.0,
            "daily_traffic_volume_aadt": 36000,
            "material_type": "Prestressed Concrete",
            "environmental_exposure_index": 0.72,
            "seismic_risk_zone": 2,
            "connected_nodes": ["HW-202"],
            "telemetry": {
                "vibration_rms_g": 1.05,
                "strain_microstrain": 610.0,
                "corrosion_rate_mpy": 6.2,
                "acoustic_energy_db": 49.0,
                "telemetry_anomaly_score": 0.45
            },
            "societal": {
                "hospital_proximity_km": 1.9,
                "emergency_corridor_weight": 0.82,
                "social_vulnerability_index": 0.86,
                "served_population": 92000,
                "detour_length_km": 5.8,
                "transit_dependency_ratio": 0.81,
                "economic_throughput_daily_usd": 1500000.0,
                "environmental_spillover_risk": 0.50
            }
        }
    ]

    assets = [InfrastructureAsset(**item) for item in raw_assets]

    # Save to JSON
    json_path = DATA_DIR / "metropolitan_network.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([a.model_dump() for a in assets], f, indent=2)

    return assets


def load_metropolitan_dataset() -> List[InfrastructureAsset]:
    """
    Loads saved assets from JSON or generates them if not found.
    """
    json_path = DATA_DIR / "metropolitan_network.json"
    if not json_path.exists():
        return generate_metropolitan_dataset()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [InfrastructureAsset(**item) for item in data]


if __name__ == "__main__":
    generated = generate_metropolitan_dataset()
    print(f"Successfully generated {len(generated)} metropolitan infrastructure assets in {DATA_DIR}!")
