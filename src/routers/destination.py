from fastapi import APIRouter, Depends, File, UploadFile, Form, Query
from sqlalchemy.orm import Session

from src.database.config import get_db
from src.repositories.destination_repository import *
from src.schemas.geocode import *
from src.services.geocode import GeocodeClass
from src.services.destination import DestinationService
from src.utils.utils import sort_location_by_distance


router = APIRouter(prefix="/trips/{trip_id}/destinations", tags=["Destinations"])


def get_destination_service():
    return DestinationService()


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
        user_lat=destination.latitude,
        user_lon=destination.longitude
    )


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


@router.post(
    "/batch",
    response_model=BatchGeocodeResponse,
    status_code=201
)
async def create_batch_destinations_route(
    trip_id: int,
    destinations: BatchGeocodeRequest,
    coordinates: Coordinates,
    db: Session = Depends(get_db),
    destination_service: DestinationService = Depends(get_destination_service)
):
    result = await destination_service.create_batch_destinations(
        db=db,
        trip_id=trip_id,
        locations=destinations.locations,
        user_lat=coordinates.latitude,
        user_lon=coordinates.longitude
    )
    print(result)
    return result
    # responses = await GeocodeClass().geocode_with_thread_pool(
    #     destinations.locations
    # )
    # results = []

    # for response in responses.results:
    #     print(f"Response type: {type(response)}")
    #     print(f"Response content: {response}")
    #     result = await add_destination(
    #         db=db,
    #         trip_id=trip_id,
    #         location=response.location if hasattr(response, 'location') else response["location"],
    #         longitude=response.longitude if hasattr(response, 'longitude') else response["longitude"],
    #         latitude=response.latitude if hasattr(response, 'latitude') else response["latitude"],
    #         distance_from_user_km=response.distance_from_user_km if hasattr(response, 'distance_from_user_km') else response["distance_from_user_km"]
    #     )
    #     results.append(result)
    
    # if responses.failed:
    #     print(responses.failed)
    
    # final_response = sort_location_by_distance(results)
    # print("Results: ", results)

    # return BatchGeocodeResponse(
    #     results=final_response,
    #     failed=responses.failed
    # )


@router.post(
    "/manual/",
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
    # coordinates: Coordinates,
    user_lat: float = Query(...),
    user_lon: float = Query(...),
    db: Session = Depends(get_db),
    destination_service: DestinationService = Depends(get_destination_service)
):
    return await destination_service.import_destinations_from_file(
        trip_id=trip_id,
        db=db,
        user_lat=user_lat,
        user_lon=user_lon,
        file_path=file.filename,
    )


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
    "/{destination_id}",
    response_model=DestinationResponse,
    status_code=200
)
async def get_destination(
    destination_id: int,
    destination_service: DestinationService = Depends(get_destination_service),
    db: Session = Depends(get_db) 
):
    destination = await destination_service.get_destination_by_id(destination_id, db)
    if not destination:
        raise HTTPException(
            status_code=404, detail=f"Destination with id {destination_id} not found"
        )
    return destination


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

