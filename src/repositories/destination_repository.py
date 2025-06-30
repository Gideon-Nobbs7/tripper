import time

from fastapi import HTTPException
from prometheus_client import Counter, Histogram
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.schemas.geocode import *

add_destination_counter = Counter("add_destination", "Rate destinations are added")
add_destination_duration = Histogram("add_destination_time", "Time taken to add a new destination")


class DestinationRepository:

    async def create_destination(
        self,
        db: Session,
        trip_id: int,
        location: str,
        longitude: float,
        latitude: float,
    ):
        add_destination_counter.inc()

        start_time = time.time()
        try:
            query = text(
                "INSERT INTO destination " \
                "(location, longitude, latitude, trip_id)" \
                "VALUES" \
                "(:location, :longitude, :latitude, :trip_id)" \
                "RETURNING id, location, longitude, latitude, trip_id, created_at" 
            )
            result = db.execute(query, {
                "location": location,
                "longitude": longitude,
                "latitude": latitude,
                "trip_id": trip_id
            })

            db.commit()
            
            row = result.fetchone()
            if row:
                result_dict = row._asdict()
                return result_dict
            else:
                return None
        finally:
            duration = time.time() - start_time
            add_destination_duration.observe(duration)
        

    async def get_destination(
        self,
        trip_id: int,
        destination_id: int,
        db: Session
    ):
        query = text("""
            SELECT destination.* FROM destination
            LEFT JOIN trip ON
            destination.trip_id = :trip_id
            WHERE destination.id = :destination_id
            GROUP BY destination.id
        """)
        result = db.execute(query, {
            "trip_id": trip_id,
            "destination_id": destination_id
        })
        details = result.mappings().fetchone()
        return details


    async def list_destinations_for_trip(
        self,
        trip_id: int,
        db: Session
    ):
        query = text("""
            SELECT destination.* FROM destination
            WHERE destination.trip_id = :trip_id
        """)
        result = db.execute(query, {
            "trip_id": trip_id
        })
        details = result.fetchall()
        print("Type of fetched details:...", type(details))
        return details


    async def delete_destination(
        self,
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
