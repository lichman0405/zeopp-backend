# The module defines the data models for the framework information API.
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0


from pydantic import BaseModel
from typing import List, Optional

class FrameworkDetail(BaseModel):
    """
    Represents information about a single framework identified in the structure.
    """
    framework_id: int
    dimensionality: int

class FrameworkInfoResponse(BaseModel):
    """
    Defines the new, more detailed response structure for the framework info API.
    """
    filename: str
    formula: str
    segments: int
    number_of_frameworks: int
    number_of_molecules: int
    frameworks: List[FrameworkDetail]
    cached: bool