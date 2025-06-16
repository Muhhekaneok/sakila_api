from pydantic import BaseModel


class Film(BaseModel):
    film_id: int
    title: str
    description: str | None
    release_year: int
