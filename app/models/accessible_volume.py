# Accessible Volume Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import Optional


class AccessibleVolumeRequest(BaseModel):
    chan_radius: float = Field(..., description="Probe radius used to determine accessible volume")
    probe_radius: float = Field(..., description="Radius used in Monte Carlo sampling")
    samples: int = Field(..., description="Number of Monte Carlo samples per unit cell")
    output_filename: Optional[str] = Field("result.vol", description="Optional output file name")
    ha: Optional[bool] = Field(True, description="Whether to use high accuracy mode (-ha)")


# Response Model
class AccessibleVolumeResponse(BaseModel):
    unitcell_volume: float
    density: float
    av: dict
    nav: dict
    cached: bool


