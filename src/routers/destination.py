from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.repositories.destination_repository import *
from src.schemas.geocode import *
from src.services.geocode import GeocodeClass
from src.database.config import get_db


router = APIRouter(prefix="/api/v1/destination", tags=["Destinations"])


@router.post(
    "/{trip_id}/new",
    response_model=DestinationResponse,
    status_code=201
)
async def create_destination(
    trip_id: int,
    destination: DestinationCreateRequest,
    db: Session = Depends(get_db)
):
    response = GeocodeClass().get_coordinates_for_address(
        destination.location
    )
    result = await add_destination(
        db=db,
        trip_id=trip_id,
        location=destination.location,
        longitude=response["longitude"],
        lattitude=response["lattitude"],
        distance_from_user_km=response["distance_from_user_km"]
    )

    return result