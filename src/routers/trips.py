from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.config import get_db
from src.dependencies.dependency import get_trip_service
from src.repositories.trip_repository import TripService
from src.schemas.trip import *


router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get(
    "/",
    response_model=List[TripResponse],
    status_code=200
)
async def list_trips(
    trip_service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db)
):
    trips = await trip_service.get_trips(db)

    if not trips:
        raise HTTPException(
            status_code=404, detail=f"There are no trips"
        )
    return trips


@router.get(
    "/{trip_id}",
    response_model=TripDetailResponse,
    status_code=200
)
async def retrive_trip(
    trip_id: int,
    trip_service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db)
):
    trip = await trip_service.trip_detail(trip_id, db)

    if not trip:
        raise HTTPException(
            status_code=404, detail=f"Trip with id {trip_id} not found"
        )
    return trip


@router.post(
    "/", 
    response_model=TripResponse,
    status_code=201
)
async def create_trip(
    trip: TripCreateModel,
    trip_service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db)
):
    created_trip = await trip_service.create_trip(trip, db)
    return created_trip


@router.put(
    "/{trip_id}",
    response_model=TripResponse,
    status_code=200
)
async def update_trip(
    trip_id: int,
    trip: TripUpdateRequest,
    trip_service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db)
):
    updated_trip = await trip_service.update_trip(trip_id, trip, db)
    if not updated_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return updated_trip


@router.delete(
    "/{trip_id}",
    status_code=200
)
async def delete_trip(
    trip_id: int,
    trip_service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db)
):
    success = await trip_service.delete_trip(trip_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Trip npt found")
    return {"message": "Deleted successfully"}


# @router.get(
#     "/{trip_id}/destinations",
#     response_model=List[DestinationResponse],
#     status_code=200
# )
# async def get_all_destinations(
#     trip_id: int,
#     db: Session = Depends(get_db),
#     destination_service: DestinationService = Depends(get_destination_service)
# ):
#     result = await destination_service.get_sorted_destination()

#     if not result:
#         raise HTTPException(
#             status_code=404, detail=f"There are not destinations for this trip"
#         )
    
#     return result