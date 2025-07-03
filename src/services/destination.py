from typing import Any, List

from sqlalchemy.orm import Session

from src.exceptions.exceptions import DatabaseError
from src.repositories.destination_repository import DestinationRepository
from src.schemas.geocode import BatchGeocodeResponse, DestinationResponse
from src.services.geocode import GeocodeClass
from src.utils.utils import haversine_distance


class DestinationService:
    def __init__(self):
        self.geocode_service = GeocodeClass()

    
    async def process_single_destination(
        self,
        trip_id: int,
        db: Session,
        location: str,
    ):
        response = self.geocode_service.get_coordinates_for_destination(location=location)

        try:
            result = await DestinationRepository().add_destination(
                db=db,
                trip_id=trip_id,
                location=location,
                longitude=response["longitude"],
                latitude=response["latitude"],
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
                result = await DestinationRepository().create_destination(
                    db=db,
                    trip_id=trip_id,
                    location=response.location if hasattr(response, 'location') else response["location"],
                    longitude=response.longitude if hasattr(response, 'longitude') else response["longitude"],
                    latitude=response.latitude if hasattr(response, 'latitude') else response["latitude"],
                )
                results.append(result)
            except Exception as e:
                raise DatabaseError(f"Failed to add destination")
        
        return BatchGeocodeResponse(
            results=results,
            failed=geocode_responses.failed
        )

    
    def _extract_destination_data(self, response):
        return {
            "location": getattr(response, "location", None) or response["location"],
            "longitude": getattr(response, "longitude", None) or response["longitude"],
            "latitude": getattr(response, "latitude", None) or response["latitude"],
        }
    

    async def create_batch_destinations(
        self, 
        db: Session,
        trip_id: int,
        locations: List[str],
    ):
        geocode_responses = await self.geocode_service.geocode_with_thread_pool(locations)
        return await self.process_batch_destinations(trip_id, db, geocode_responses)
    

    async def create_manual_destinations(
        self,
        db: Session,
        trip_id: int,
        location: str,
        longitude: float,
        latitude: float,
    ):

        try:
            result = await DestinationRepository().create_destination(
                db=db,
                trip_id=trip_id,
                location=location,
                longitude=longitude,
                latitude=latitude,
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
    

    async def get_destination_by_id(
        self,
        trip_id: int,
        destination_id: int,
        db: Session
    ):
        return await DestinationRepository().get_destination(trip_id, destination_id, db)


    async def get_destinations_for_trip(
        self,
        trip_id: int,
        db: Session
    ):
        destinations = await DestinationRepository().list_destinations_for_trip(trip_id, db)
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
    

    async def get_optimal_route_destinations(
        self,
        trip_id: int,
        user_lat: float,
        user_lon: float,
        db: Session
    ):
        db_destinations = await DestinationRepository().list_destinations_for_trip(trip_id, db)

        destinations_dict = [dest._asdict() for dest in db_destinations]
        unvisited = {dest["id"]: dest for dest in destinations_dict if dest["latitude"] is not None and dest["longitude"] is not None}
        
        optimal_route_ordered = []

        current_lat, current_lon = user_lat, user_lon

        # destinations_with_distance = []
        while unvisited:
            nearest_dest = None
            min_distance = float("inf")

            for dest_id, dest in unvisited.items():
                if dest["latitude"] is not None and dest["longitude"] is not None:
                    distance = haversine_distance(current_lat, current_lon, dest["latitude"], dest["longitude"])
                    if distance < min_distance:
                        nearest_dest = dest
                        min_distance = distance
                
            if nearest_dest:
                nearest_dest["distance_from_user"] = min_distance
                optimal_route_ordered.append(nearest_dest)
                # setattr(nearest_dest, "distance_from_user", min_distance)

                current_lat, current_lon = nearest_dest["latitude"], nearest_dest["longitude"]

                unvisited.pop(nearest_dest["id"])
            else:
                break
        
        return optimal_route_ordered
    

    async def mark_destinations_as_visited(
        self,
        trip_id: int,
        destination_id: int,
        db: Session
    ):
        destination = await DestinationRepository().update_destination_as_visited(trip_id, destination_id, db)

        if not destination:
            return None
        return destination    
