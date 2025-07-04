from fastapi import APIRouter, Depends, Query, UploadFile
from sqlalchemy.orm import Session

from src.database.config import get_db
from src.repositories.destination_repository import *
from src.schemas.geocode import *
from src.services.destination import DestinationService


router = APIRouter(prefix="/trips/{trip_id}/destinations", tags=["Destinations"])


def get_destination_service():
    return DestinationService()


@router.get(
    "/",
    response_model=List[DestinationResponse],
    status_code=200
)
async def list_trip_destinations(
    trip_id: int,
    destination_service: DestinationService = Depends(get_destination_service),
    db: Session = Depends(get_db) 
):
    destinations = await destination_service.get_destinations_for_trip(trip_id, db)
    if not destinations:
        raise HTTPException(
            status_code=404, detail=f"There are not destinations for this trip"
        )
    return destinations


@router.get(
    "/sorted",
    response_model=List[DestinationResponse],
    status_code=200
)
async def get_sorted_destinations(
    trip_id: int,
    user_lat: float = Query(..., description="User's current latitude for sorting destinations"),
    user_lon: float = Query(..., description="User's current longitude for sorting destinations"),
    destination_service: DestinationService = Depends(get_destination_service),
    db: Session = Depends(get_db)
):
    sorted_destinations = await destination_service.get_sorted_destinations(
        trip_id=trip_id,
        user_lat=user_lat,
        user_lon=user_lon,
        db=db
    )
    if not sorted_destinations:
        return []
    return sorted_destinations


@router.get(
    "/optimal_route",
    response_model=List[DestinationResponse],
    status_code=200
)
async def get_optimal_trip_route(
    trip_id: int,
    user_lat: float = Query(..., description="Starting latitude of the user"),
    user_lon: float = Query(..., description="Starting longitude of the user"),
    destination_service: DestinationService = Depends(get_destination_service), 
    db: Session = Depends(get_db) 
):
    """
    Calculates and returns an optimal route for visiting destinations in a trip,
    starting from the user's initial coordinates.
    """
    return await destination_service.get_optimal_route_destinations(
        trip_id=trip_id,
        user_lat=user_lat,
        user_lon=user_lon,
        db=db
    )


@router.get(
    "/{destination_id}",
    response_model=DestinationResponse,
    status_code=200
)
async def get_destination(
    trip_id: int,
    destination_id: int,
    destination_service: DestinationService = Depends(get_destination_service),
    db: Session = Depends(get_db) 
):
    destination = await destination_service.get_destination_by_id(trip_id, destination_id, db)
    print(destination)
    if not destination:
        raise HTTPException(
            status_code=404, detail=f"Destination with id {destination_id} not found"
        )
    return destination


@router.post(
    "/",
    response_model=DestinationResponse,
    status_code=201
)
async def create_destination(
    trip_id: int,
    destination: DestinationCreateRequest,
    db: Session = Depends(get_db),
    destination_service: DestinationService = Depends(get_destination_service)
):
    return await destination_service.process_single_destination(
        trip_id=trip_id,
        db=db,
        location=destination.location,
    )

@router.post(
    "/batch",
    response_model=BatchGeocodeResponse,
    status_code=201
)
async def create_batch_destinations_route(
    trip_id: int,
    destinations: BatchGeocodeRequest,
    db: Session = Depends(get_db),
    destination_service: DestinationService = Depends(get_destination_service)
):
    result = await destination_service.create_batch_destinations(
        db=db,
        trip_id=trip_id,
        locations=destinations.locations,
    )
    return result


@router.post(
    "/manual",
    response_model=DestinationResponse,
    status_code=201
)
async def create_manual_destination(
    trip_id: int,
    destination: ManualDestinationCreateRequest,
    db: Session = Depends(get_db),
    destination_service: DestinationService = Depends(get_destination_service)
):
    return await destination_service.create_manual_destinations(
        db=db,
        trip_id=trip_id,
        **destination.model_dump()
    )


@router.post(
    "/import",
    response_model=BatchGeocodeResponse,
    status_code=201
)
async def import_destinations(
    file: UploadFile,
    trip_id: int,
    db: Session = Depends(get_db),
    destination_service: DestinationService = Depends(get_destination_service)
):
    return await destination_service.import_destinations_from_file(
        trip_id=trip_id,
        db=db,
        file_path=file.filename,
    )


@router.put(
    "/{destination_id}/mark",
    response_model=DestinationResponse,
    status_code=200
)
async def mark_destinations_as_visited(
    trip_id: int,
    destination_id: int,
    destination_service: DestinationService = Depends(get_destination_service),
    db: Session = Depends(get_db)
):
    updated_destination = await destination_service.mark_destinations_as_visited(
        trip_id, destination_id, db
    )
    if not updated_destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    return updated_destination



@router.delete(
    "/{destination_id}",
    status_code=200
)
async def delete_destination(
    destination_id: int,
    destination_service: DestinationService = Depends(get_destination_service),
    db: Session = Depends(get_db)
):
    success = await destination_service.delete_destination(destination_id, db)
    return {"message": "Destination deleted successfully"}

