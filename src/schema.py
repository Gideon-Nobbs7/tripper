from typing import List

from pydantic import BaseModel, Field


class GeocodeModel(BaseModel):
    location: str = Field("Enter a location to geocode", examples=["Amalitech, Kumasi, Ghana"])


class BatchGeocodeModel(BaseModel):
    locations: List[str]


class CoordinateModel(BaseModel):
    location: str
    longitude: float
    latitude: float