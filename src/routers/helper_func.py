from sqlalchemy import text
from sqlalchemy.orm import Session

from src.schemas.schema import CoordinateModel, TripModel


async def new_trip(
    trip: TripModel,
    db: Session
):
    query = text(
        "INSERT INTO trip (name) VALUES (:name) " \
        "RETURNING id, name, created_at"
    )
    result = db.execute(query, {"name":trip.name})
    db.commit()
    new_trip = result.fetchone()
    return new_trip



async def add_destination(
    db: Session,
    trip_id: int,
    location: str,
    longitude: float,
    latitude: float,
    distance_from_user_km: float,
):
    query = text(
        "INSERT INTO destination " \
        "(location, longitude, latitude, distance_from_user_km, trip_id)" \
        "VALUES" \
        "(:location, :longitude, :latitude, :distance_from_user_km, :trip_id)" \
        "RETURNING location, longitude, latitude, distance_from_user_km" 
    )
    result = db.execute(query, {
        "location": location,
        "longitude": longitude,
        "latitude": latitude,
        "distance_from_user_km": distance_from_user_km,
        "trip_id": trip_id
    })

    db.commit()
    
    row = result.fetchone()
    if row:
        result_dict = row._asdict()
        return result_dict
    else:
        return None