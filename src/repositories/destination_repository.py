from sqlalchemy import text
from sqlalchemy.orm import Session

from src.schemas.geocode import *


async def add_destination(
    db: Session,
    trip_id: int,
    location: str,
    longitude: float,
    lattitude: float,
    distance_from_user_km: float,
):
    query = text(
        "INSERT INTO destination " \
        "(location, longitude, lattitude, distance_from_user_km, trip_id)" \
        "VALUES" \
        "(:location, :longitude, :lattitude, :distance_from_user_km, :trip_id)" \
        "RETURNING id, location, longitude, lattitude, distance_from_user_km, trip_id, created_at" 
    )
    result = db.execute(query, {
        "location": location,
        "longitude": longitude,
        "lattitude": lattitude,
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
    

async def retrieve_destination(
    destination_id: int,
    db: Session
):
    query = text("""
        SELECT destination.* FROM destination
        LEFT JOIN trip ON
        destination.trip_id = trip.id
        WHERE destination.id = :id
        GROUP BY destination.id
    """)

    result = db.execute(query, {
        "id": destination_id
    })

    details = result.mappings().fetchone()
    return details


async def remove_destination(
    destination_id: int,
    db: Session
):
    query = text("""
        DELETE FROM destination
        WHERE id = :id
    """)

    result = db.execute(query, {
        "id": destination_id,
    })
    db.commit()
