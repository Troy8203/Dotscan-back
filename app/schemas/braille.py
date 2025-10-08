from pydantic import BaseModel
from typing import List
from uuid import UUID


class UuidBraille(BaseModel):
    uuid: UUID
