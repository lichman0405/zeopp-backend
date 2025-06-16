# The module defines the data models for the framework information API.
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0


from pydantic import BaseModel
from typing import List

class FrameworkDetail(BaseModel):
    """
    Represents information about a single framework identified in the structure.
    """
    framework_id: int
    dimensionality: int

class FrameworkInfoResponse(BaseModel):
    """
    Defines the response structure for the framework info API.
    """
    number_of_frameworks: int
    frameworks: List[FrameworkDetail]
    cached: bool