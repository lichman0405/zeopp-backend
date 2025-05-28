# Ray Tracing Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import Optional


class RayTracingRequest(BaseModel):
    chan_radius: float = Field(..., description="Accessibility determination radius")
    probe_radius: float = Field(..., description="Ray-sampling probe radius")
    samples: int = Field(..., description="Number of rays")
    output_filename: Optional[str] = Field("result.ray", description="Optional output file name")
    ha: Optional[bool] = Field(True, description="Whether to use high accuracy mode (-ha)")


class RayTracingResponse(BaseModel):
    content: str
    cached: bool

