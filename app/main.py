import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from app.routers import images, items, users
from app.core.utils import error_response
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

name = os.getenv("NAME", "DotScan API Backend")
version = os.getenv("VERSION", "1.0.0")
description = os.getenv("DESCRIPTION", "Api for DotScan")

app = FastAPI(
    title=name,
    version=version,
    description=description,
)

logger = logging.getLogger("uvicorn")


@app.middleware("http")
async def log_responses(request: Request, call_next):
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"

    response = await call_next(request)

    process_time = time.time() - start_time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        body_content = b"".join(chunks)

        async def new_body_iterator():
            for chunk in chunks:
                yield chunk

        response.body_iterator = new_body_iterator()

        try:
            body_preview = body_content.decode("utf-8")
        except:
            body_preview = f"[Binary data - {len(body_content)} bytes]"

        logger.info(
            f"🌐 {timestamp} | {client_ip} | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Time: {process_time:.3f}s"
        )
        logger.info(f"📦 Response Body: {body_preview}")

    except Exception as e:
        logger.warning(f"Could not log response: {e}")
        logger.info(
            f"🌐 {timestamp} | {client_ip} | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Time: {process_time:.3f}s"
        )

    return response


# Routers
app.include_router(images.router, prefix="/images", tags=["Images"])
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(users.router, prefix="/users", tags=["Users"])


def custom_openapi():
    if not app.openapi_schema:
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        for path, methods in openapi_schema.get("paths", {}).items():
            for method, operation in methods.items():
                responses = operation.get("responses", {})
                if "422" in responses:
                    del responses["422"]

        app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
