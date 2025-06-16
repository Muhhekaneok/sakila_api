from db.connection import get_logging_connection


def save_search_keyword(keyword: str, search_type: str = "film"):
    connection = get_logging_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            id,
            counter
        FROM recq
        WHERE keyword = %s AND search_type = %s
        """,
        (keyword, search_type)
    )
    row = cursor.fetchone()

    if row:
        recq_id, counter = row
        cursor.execute(
            """
            UPDATE recq
            SET counter = %s, created_at = NOW()
            WHERE id = %s
            """,
            (counter + 1, recq_id)
        )
    else:
        cursor.execute(
            """
            INSERT INTO recq (keyword, search_type)
            VALUES (%s, %s)
            """,
            (keyword, search_type)
        )
    connection.commit()
    cursor.close()
    connection.close()