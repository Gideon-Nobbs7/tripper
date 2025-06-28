from src.repositories.trip_repository import TripService
from src.services.destination import DestinationService



def get_trip_service():
    return TripService()


def get_destination_service():
    return DestinationService()
