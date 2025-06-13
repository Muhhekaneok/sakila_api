from fastapi import FastAPI
from db.connection import get_connection

app = FastAPI()


@app.get("/")
def read_root():
    try:
        connection = get_connection()
        if connection.is_connected():
            return {"message": "Connected to sakila db"}
    except Exception as e:
        return {"error": e}
