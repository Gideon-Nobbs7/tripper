import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class GeocodeRequest(BaseModel):
    location: str = Field(..., description="Location to geocode", examples=["Amalitech, Kumasi, Ghana"])


class CoordinateResponse(BaseModel):
    location: str
    longitude: float
    latitude: float
    distance_from_user_km: float


class BatchGeocodeRequest(BaseModel):
    locations: List[GeocodeRequest] = Field(..., description="A list of locations to geocode")


class BatchGeocodeResponse(BaseModel):
    results: List[CoordinateResponse]
    failed: Optional[List[str]]


class DestinationCreateRequest(BaseModel):
    destination: str = Field(..., description="A destination to add to your trip")
    trip_id: int = Field(..., description="A trip this destination belongs to")


class DestinationResponse(BaseModel):
    id: int
    location: str
    longitude: float
    latitude: float
    distance_from_user_km: float
    trip_id: int
    created_at: datetime