from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

from app.schemas.image import ImageRequest

load_dotenv()

router = APIRouter(tags=["Images"])

NFS_PATH = os.getenv("NFS_PATH", "/")

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


@router.get(
    "/{image_name}",
    summary="API to get an image",
    description="Return an image from the server",
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
    "/upload/",
    summary="Upload an image",
    description="Upload an image to the server",
    response_model=dict,
)
async def upload_image(file: UploadFile = File(...)):
    """
    Subir una imagen al servidor.

    - **file**: Archivo de imagen a subir (formatos: PNG, JPG, JPEG, GIF, WEBP, SVG)

    Returns información sobre la imagen subida.
    """
    # Validar extensión del archivo
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Extensiones válidas: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Validar tamaño del archivo (ejemplo: máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file.file.seek(0, 2)  # Ir al final del archivo
    file_size = file.file.tell()
    file.file.seek(0)  # Volver al inicio

    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Tamaño máximo: {max_size // (1024*1024)}MB",
        )

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


@router.delete(
    "/{image_name}",
    summary="Eliminar una imagen",
    description="Elimina una imagen del almacenamiento NFS",
    response_model=dict,
)
async def delete_image(image_name: str):
    """
    Eliminar una imagen específica por nombre de archivo.

    - **image_name**: Nombre del archivo de imagen a eliminar
    """
    if ".." in image_name or "/" in image_name:
        raise HTTPException(status_code=400, detail="Nombre de imagen inválido")

    image_path = os.path.join(NFS_PATH, image_name)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    try:
        os.remove(image_path)
        return {"message": f"Imagen '{image_name}' eliminada correctamente"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar la imagen: {str(e)}"
        )
