import asyncio
import time
from typing import List

import aiohttp
import uvicorn
from fastapi import FastAPI, Query, APIRouter

from src.schema.schema import BatchGeocodeModel, CoordinateModel, GeocodeModel
from src.services.geocode import GeocodeClass


app = APIRouter()


@app.get(
    "/sync-geocode",
    summary="Convert a location to its longitude and latitude",
    response_model=CoordinateModel,
    status_code=200,
)
def geocode_location(
    location: str = Query(..., description="E.g. 'Amalitech, Kumasi, Ghana'")
):
    response = GeocodeClass().get_coordinates_for_address(location)
    return response


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


@app.post("/async-geocode-thread")
async def geocode_multiple_location_thread(
       request: BatchGeocodeModel 
):  
    start_time = time.time()
    response = await GeocodeClass().geocode_with_thread_pool(request.locations)
    end_time = start_time - time.time()
    print(end_time)
    return response

if __name__ == "__main__":
    uvicorn.run(app=app, port=8000, reload=True)