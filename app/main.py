# FastAPI Main Entrypoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all route modules
from app.api import (
    pore_diameter,
    surface_area,
    accessible_volume,
    probe_volume,
    channel_analysis,
    structure_info,
    pore_size_dist,
    ray_tracing,
    blocking_spheres,
    distance_grid,
    voronoi_network
)

app = FastAPI(
    title="Zeo++ Analysis API",
    description="A containerized FastAPI service for Zeo++ structure analysis",
    version="1.0.0"
)

# Optional: CORS for frontend or external service usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(pore_diameter.router)
app.include_router(surface_area.router)
app.include_router(accessible_volume.router)
app.include_router(probe_volume.router)
app.include_router(channel_analysis.router)
app.include_router(structure_info.router)
app.include_router(pore_size_dist.router)
app.include_router(ray_tracing.router)
app.include_router(blocking_spheres.router)
app.include_router(distance_grid.router)
app.include_router(voronoi_network.router)
