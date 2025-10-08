from pydantic import BaseModel
from typing import List
from uuid import UUID


class ImageRequest(BaseModel):
    uuid: UUID


class BatchUploadResponse(BaseModel):
    total_files: int
    successful_uploads: int
    failed_uploads: int
    results: List[dict]
