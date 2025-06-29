from sqlalchemy.orm import Session
from typing import Any, List

from src.exceptions.exceptions import DatabaseError
from src.repositories.destination_repository import DestinationRepository
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
        response = self.geocode_service.get_coordinates_for_destination(
            location=location,
            user_lat=user_lat,
            user_lon=user_lon
        )

        try:
            result = await DestinationRepository().add_destination(
                db=db,
                trip_id=trip_id,
                location=location,
                longitude=response["longitude"],
                latitude=response["latitude"],
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
                result = await DestinationRepository().add_destination(
                    db=db,
                    trip_id=trip_id,
                    location=response.location if hasattr(response, 'location') else response["location"],
                    longitude=response.longitude if hasattr(response, 'longitude') else response["longitude"],
                    latitude=response.latitude if hasattr(response, 'latitude') else response["latitude"],
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
            "latitude": getattr(response, "latitude", None) or response["latitude"],
            "distance_from_user_km": getattr(response, "distance_from_user_km", None) or response["distance_from_user_km"],
        }
    

    async def create_batch_destinations(
        self, 
        db: Session,
        trip_id: int,
        locations: List[str],
        user_lat: float,
        user_lon: float
    ):
        geocode_responses = await self.geocode_service.geocode_with_thread_pool(locations, user_lat, user_lon)
        return await self.process_batch_destinations(trip_id, db, geocode_responses)
    

    async def create_manual_destinations(
        self,
        db: Session,
        trip_id: int,
        location: str,
        longitude: float,
        latitude: float,
    ):
        distance_from_user_km = haversine_distance(5.5545, -0.1902, longitude, latitude)

        try:
            result = await DestinationRepository().add_destination(
                db=db,
                trip_id=trip_id,
                location=location,
                longitude=longitude,
                latitude=latitude,
                distance_from_user_km=distance_from_user_km
            )
        except Exception as e:
            raise DatabaseError(f"Failed to add destination for {location}: {str(e)}")
        return result
    

    async def import_destinations_from_file(
        self,
        trip_id: int,
        user_lat: float,
        user_lon: float,
        db: Session,
        file_path: str
    ):
        geocode_responses = await self.geocode_service.import_data_from_csv(user_lat, user_lon, file_path)
        return await self.process_batch_destinations(trip_id, db, geocode_responses)
    

    async def get_destination_by_id(
        self,
        destination_id: int,
        db: Session
    ):
        return await DestinationRepository().get_destination(destination_id, db)


    async def get_destinations_for_trip(
        self,
        trip_id: int,
        db: Session
    ):
        destinations = await DestinationRepository().list_trip_destinations(trip_id, db)
        return destinations
    

    async def delete_destination(
        self,
        destination_id: int,
        db: Session
    ):
        return await DestinationRepository().delete_destination(destination_id, db)


    async def get_sorted_destinations(
        self,
        trip_id: int,
        user_lat: float,
        user_lon: float,
        db: Session
    ):
        db_destinations = await DestinationRepository().list_destinations_for_trip(trip_id, db)

        destionations_dict = [dest._asdict() for dest in db_destinations]
        
        destinations_with_distance = []
        for dest in destionations_dict:
            if dest["latitude"] is not None and dest["longitude"] is not None:
                distance = haversine_distance(user_lat, user_lon, dest["latitude"], dest["longitude"])
                dest["distance_from_user"] = distance
                destinations_with_distance.append(dest)
        
        destinations_with_distance.sort(key=lambda d: d["distance_from_user"])
        
        return destinations_with_distance

