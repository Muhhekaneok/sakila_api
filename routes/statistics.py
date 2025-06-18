import plotly.graph_objects as go
from fastapi import APIRouter, Query, Path
from fastapi.responses import HTMLResponse

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


@router.get("/stats/top-customers-chart", response_class=HTMLResponse)
def get_top_customers_chart(limit: int = Query(10, ge=1, le=20)):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            CONCAT(c.first_name, ' ',c.last_name) AS name,
            SUM(p.amount) AS total_paid
        FROM customer AS c
        JOIN payment AS p
        ON c.customer_id = p.customer_id
        GROUP BY c.customer_id
        ORDER BY total_paid DESC
        LIMIT %s
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    names = [row[0] for row in rows]
    totals = [float(row[1]) for row in rows]

    fig = go.Figure(
        data=[
            go.Bar(
                x=names,
                y=totals,
                text=[f"${t}" for t in totals],
                textposition="outside"
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Top Customers by Payment",
            x=.5,
            font=dict(
                size=24
            )
        ),
        xaxis_title="Customer",
        yaxis_title="Total Paid",
        xaxis_title_font=dict(size=20),
        yaxis_title_font=dict(size=20),
        template="plotly_dark",
        uniformtext_minsize=16,
        uniformtext_mode='hide'
    )

    fig.update_traces(marker_color="sky blue")

    return fig.to_html(full_html=True)


@router.get("/stats/top-films-chart", response_class=HTMLResponse)
def get_top_films_by_genres_chart(limit: int = Query(10, ge=1, le=20)):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            c.name AS genre,
            COUNT(fc.film_id) AS film_count
        FROM category AS c
        JOIN film_category AS fc
        ON c.category_id = fc.category_id
        GROUP BY c.name
        ORDER BY film_count DESC
        LIMIT %s
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    genres = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    fig = go.Figure(
        data=[
            go.Bar(
                x=genres,
                y=counts,
                text=[c for c in counts],
                textposition="outside"
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Number of Films by Genre",
            x=.5,
            font=dict(
                size=24
            )
        ),
        xaxis_title="Genre",
        yaxis_title="Film Count",
        xaxis_title_font=dict(size=20),
        yaxis_title_font=dict(size=20),
        template="plotly_dark",
        uniformtext_minsize=16,
        uniformtext_mode='hide'
    )

    fig.update_traces(marker_color="orange")

    return fig.to_html(full_html=True)


@router.get("/stats/films-by-year-count-chart", response_class=HTMLResponse)
def get_film_count_by_years_chart():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            release_year,
            COUNT(*) as film_count
        FROM film
        GROUP BY release_year
        ORDER By release_year DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    years = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    fig = go.Figure(
        data=[
            go.Bar(
                x=years,
                y=counts,
                text=[c for c in counts],
                textposition="outside"
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Number of Films by Release Year",
            x=.5,
            font=dict(
                size=24
            )
        ),
        xaxis_title="Release Year",
        yaxis_title="Film Count",
        xaxis_title_font=dict(size=20),
        yaxis_title_font=dict(size=20),
        template="plotly_dark",
        uniformtext_minsize=16,
        uniformtext_mode='hide'
    )

    fig.update_traces(marker_color="limegreen")

    return fig.to_html(full_html=True)


@router.get("/stats/popular-keywords-chart", response_class=HTMLResponse)
def get_popular_keywords_chart(limit: int = Query(10, ge=1, le=20)):
    connection = get_logging_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            keyword,
            SUM(counter) AS total
        FROM recq
        GROUP BY keyword
        ORDER BY total DESC
        LIMIT %s
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    keywords = [row[0] for row in rows]
    counters = [row[1] for row in rows]

    fig = go.Figure(
        data=[
            go.Bar(
                x=keywords,
                y=counters,
                text=[c for c in counters],
                textposition="outside"
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=f"Top {limit} Searched Keywords",
            x=.5,
            font=dict(size=24)
        ),
        xaxis_title="Keyword",
        yaxis_title="Search Count",
        xaxis_title_font=dict(size=20),
        yaxis_title_font=dict(size=20),
        template="plotly_dark",
        uniformtext_minsize=16,
        uniformtext_mode='hide'
    )

    fig.update_traces(marker_color="magenta")

    return fig.to_html(full_html=True)


@router.get("/stats/search-types-chart", response_class=HTMLResponse)
def get_search_type_chart():
    connection = get_logging_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            search_type,
            COUNT(*) AS total
        FROM recq
        GROUP BY search_type
        ORDER BY total DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    types = [row[0] for row in rows]
    totals = [row[1] for row in rows]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=types,
                values=totals,
                textinfo="label+percent",
                textfont=dict(size=35),
                hole=.7
            )
        ]
    )

    fig.update_layout(
        title={
            "text": "Search Type Distribution",
            "x": .5,
            "font": {"size": 24}
        },
        template="plotly_dark"
    )

    return fig.to_html(full_html=True)