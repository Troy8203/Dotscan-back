from typing import List
from fastapi import APIRouter, UploadFile, File, Depends

# Schemas
from app.schemas.braille import UuidBraille

# Services
from app.services.text_service import upload_image_service, upload_image_service_to_text

router = APIRouter(tags=["Text"])


@router.post(
    "",
    summary="API para detectar caracteres en una imagen",
    description="Sube una imagen y retorna una imagen con los caracteres encontrados",
)
async def upload_image(file: UploadFile = File(...)):
    return upload_image_service(file)


@router.post(
    "/texto-test",
    summary="API para traducir una imagen a braille",
    description="Sube una imagen y retorna una imagen con los caracteres traducidos",
)
async def upload_image(file: UploadFile = File(...)):
    return upload_image_service_to_text(file)
