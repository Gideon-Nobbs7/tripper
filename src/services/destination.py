from sqlalchemy.orm import Session
from typing import Any, List

from src.exceptions.exceptions import DatabaseError
from src.repositories.destination_repository import add_destination
from src.schemas.geocode import BatchGeocodeResponse
from src.services.geocode import GeocodeClass
from src.utils.utils import sort_location_by_distance, haversine_distance


class DestinationService:
    def __init__(self):
        self.geocode_service = GeocodeClass()

    
    async def process_single_destination(
        self,
        trip_id: int,
        db: Session,
        location: str,
        user_lat: float,
        user_lon: float
    ):
        response = self.geocode_service.get_coordinates_for_address(
            location=location,
            user_lat=user_lat,
            user_lon=user_lon
        )

        try:
            result = await add_destination(
                db=db,
                trip_id=trip_id,
                location=location,
                longitude=response["longitude"],
                lattitude=response["lattitude"],
                distance_from_user_km=response["distance_from_user_km"]
            )
        except Exception as e:
            raise DatabaseError(f"Failed to add destination {location}: {str(e)}")
        
        return result


    async def process_batch_destinations(
        self,
        trip_id: int,
        db: Session,
        geocode_responses: Any
    ) -> BatchGeocodeResponse:
        results = []

        for response in geocode_responses.results:
            try:
                result = await add_destination(
                    db=db,
                    trip_id=trip_id,
                    location=response.location if hasattr(response, 'location') else response["location"],
                    longitude=response.longitude if hasattr(response, 'longitude') else response["longitude"],
                    lattitude=response.lattitude if hasattr(response, 'lattitude') else response["lattitude"],
                    distance_from_user_km=response.distance_from_user_km if hasattr(response, 'distance_from_user_km') else response["distance_from_user_km"]
                )
                results.append(result)
            except Exception as e:
                raise DatabaseError(f"Failed to add destination")
        
        sorted_results = sort_location_by_distance(results)

        return BatchGeocodeResponse(
            results=sorted_results,
            failed=geocode_responses.failed
        )

    
    def _extract_destination_data(self, response):
        return {
            "location": getattr(response, "location", None) or response["location"],
            "longitude": getattr(response, "longitude", None) or response["longitude"],
            "lattitude": getattr(response, "lattitude", None) or response["lattitude"],
            "distance_from_user_km": getattr(response, "distance_from_user_km", None) or response["distance_from_user_km"],
        }
    

    async def create_batch_destinations(
        self, 
        db: Session,
        trip_id: int,
        locations: List[str]
    ):
        geocode_responses = await self.geocode_service.geocode_with_thread_pool(locations)
        return await self.process_batch_destinations(trip_id, db, geocode_responses)
    

    async def create_manual_destinations(
        self,
        db: Session,
        trip_id: int,
        location: str,
        longitude: float,
        lattitude: float,
    ):
        distance_from_user_km = haversine_distance(5.5545, -0.1902, longitude, lattitude)

        try:
            result = await add_destination(
                db=db,
                trip_id=trip_id,
                location=location,
                longitude=longitude,
                lattitude=lattitude,
                distance_from_user_km=distance_from_user_km
            )
        except Exception as e:
            raise DatabaseError(f"Failed to add destination for {location}: {str(e)}")
        
        return result
    

    async def import_destinations_from_file(
        self,
        trip_id: int,
        db: Session,
        file_path: str
    ):
        geocode_responses = await self.geocode_service.import_data_from_csv(file_path)
        return await self.process_batch_destinations(trip_id, db, geocode_responses)