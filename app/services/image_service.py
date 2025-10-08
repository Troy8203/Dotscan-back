import os
import glob
import shutil
from typing import List
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse


# Core
from app.core.utils import success_response, error_response

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
        return error_response("Imagen no encontrada")

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

        return success_response(
            message="Imagen subida correctamente",
            data={
                "filename": safe_filename,
                "file_size": file_size,
                "content_type": file.content_type,
                "url": f"/images/{safe_filename}",
            },
        )

    except Exception as e:
        return error_response(f"Error al guardar la imagen: {str(e)}")


def upload_batch_images_service(files: List[UploadFile]):
    results = []
    successful_uploads = 0
    failed_uploads = 0

    for file in files:
        try:
            validate_file_extension(file.filename)
            file_size = validate_file_size(file)

            safe_filename = generate_unique_filename(file.filename)
            file_path = os.path.join(NFS_PATH, safe_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            results.append(
                {
                    "filename": safe_filename,
                    "original_name": file.filename,
                    "file_size": file_size,
                    "content_type": file.content_type,
                    "url": f"/images/{safe_filename}",
                    "status": "success",
                    "message": "Imagen subida correctamente",
                }
            )
            successful_uploads += 1

        except HTTPException as e:
            results.append(
                {"filename": file.filename, "status": "error", "message": e.detail}
            )
            failed_uploads += 1

        except Exception as e:
            results.append(
                {
                    "filename": file.filename,
                    "status": "error",
                    "message": f"Error al guardar la imagen: {str(e)}",
                }
            )
            failed_uploads += 1

    return success_response(
        message=f"Procesamiento de lote completado",
        data={
            "total_files": len(files),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "results": results,
        },
        status_code=207,
    )
