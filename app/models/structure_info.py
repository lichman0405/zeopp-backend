# Structure Info Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import Optional, List


class StructureInfoRequest(BaseModel):
    output_filename: Optional[str] = Field("result.strinfo", description="Optional output file name")

class FrameworkInfo(BaseModel):
    id: int = Field(..., description="Molecule ID")
    dimensionality: int = Field(..., description="Dimensionality of the framework")


class StructureInfoResponse(BaseModel):
    num_frameworks: int = Field(..., description="Number of molecule frameworks")
    frameworks: List[FrameworkInfo] = Field(..., description="List of frameworks and dimensionality")
    channels: int = Field(..., description="Number of channels identified")
    pockets: int = Field(..., description="Number of pockets identified")
    nodes_assigned: int = Field(..., description="Number of nodes assigned to pores")
    raw: str = Field(..., description="Raw .strinfo output text")
    cached: bool = Field(..., description="Whether the result came from cache")
