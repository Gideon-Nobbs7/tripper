from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from src.database.config import get_db
from src.repositories.destination_repository import *
from src.schemas.geocode import *
from src.services.geocode import GeocodeClass
from src.services.destination import DestinationService
from src.utils.utils import sort_location_by_distance


router = APIRouter(prefix="/api/v1/destination", tags=["Destinations"])


def get_destination_service():
    return DestinationService()


@router.post(
    "/{trip_id}/new",
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
    "/{trip_id}/all",
    response_model=List[DestinationResponse],
    status_code=200
)
async def get_all_destinations(
    trip_id: int,
    db: Session = Depends(get_db) 
):
    result = await all_destinations(trip_id, db)

    if not result:
        raise HTTPException(
            status_code=404, detail=f"There are not destinations for this trip"
        )
    
    return result


@router.get(
    "/{destination_id}",
    response_model=DestinationResponse,
    status_code=200
)
async def get_destination(
    destination_id: int,
    db: Session = Depends(get_db) 
):
    result = await retrieve_destination(destination_id, db)

    if not result:
        raise HTTPException(
            status_code=404, detail=f"Destination with id {destination_id} not found"
        )
    
    return result


@router.delete(
    "/{destination_id}",
    status_code=200
)
async def delete_destination(
    destination_id: int,
    db: Session = Depends(get_db)
):
    result = await remove_destination(destination_id, db)
    return {"message":"Destination deleted successfully"}


@router.post(
    "/{trip_id}/batch",
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
    return await destination_service.create_batch_destinations(
        db=db,
        trip_id=trip_id,
        locations=destinations.locations,
        user_lat=coordinates.latitude,
        user_lon=coordinates.longitude
    )
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
    "/{trip_id}/new/manual",
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
    "/{trip_id}/import",
    response_model=BatchGeocodeResponse,
    status_code=201
)
async def import_destinations(
    trip_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    destination_service: DestinationService = Depends(get_destination_service)
):
    return await destination_service.import_destinations_from_file(
        trip_id=trip_id,
        db=db,
        file_path=file.filename
    )
