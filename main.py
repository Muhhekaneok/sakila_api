from fastapi import FastAPI

from routes import films, actors, statistics

app = FastAPI()

app.include_router(films.router)
app.include_router(actors.router)
app.include_router(statistics.router)


@app.get("/")
def read_root():
    return {"message": "Sakila API is running"}
