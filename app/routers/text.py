from typing import List
from fastapi import APIRouter, UploadFile, File, Depends

# Schemas
from app.schemas.braille import UuidBraille

# Services
from app.services.text_service import (
    upload_image_service,
    upload_image_service_to_text,
    upload_batch_images_service,
    upload_batch_images_to_brf,
)

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
    summary="API para traducir una imagen a texto convencional",
    description="Sube una imagen y retorna una imagen con los caracteres traducidos",
)
async def upload_image(file: UploadFile = File(...)):
    return upload_image_service_to_text(file)


@router.post(
    "/text",
    summary="API para subir múltiples imágenes en texto convencional",
    description="Sube muchas imágenes y retorna un texto con los caracteres traducidos",
)
async def upload_batch_images(files: List[UploadFile] = File(...)):
    return upload_batch_images_service(files)


@router.post(
    "/brf",
    summary="API para subir múltiples imágenes en texto convencional",
    description="Sube muchas imágenes y retorna un archivo pdf con los caracteres traducidos",
)
async def upload_batch_pdf(files: List[UploadFile] = File(...)):
    return upload_batch_images_to_brf(files)
