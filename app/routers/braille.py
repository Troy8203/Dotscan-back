from typing import List
from fastapi import APIRouter, UploadFile, File, Depends

# Schemas
from app.schemas.braille import UuidBraille

# Services
from app.services.braille_service import (
    get_image_service,
    upload_image_service,
    upload_batch_images_service,
    upload_image_service_to_text,
    upload_batch_images_to_pdf,
)

router = APIRouter(tags=["Braille"])


@router.get(
    "/{uuid}",
    summary="API para obtener una imagen",
    description="Retorna una imagen del almacenamiento NFS",
)
async def get_image(request: UuidBraille = Depends()):
    uuid_str = str(request.uuid)
    return get_image_service(uuid_str)


@router.post(
    "",
    summary="API para traducir una imagen",
    description="Sube una imagen y retorna una imagen con los caracteres traducidos",
)
async def upload_image(file: UploadFile = File(...)):
    return upload_image_service(file)


@router.post(
    "/texto-test",
    summary="API para traducir una imagen",
    description="Sube una imagen y retorna una imagen con los caracteres traducidos",
)
async def upload_image(file: UploadFile = File(...)):
    return upload_image_service_to_text(file)


@router.post(
    "/text",
    summary="API para subir múltiples imágenes en braille",
    description="Sube muchas imágenes y retorna un texto con los caracteres traducidos",
)
async def upload_batch_images(files: List[UploadFile] = File(...)):
    return upload_batch_images_service(files)


@router.post(
    "/pdf",
    summary="API para subir múltiples imágenes en braille",
    description="Sube muchas imágenes y retorna un archivo pdf con los caracteres traducidos",
)
async def upload_batch_pdf(files: List[UploadFile] = File(...)):
    return upload_batch_images_to_pdf(files)


@router.post(
    "/brf",
    summary="API para subir múltiples imágenes en braille",
    description="Sube muchas imágenes y retorna un archivo brf con los caracteres traducidos",
)
async def upload_batch_images(files: List[UploadFile] = File(...)):
    return upload_batch_images_service(files)
