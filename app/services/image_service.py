import os
import glob
import shutil
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse

# Utils
from app.utils.file import (
    generate_unique_filename,
    validate_file_extension,
    validate_file_size,
)

NFS_PATH = os.getenv("NFS_PATH", "/")


def get_image_service(uuid: str):
    if ".." in uuid or "/" in uuid:
        raise HTTPException(status_code=400, detail="File name invalid")

    pattern = os.path.join(NFS_PATH, f"{uuid}.*")
    matching_files = glob.glob(pattern)

    if not matching_files:
        raise HTTPException(status_code=404, detail="Image not found")

    image_path = matching_files[0]
    return FileResponse(image_path)


def upload_image_service(file: UploadFile):
    validate_file_extension(file.filename)
    file_size = validate_file_size(file)

    safe_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(NFS_PATH, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

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
