# Surface Area Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import List, Optional


class SurfaceAreaRequest(BaseModel):
    chan_radius: float = Field(..., description="Radius used to determine accessibility of void space")
    probe_radius: float = Field(..., description="Radius used in Monte Carlo sampling")
    samples: int = Field(..., description="Number of Monte Carlo samples per atom")
    output_filename: Optional[str] = Field("result.sa", description="Optional output file name")
    ha: Optional[bool] = Field(True, description="Whether to use high accuracy mode (-ha)")


class SurfaceAreaResponse(BaseModel):
    asa_unitcell: float
    asa_volume: float
    asa_mass: float
    nasa_unitcell: float
    nasa_volume: float
    nasa_mass: float
    # Optional extension fields exposed by newer Zeo++ versions. Backward
    # compatible: older outputs leave these as None.
    number_of_channels: Optional[int] = None
    channel_surface_area_a2: Optional[List[float]] = None
    number_of_pockets: Optional[int] = None
    pocket_surface_area_a2: Optional[List[float]] = None
    cached: bool

