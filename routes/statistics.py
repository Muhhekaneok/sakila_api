from fastapi import APIRouter, Query

from db.connection import get_logging_connection

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