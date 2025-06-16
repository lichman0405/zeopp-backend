# Pore Diameter Request & Response Models
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from pydantic import BaseModel
from typing import Optional

class PoreDiameterRequest(BaseModel):
    ha: Optional[bool] = True        # Whether or not to use high accuracy '-ha' mode
    output_filename: Optional[str] = None  # Optional: output filename


class PoreDiameterResponse(BaseModel):
    included_diameter: float
    free_diameter: float
    included_along_free: float
    cached: bool
