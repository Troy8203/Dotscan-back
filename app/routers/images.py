from typing import List
from fastapi import APIRouter, UploadFile, File, Depends

# Schemas
from app.schemas.image import ImageRequest

# Services
from app.services.image_service import (
    get_image_service,
    upload_image_service,
    upload_batch_images_service,
)

router = APIRouter(tags=["Images"])


@router.get(
    "/{uuid}",
    summary="API para obtener una imagen",
    description="Retorna una imagen del almacenamiento NFS",
)
async def get_image(request: ImageRequest = Depends()):
    uuid_str = str(request.uuid)
    return get_image_service(uuid_str)


@router.post(
    "",
    summary="API para subir una imagen",
    description="Retorna la información del archivo subido",
)
async def upload_image(file: UploadFile = File(...)):
    return upload_image_service(file)


@router.post(
    "/batch",
    summary="API para subir múltiples imágenes en lote",
    description="Retorna el resultado de todas las imágenes procesadas",
)
async def upload_batch_images(files: List[UploadFile] = File(...)):
    return upload_batch_images_service(files)
