from typing import Optional
from pydantic import BaseModel


class Assessment(BaseModel):

    id: Optional[int]
    owner: str | None
