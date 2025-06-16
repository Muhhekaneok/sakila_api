from fastapi import APIRouter, HTTPException

from db.connection import get_connection
from models.film import Film
from routes.recorder import save_search_keyword

router = APIRouter()


@router.get("/films", response_model=list[Film])
def get_all_films():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            film_id,
            title,
            description,
            release_year
        FROM film
        LIMIT 10
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    films = [
        Film(film_id=row[0], title=row[1], description=row[2], release_year=row[3])
        for row in rows
    ]
    return films


@router.get("/films/search", response_model=list[Film])
def search_films_by_key_word(keyword: str):
    connection = get_connection()
    cursor = connection.cursor()
    like_pattern = f"%{keyword}%"
    cursor.execute(
        """
        SELECT
            film_id,
            title,
            description,
            release_year
        FROM film
        WHERE title LIKE %s OR description LIKE %s
        LIMIT 20
        """,
        (like_pattern, like_pattern)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No films found with given keyword")

    save_search_keyword(keyword=keyword)

    return [
        Film(film_id=row[0], title=row[1], description=row[2], release_year=row[3])
        for row in rows
    ]


@router.get("/films/{film_id}", response_model=Film)
def get_film_by_id(film_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            film_id,
            title,
            description,
            release_year
        FROM film
        WHERE film_id = %s
        """,
        (film_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if row:
        return Film(film_id=row[0], title=row[1], description=row[2], release_year=row[3])
    else:
        raise HTTPException(status_code=404, detail="No film found for this id")
