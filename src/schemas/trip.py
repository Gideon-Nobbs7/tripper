from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TripCreateModel(BaseModel):
    name: str = Field(..., description="A name for your trip", min_length=1, max_length=100)


class TripUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Updated trip name", min_length=1, max_length=100)


class TripResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    destinations: Optional[int] = 0


class TripDetailResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    destinations: List


class TripListResponse(BaseModel):
    trips: List[TripDetailResponse]
    total: int
    page: int
    per_page: int