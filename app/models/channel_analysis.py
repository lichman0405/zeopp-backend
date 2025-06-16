# Channel Dimensionality Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel
class ChannelAnalysisResponse(BaseModel):
    """
    Defines the response structure for the channel analysis API.
    This now correctly reflects the parsed data instead of raw text.
    """
    dimension: int
    included_diameter: float
    free_diameter: float
    included_along_free: float
    cached: bool


