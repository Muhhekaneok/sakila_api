from pydantic import BaseModel


class Actor(BaseModel):
    actor_id: int
    first_name: str
    last_name: str
