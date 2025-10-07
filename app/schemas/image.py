from pydantic import BaseModel
from uuid import UUID


class ImageRequest(BaseModel):
    uuid: UUID
