# Distance Grid Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel, Field
from typing import Optional
from typing import List

class DistanceGridRequest(BaseModel):
    mode: str = Field(..., description="Choose from 'gridG', 'gridGBohr', or 'gridBOV'")
    output_basename: Optional[str] = Field("result", description="Base name for output files")
    ha: Optional[bool] = Field(True, description="Whether to use high accuracy mode (-ha)")

class DistanceGridResponse(BaseModel):
    message: str
    output_files: List[str]
    cached: bool

