from sqlalchemy import text
from sqlalchemy.orm import Session

from src.schemas.trip import *


async def create_trip(
    trip: TripCreateModel,
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


async def alter_trip(
    id: int,
    trip: TripUpdateRequest,
    db: Session
):
    # query = text(
    #     "UPDATE trip" \
    #     "SET name = :name" \
    #     "WHERE id = :id"
    # )
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


async def remove_trip(
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


async def trip_detail(
    id: int,
    db: Session
):
    # query = text(
    #     "SELECT trip.*, COUNT(destination.trip_id) AS destinations " \
    #     "FROM trip JOIN destination ON " \
    #     "trip.id = destination.trip_id " \
    #     "WHERE id = :id" \
    #     "GROUP BY trip.id"
    # )
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