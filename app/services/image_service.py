import os
import shutil
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse

# Utils
from app.utils.file import validate_file_extension, validate_file_size

NFS_PATH = os.getenv("NFS_PATH", "/")


def _create_safe_filename(filename: str) -> str:
    """Crea un nombre de archivo seguro"""
    return "".join(c for c in filename if c.isalnum() or c in "._-")


def get_image_service(image_name: str):
    """Obtener una imagen del almacenamiento"""
    if ".." in image_name or "/" in image_name:
        raise HTTPException(status_code=400, detail="File name invalid")

    image_path = os.path.join(NFS_PATH, image_name)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)


def upload_image_service(file: UploadFile):
    """Subir una imagen al almacenamiento"""
    # Usar utils existentes
    validate_file_extension(file.filename)
    file_size = validate_file_size(file)

    # Crear nombre seguro
    safe_filename = _create_safe_filename(file.filename)
    file_path = os.path.join(NFS_PATH, safe_filename)

    # Verificar si ya existe
    if os.path.exists(file_path):
        raise HTTPException(
            status_code=400,
            detail="Ya existe un archivo con ese nombre. Por favor, renombra el archivo.",
        )

    try:
        # Guardar el archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Retornar información
        return {
            "filename": safe_filename,
            "file_size": file_size,
            "content_type": file.content_type,
            "url": f"/images/{safe_filename}",
            "message": "Imagen subida correctamente",
        }

    except Exception as e:
        # Limpieza en caso de error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500, detail=f"Error al guardar la imagen: {str(e)}"
        )
