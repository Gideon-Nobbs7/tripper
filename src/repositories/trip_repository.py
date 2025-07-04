from sqlalchemy import text
from sqlalchemy.orm import Session

from src.schemas.trip import *


class TripService:

    async def create_trip(
        self,
        trip: TripCreateModel,
        db: Session
    ):
        query = text(
            "INSERT INTO trip (name) VALUES (:name) " \
            "RETURNING id, name, created_at"
        )
        # query = text(""""
        #     INSERT INTO trip (name) VALUES (:name)
        #     RETURNING id, name, created_at
        # """)
        result = db.execute(query, {"name":trip.name})
        db.commit()
        new_trip = result.fetchone()
        return new_trip


    async def update_trip(
        self,
        id: int,
        trip: TripUpdateRequest,
        db: Session
    ):
        query = text("""
            UPDATE trip
            SET name = :name
            WHERE id = :id
            RETURNING id, name, created_at
        """)

        result = db.execute(query, {
            "id": id,
            "name": trip.name
        })
        updated_trip = result.mappings().fetchone()
        db.commit()

        return updated_trip


    async def delete_trip(
        self,
        id: int,
        db: Session
    ):
        query = text(
            "DELETE FROM trip" \
            "WHERE id = :id"
        )

        result = db.execute(query, {
            "id": id,
        })

        db.commit()
        return result.fetchone()


    async def get_trips(
        self,
        db: Session
    ):
        query = text("""
            SELECT * FROM trip
        """)

        result = db.execute(query)

        trips = result.fetchall()
        return trips


    async def trip_detail(
        self,
        id: int,
        db: Session
    ):
        query = text("""
            SELECT trip.*, COUNT(destination.trip_id) AS count,
            COALESCE(
                JSON_AGG(destination.*) FILTER (WHERE destination.id IS NOT NULL),
                '[]'
            ) AS destinations
            FROM trip LEFT JOIN destination ON 
            trip.id = destination.trip_id
            WHERE trip.id = :id
            GROUP BY trip.id
        """)

        result = db.execute(query, {
            "id": id
        })

        trip_details = result.mappings().fetchone()
        return trip_details