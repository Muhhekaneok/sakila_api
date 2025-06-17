from fastapi import APIRouter, Query, Path

from db.connection import get_connection, get_logging_connection

router = APIRouter()


@router.get("/popular-searches")
def get_popular_searches(limit: int = Query(10, ge=1, le=20)):
    connection = get_logging_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            keyword,
            search_type,
            counter,
            created_at
        FROM recq
        ORDER BY counter DESC, created_at DESC
        LIMIT %s
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


@router.get("/top-rented-films")
def get_top_rented_films(limit: int = Query(10, ge=1, le=20)):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            f.film_id,
            f.title,
            COUNT(r.rental_id) AS rental_count
        FROM rental AS r
        JOIN inventory AS i
        ON r.inventory_id = i.inventory_id
        JOIN film AS f
        ON i.film_id = f.film_id
        GROUP BY f.film_id, f.title
        ORDER BY rental_count DESC
        LIMIT %s
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


@router.get("/top-paying-customers")
def get_top_paying_customers(limit: int = Query(10, ge=1, le=20)):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            c.customer_id,
            c.first_name,
            c.last_name,
            SUM(p.amount) AS total_paid
        FROM payment AS p
        JOIN customer AS c
        ON p.customer_id = c.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name
        ORDER BY total_paid DESC
        LIMIT %s
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


@router.get("/available-films/{store_id}")
def get_available_films_by_store(store_id: int = Path(..., ge=1, le=2)):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            f.film_id,
            f.title,
            COUNT(i.inventory_id) AS available_count
        FROM film AS f
        JOIN inventory AS i
        ON f.film_id = i.film_id
        LEFT JOIN rental AS r                                           -- см. ниже
        ON r.inventory_id = i.inventory_id AND r.return_date IS NULL    -- находится ли экземпляр в аренде
        WHERE i.store_id = %s AND r.rental_id IS NULL                   -- фильтрует только неарендованные копии
        GROUP BY f.film_id, f.title
        ORDER BY available_count DESC
        """,
        (store_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


@router.get("/top-actors")
def get_top_actors_by_film_count(limit: int = Query(10, ge=1, le=20)):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            a.actor_id,
            a.first_name,
            a.last_name,
            COUNT(fa.film_id) AS film_count
        FROM actor AS a
        JOIN film_actor AS fa
        ON a.actor_id = fa.actor_id
        GROUP BY a.actor_id, a.first_name, a.last_name
        ORDER BY film_count DESC
        LIMIT %s
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows