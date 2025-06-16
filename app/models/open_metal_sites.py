# The module defines the data models for the Open Metal Sites API.
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0

from pydantic import BaseModel

class OpenMetalSitesResponse(BaseModel):
    """
    Defines the response structure for the Open Metal Sites (OMS) API.
    """
    open_metal_sites_count: int
    cached: bool