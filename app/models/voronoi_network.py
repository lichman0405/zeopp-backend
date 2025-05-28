# Voronoi Network Export Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import Optional


class VoronoiNetworkRequest(BaseModel):
    use_radii: Optional[bool] = Field(True, description="Use atomic radii (-r) or not (-nor)")
    output_filename: Optional[str] = Field("result.nt2", description="Optional output file name")

class VoronoiNetworkResponse(BaseModel):
    node_count: Optional[int] = Field(None, description="Number of Voronoi nodes")
    edge_count: Optional[int] = Field(None, description="Number of Voronoi edges")
    raw: str = Field(..., description="Raw content of .nt2 file")
    cached: bool = Field(..., description="Whether the result came from cache")


