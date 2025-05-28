# Pore Size Distribution Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import Optional


class PoreSizeDistRequest(BaseModel):
    chan_radius: float = Field(..., description="Radius used to determine accessibility")
    probe_radius: float = Field(..., description="Probe radius used in histogram")
    samples: int = Field(..., description="Number of MC samples per unit cell")
    output_filename: Optional[str] = Field("result.psd_histo", description="Optional output file name")
    ha: Optional[bool] = Field(True, description="Whether to use high accuracy mode (-ha)")


class PoreSizeDistResponse(BaseModel):
    content: str
    cached: bool

