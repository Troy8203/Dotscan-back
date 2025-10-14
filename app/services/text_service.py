import os
import io
import shutil
import numpy as np
from PIL import Image
from typing import List
from datetime import datetime
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse


# Core
from app.core.utils import success_response, error_response
from app.core.messages import Messages

# Utils
from app.utils.brf import text_to_ascii_braille, text_to_brf_file
from app.utils.file import validate_file_extension, validate_file_size
from app.utils.text_tools import image_text_to_segmentation, image_text_to_text


def upload_image_service(
    file: UploadFile,
    conf_threshold: float = 0.001,
    iou_threshold: float = 0.15,
):
    try:
        validate_file_extension(file.filename)
        validate_file_size(file)

        img_bytes = image_text_to_segmentation(file, conf_threshold, iou_threshold)
        return StreamingResponse(img_bytes, media_type="image/jpeg")

    except Exception as e:
        return error_response(f"{Messages.IMAGE_UPLOAD_ERROR}: {e}", status_code=500)


def upload_image_service_to_text(
    file: UploadFile,
    conf_threshold: float = 0.001,
    iou_threshold: float = 0.15,
    y_threshold: int = 20,
):
    try:
        validate_file_extension(file.filename)
        validate_file_size(file)

        response = image_text_to_text(file, conf_threshold, iou_threshold, y_threshold)

        return success_response(
            message=Messages.SUCCESS_OPERATION,
            data={"text": response},
        )

    except Exception as e:
        return error_response(f"{Messages.IMAGE_UPLOAD_ERROR}: {e}", status_code=500)


def upload_batch_images_service(
    files: List[UploadFile],
    conf_threshold: float = 0.001,
    iou_threshold: float = 0.15,
    y_threshold: int = 20,
):
    results = ""
    successful_uploads = 0
    failed_uploads = 0

    for file in files:
        try:
            validate_file_extension(file.filename)
            validate_file_size(file)
            text_converted = image_text_to_text(
                file, conf_threshold, iou_threshold, y_threshold
            )

            results += f"{text_to_ascii_braille(text_converted)}\n"
            successful_uploads += 1

        except HTTPException as e:
            failed_uploads += 1

        except Exception as e:
            failed_uploads += 1
            return error_response(
                f"{Messages.IMAGE_UPLOAD_ERROR}: {e}", status_code=500
            )

    return success_response(
        message=Messages.IMAGE_UPLOAD_BATCH_SUCCESS,
        data={
            "text": results,
            "total_files": len(files),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
        },
        status_code=207,
    )


def upload_batch_images_to_brf(
    files: List[UploadFile],
    conf_threshold: float = 0.001,
    iou_threshold: float = 0.15,
    y_threshold: int = 20,
):
    text = ""

    for file in files:
        try:
            validate_file_extension(file.filename)
            validate_file_size(file)
            text_converted = image_text_to_text(
                file, conf_threshold, iou_threshold, y_threshold
            )
            text += f"{text_converted}\n"

        except Exception as e:
            return error_response(f"{Messages.EXCEPTION_DEFAULT}: {e}", status_code=500)

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    brf_bytes = text_to_brf_file(text)

    return StreamingResponse(
        brf_bytes,
        media_type="application/x-brf",
        headers={"Content-Disposition": f"attachment; filename={current_date}.brf"},
    )
