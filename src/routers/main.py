import asyncio
import time
from typing import List

import aiohttp
import uvicorn
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.config import get_db
from src.routers.helper_func import add_destination, new_trip
from src.schemas.schema import BatchGeocodeModel, CoordinateModel, TripModel
from src.services.geocode import GeocodeClass
from src.utils.utils import sort_location_by_distance

app = APIRouter(prefix="/api/v1")


@app.post(
    "/create", 
    tags=["Trip"], 
    response_model=TripModel,
    status_code=201
)
async def create_trip(
    trip: TripModel,
    db: Session = Depends(get_db)
):
    created_trip = await new_trip(trip, db)
    return created_trip


@app.get(
    "/{trip_id}/geocode",
    summary="Convert a location to its longitude and latitude",
    response_model=CoordinateModel,
    status_code=200,
)
async def geocode_location(
    trip_id: int,
    location: str = Query(..., description="E.g. 'Amalitech, Kumasi, Ghana'"),
    db: Session = Depends(get_db)
):
    response = GeocodeClass().get_coordinates_for_address(location)
    print("Response: ", response)
    result = await add_destination(
        db=db,
        trip_id=trip_id,
        location=location,
        longitude=response["longitude"],
        latitude=response["latitude"],
        distance_from_user_km=response["distance_from_user_km"]
    )
    return result


@app.post(
    "/batch-geocode",
    summary="Convert a list of locations to their coordinates", 
    status_code=200,
    response_model=List[CoordinateModel]
)
def batch_coordinates(request: BatchGeocodeModel):
    results = []
    start_time = time.time()
    
    for address in request.locations:
        result = GeocodeClass().get_coordinates_for_address(address)
        results.append(result)
        end_time = start_time - time.time()
        print(end_time)
        time.sleep(2)

    return results


@app.post("/async-geocode")
async def geocode_multiple_location_aiohttp(
       locations: BatchGeocodeModel 
):
    semaphore = asyncio.Semaphore(value=1)

    async def bounded_fetch(session, location):
        async with semaphore:
            return await GeocodeClass().get_coordinates_async_aiohttp(location, session)
    
    async with aiohttp.ClientSession() as session:
        tasks = [bounded_fetch(session, location) for location in locations.locations]
        return await asyncio.gather(*tasks)


@app.post("/multiplegeocode", response_model=List[CoordinateModel])
async def geocode_multiple_location_thread(
       request: BatchGeocodeModel 
):  
    start_time = time.time()
    response = await GeocodeClass().geocode_with_thread_pool(request.locations)
    end_time = start_time - time.time()
    print(end_time)
    data = sort_location_by_distance(response)
    return data

if __name__ == "__main__":
    uvicorn.run(app=app, port=8000, reload=True)