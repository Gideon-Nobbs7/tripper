from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.repositories.trip_repository import *
from src.schemas.trip import *
from src.database.config import get_db


router = APIRouter(prefix="/api/v1/trips", tags=["Trips"])


@router.post(
    "/create", 
    response_model=TripResponse,
    status_code=201
)
async def create_trip(
    trip: TripCreateModel,
    db: Session = Depends(get_db)
):
    created_trip = await create_trip(trip, db)
    return created_trip


@router.put(
    "/{trip_id}/update",
    response_model=TripResponse,
    status_code=200
)
async def update_trip(
    trip_id: int,
    trip: TripUpdateRequest,
    db: Session = Depends(get_db)
):
    updated_trip = await alter_trip(trip_id, trip, db)
    return updated_trip


@router.delete(
    "/{trip_id}/delete",
    status_code=200
)
async def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    removed_trip = await remove_trip(trip_id, db)
    return {"message": "Deleted successfully"}