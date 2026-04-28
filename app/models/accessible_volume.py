# Accessible Volume Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import List, Optional


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
    # Optional extension fields exposed by newer Zeo++ versions. Backward
    # compatible: older outputs leave these as None.
    number_of_channels: Optional[int] = None
    channel_volume_a3: Optional[List[float]] = None
    number_of_pockets: Optional[int] = None
    pocket_volume_a3: Optional[List[float]] = None
    cached: bool


