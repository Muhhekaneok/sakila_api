from fastapi import APIRouter, HTTPException

from db.connection import get_connection
from models.actor import Actor

router = APIRouter()


@router.get("/actors", response_model=list[Actor])
def get_all_actors():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            actor_id,
            first_name,
            last_name
        FROM actor
        LIMIT 10
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    actors = [
        Actor(actor_id=row[0], first_name=row[1], last_name=row[2])
        for row in rows
    ]

    return actors


@router.get("/actors/{actor_id}", response_model=Actor)
def get_actor_by_id(actor_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            actor_id,
            first_name,
            last_name
        FROM actor
        WHERE actor_id = %s
        """,
        (actor_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if row:
        return Actor(actor_id=row[0], first_name=row[1], last_name=row[2])
    else:
        raise HTTPException(status_code=404, detail="No actor found with this id")