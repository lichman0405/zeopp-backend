# Middleware for FastAPI Application
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-31
# Version: 0.3.1

"""
Custom middleware for request processing, timing, and security.
"""

import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import logger


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request processing time and add request ID.
    Also collects metrics for Prometheus monitoring.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Import here to avoid circular imports
        from app.api.metrics import metrics_store
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Record start time and increment active requests
        start_time = time.time()
        metrics_store.active_requests += 1
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time_ms}ms"
            
            # Record metrics (skip /metrics endpoint to avoid recursion)
            if not request.url.path.startswith("/metrics"):
                metrics_store.record_request(
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    latency=process_time
                )
            
            # Log request info (skip health checks and metrics to reduce noise)
            if not request.url.path.startswith(("/health", "/metrics")):
                logger.info(
                    f"[{request_id}] {request.method} {request.url.path} "
                    f"- {response.status_code} - {process_time_ms}ms"
                )
            
            return response
        finally:
            # Decrement active requests counter
            metrics_store.active_requests -= 1


# Allowed file extensions for structure files
ALLOWED_EXTENSIONS = {
    ".cif",
    ".cssr", 
    ".v1",
    ".arc",
    ".xyz",
    ".pdb",
    ".cuc"
}


def validate_structure_file(filename: Optional[str]) -> bool:
    """
    Validate that the uploaded file has an allowed extension.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    # Get file extension (lowercase)
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    return ext in ALLOWED_EXTENSIONS


def get_allowed_extensions_str() -> str:
    """Get a formatted string of allowed extensions."""
    return ", ".join(sorted(ALLOWED_EXTENSIONS))
