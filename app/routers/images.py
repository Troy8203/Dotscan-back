from fastapi import APIRouter, UploadFile, File, Depends

# Schemas
from app.schemas.image import ImageRequest

# Services
from app.services.image_service import (
    get_image_service,
    upload_image_service,
)

router = APIRouter(tags=["Images"])


@router.get(
    "/{image_name}",
    summary="API para obtener una imagen",
    description="Retorna una imagen del almacenamiento NFS",
)
async def get_image(request: ImageRequest = Depends()):
    return get_image_service(request.image_name)


@router.post(
    "",
    summary="API para subir una imagen",
    description="Retorna la información del archivo subido",
)
async def upload_image(file: UploadFile = File(...)):
    return upload_image_service(file)
