# FastAPI Main Entrypoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13
# Updated: 2025-12-22 - Added v1 API versioning and health checks
# Updated: 2025-12-31 - Added cache management, security enhancements, rate limiting

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import configuration and middleware
from app.core.config import settings
from app.core.middleware import RequestTimingMiddleware

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
    health,
    cache,
    metrics
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.app_name,
    description="A containerized FastAPI service for Zeo++ structure analysis with versioned endpoints",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add request timing middleware
app.add_middleware(RequestTimingMiddleware)

# CORS configuration from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register health check and system routers first
app.include_router(health.router)
app.include_router(cache.router)
app.include_router(metrics.router)

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


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    from app.utils.logger import logger
    logger.rule("Zeo++ API Service Starting", style="green")
    logger.info(f"Version: {app.version}")
    logger.info(f"Cache enabled: {settings.enable_cache}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    logger.info(f"Rate limit: {settings.rate_limit_requests} requests/minute")
    logger.info(f"Max upload size: {settings.max_upload_size_mb}MB")
    logger.rule("Ready to accept requests", style="green")
