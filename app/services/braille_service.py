import os
import io
import glob
import shutil
from typing import List
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse


# Core
from app.core.utils import success_response, error_response
from app.core.messages import Messages

# Utils
from app.utils.file import (
    generate_unique_filename,
    validate_file_extension,
    validate_file_size,
)
from app.models.inference import model

NFS_PATH = os.getenv("NFS_PATH", "/")


def get_image_service(uuid: str):
    if ".." in uuid or "/" in uuid:
        raise HTTPException(status_code=400, detail="File name invalid")

    pattern = os.path.join(NFS_PATH, f"{uuid}.*")
    matching_files = glob.glob(pattern)

    if not matching_files:
        return error_response(Messages.IMAGE_NOT_FOUND, status_code=404)

    image_path = matching_files[0]
    return FileResponse(image_path)


def upload_image_service(file: UploadFile):
    import io
    import numpy as np
    import cv2
    from PIL import Image
    import shutil
    import os
    from fastapi.responses import StreamingResponse
    from app.core.utils import error_response
    from app.core.messages import Messages
    from app.utils.file import (
        generate_unique_filename,
        validate_file_extension,
        validate_file_size,
    )
    from app.models.inference import model  # tu modelo YOLOv5 ya cargado

    try:
        # 1️⃣ Validaciones
        validate_file_extension(file.filename)
        validate_file_size(file)

        # 2️⃣ Guardar temporalmente la imagen en NFS (o /tmp si quieres)
        safe_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(NFS_PATH, safe_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3️⃣ Procesar imagen con YOLOv5
        results = model(file_path)

        # 4️⃣ Abrir imagen original en numpy
        img = np.array(Image.open(file_path).convert("RGB"))

        # 5️⃣ Dibujar detecciones con un solo color uniforme
        border_color = (245, 166, 35)  # verde en BGR
        font_color = (35, 35, 35)
        thickness = 2
        font_scale = 0.8

        detections = results.pandas().xyxy[
            0
        ]  # xmin, ymin, xmax, ymax, confidence, name

        for _, row in detections.iterrows():
            x1, y1, x2, y2 = (
                int(row["xmin"]),
                int(row["ymin"]),
                int(row["xmax"]),
                int(row["ymax"]),
            )
            label = str(row["name"])
            # Dibujar rectángulo
            cv2.rectangle(img, (x1, y1), (x2, y2), border_color, thickness)
            # Escribir texto
            cv2.putText(
                img,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                font_color,
                3,
            )

        # 6️⃣ Convertir a PIL y luego a BytesIO para StreamingResponse
        pil_img = Image.fromarray(img)
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        return StreamingResponse(img_bytes, media_type="image/jpeg")

    except Exception as e:
        return error_response(f"{Messages.IMAGE_UPLOAD_ERROR}: {e}", status_code=500)


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
        message=Messages.IMAGE_UPLOAD_BATCH_SUCCESS,
        data={
            "total_files": len(files),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "results": results,
        },
        status_code=207,
    )
