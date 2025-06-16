# Channel Dimensionality Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import Optional

class ChannelAnalysisRequest(BaseModel):
    probe_radius: float = Field(..., description="Radius of spherical probe")
    output_filename: Optional[str] = Field("result.chan", description="Optional output file name")
    ha: Optional[bool] = Field(True, description="Whether to use high accuracy mode (-ha)")

class ChannelAnalysisResponse(BaseModel):
    dimension: int
    included_diameter: float
    free_diameter: float
    included_along_free: float
    raw_text: str = Field(..., description="Original .chan output")
    cached: bool



