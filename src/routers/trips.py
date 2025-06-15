from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.config import get_db
from src.repositories.trip_repository import *
from src.schemas.trip import *


trips_route = APIRouter(prefix="/api/v1/trips", tags=["Trips"])


@trips_route.get(
    "/{trip_id}/",
    response_model=TripDetailResponse,
    status_code=200
)
async def retrive_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    trip = await trip_detail(trip_id, db)

    if not trip:
        raise HTTPException(
            status_code=404, detail=f"Trip with id {trip_id} not found"
        )
    return trip


@trips_route.get(
    "/",
    response_model=List[TripResponse],
    status_code=200
)
async def get_all_trips(
    db: Session = Depends(get_db)
):
    trips = await all_trips(db)

    if not trips:
        raise HTTPException(
            status_code=404, detail=f"There are no trips"
        )
    return trips


@trips_route.post(
    "/create", 
    response_model=TripResponse,
    status_code=201
)
async def create_new_trip(
    trip: TripCreateModel,
    db: Session = Depends(get_db)
):
    created_trip = await create_trip(trip, db)
    return created_trip


@trips_route.put(
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


@trips_route.delete(
    "/{trip_id}/delete",
    status_code=200
)
async def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    removed_trip = await remove_trip(trip_id, db)
    return {"message": "Deleted successfully"}