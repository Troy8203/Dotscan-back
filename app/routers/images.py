from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Schemas
from app.schemas.image import ImageRequest

# Utils
from app.utils.file import validate_file_extension, validate_file_size

load_dotenv()

router = APIRouter(tags=["Images"])

NFS_PATH = os.getenv("NFS_PATH", "/")

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


@router.get(
    "/{image_name}",
    summary="API para obtener una imagen",
    description="Retorna una imagen del almacenamiento NFS",
)
async def get_image(request: ImageRequest = Depends()):
    image_name = request.image_name

    if ".." in image_name or "/" in image_name:
        raise HTTPException(status_code=400, detail="File name invalid")

    image_path = os.path.join(NFS_PATH, image_name)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)


@router.post(
    "",
    summary="API para subir una imagen",
    description="Retorna la información del archivo subido",
    response_model=dict,
)
async def upload_image(file: UploadFile = File(...)):
    validate_file_extension(file.filename)
    file_size = validate_file_size(file)

    # Crear nombre seguro para el archivo
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._-")
    file_path = os.path.join(NFS_PATH, safe_filename)

    # Verificar si el archivo ya existe
    if os.path.exists(file_path):
        raise HTTPException(
            status_code=400,
            detail="Ya existe un archivo con ese nombre. Por favor, renombra el archivo.",
        )

    try:
        # Guardar el archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Obtener información del archivo guardado
        file_info = {
            "filename": safe_filename,
            "file_size": file_size,
            "content_type": file.content_type,
            "url": f"/images/{safe_filename}",
            "message": "Imagen subida correctamente",
        }

        return JSONResponse(content=file_info, status_code=201)

    except Exception as e:
        # Si hay error, eliminar el archivo si se creó parcialmente
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500, detail=f"Error al guardar la imagen: {str(e)}"
        )
