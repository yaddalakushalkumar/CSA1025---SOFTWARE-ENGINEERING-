"""
FastAPI Main Application Entrypoint
====================================
Serves RESTful API routes and static interactive dashboard.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import router
from config import WEB_DIR

app = FastAPI(
    title="InfraRisk-AI: Infrastructure Risk Assessment & Maintenance Optimization",
    description=(
        "An AI-Driven Predictive Infrastructure Risk Assessment and Societal Impact-Based "
        "Maintenance Optimization Framework. Couples Weibull survival curves, Markov chain "
        "deterioration, CDC Social Vulnerability Index (SVI), and Multi-Objective Evolutionary "
        "Algorithms to prioritize civil infrastructure interventions."
    ),
    version="1.0.0"
)

# CORS middleware for open accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(router, prefix="/api")

# Mount Static Files (Web UI Dashboard)
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_dashboard():
        return FileResponse(str(WEB_DIR / "index.html"))
