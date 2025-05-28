# Blocking Spheres Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import Optional


class BlockingSpheresRequest(BaseModel):
    probe_radius: float = Field(..., description="Probe radius used to determine blocking spheres")
    samples: int = Field(..., description="Number of MC samples")
    output_filename: Optional[str] = Field("result.block", description="Optional output file name")
    ha: Optional[bool] = Field(True, description="Whether to use high accuracy mode (-ha)")


class BlockingSpheresResponse(BaseModel):
    channels: int = Field(..., description="Number of channels identified")
    pockets: int = Field(..., description="Number of pockets identified")
    nodes_assigned: int = Field(..., description="Number of nodes assigned to pores")
    raw: str = Field(..., description="Raw .block output")
    cached: bool = Field(..., description="Whether the result was served from cache")
