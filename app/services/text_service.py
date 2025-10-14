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
