from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class GeocodeRequest(BaseModel):
    location: str = Field(..., description="Location to geocode", examples=["Amalitech, Kumasi, Ghana"])


class CoordinateResponse(BaseModel):
    location: str
    longitude: float
    lattitude: float
    distance_from_user_km: float


class DestinationResponse(BaseModel):
    id: int
    location: str
    longitude: float
    lattitude: float
    distance_from_user_km: float
    trip_id: int
    created_at: datetime
    

class DestinationCreateRequest(BaseModel):
    location: str = Field(..., description="A location to add to your trip")
    lattitude: float
    longitude: float
    # trip_id: int = Field(..., description="A trip this destination belongs to")


class BatchGeocodeRequest(BaseModel):
    locations: List[str] = Field(..., description="A list of locations to geocode")


class BatchGeocodeResponse(BaseModel):
    results: List
    failed: Optional[List[str]] = []


class ManualDestinationCreateRequest(BaseModel):
    location: str
    longitude: float
    lattitude: float


class Location(BaseModel):
    lattitude: float
    longitude: float