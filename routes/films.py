from fastapi import APIRouter, HTTPException, Path
from fastapi.params import Query

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
def search_films_by_keyword(keyword: str):
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


@router.get("/films/genre/{genre_name}", response_model=list[Film])
def get_film_by_genre(genre_name: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            f.film_id,
            f.title,
            f.description,
            f.release_year
        FROM film AS f
        JOIN film_category AS fc
        ON f.film_id = fc.film_id
        JOIN category AS c
        ON fc.category_id = c.category_id
        WHERE c.name = %s
        LIMIT 20
        """,
        (genre_name,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No films with this genre")

    save_search_keyword(keyword=genre_name, search_type="genre")

    return [
        Film(film_id=row[0], title=row[1], description=row[2], release_year=row[3])
        for row in rows
    ]


@router.get("/films/year/{year_start}", response_model=list[Film])
def get_film_by_years(year_start: int = Path(..., ge=1990, le=2025),
                      year_end: int = Query(None, ge=1990, le=2025)):
    connection = get_connection()
    cursor = connection.cursor()

    if year_end:
        query = """
        SELECT
            film_id,
            title,
            description,
            release_year
        FROM film
        WHERE release_year BETWEEN %s AND %s
        LIMIT 20
        """
        cursor.execute(query, (year_start, year_end))
    else:
        query = """
        SELECT
            film_id,
            title,
            description,
            release_year
        FROM film
        WHERE release_year = %s
        LIMIT 20
        """
        cursor.execute(query, (year_start,))

    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No films found for this year(s)")

    return [
        Film(film_id=row[0], title=row[1], description=row[2], release_year=row[3])
        for row in rows
    ]


@router.get("/films/{film_id}", response_model=Film)
def get_film_by_id(film_id: int = Path(..., ge=1, le=1000, description="ID of a film (1-1000)")):
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
