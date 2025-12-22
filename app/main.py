# FastAPI Main Entrypoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13
# Updated: 2025-12-22 - Added v1 API versioning and health checks

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all route modules
from app.api import (
    pore_diameter,
    surface_area,
    accessible_volume,
    probe_volume,
    channel_analysis,
    framework_info,
    pore_size_dist,
    blocking_spheres,
    open_metal_sites,
    health
)

app = FastAPI(
    title="Zeo++ Analysis API",
    description="A containerized FastAPI service for Zeo++ structure analysis with versioned endpoints",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Optional: CORS for frontend or external service usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register health check and system routers first
app.include_router(health.router)

# Register analysis API routers (v1)
app.include_router(pore_diameter.router)
app.include_router(surface_area.router)
app.include_router(accessible_volume.router)
app.include_router(probe_volume.router)
app.include_router(channel_analysis.router)
app.include_router(framework_info.router)
app.include_router(pore_size_dist.router)
app.include_router(blocking_spheres.router)
app.include_router(open_metal_sites.router)
