import os
import time
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from app.routers import images, items, users
from app.core.utils import error_response
from dotenv import load_dotenv
from datetime import datetime


class LevelColorFormatter(logging.Formatter):
    """Formateador que colorea los niveles de logging"""

    LEVEL_COLORS = {
        "DEBUG": "\033[46m\033[97m",
        "INFO": "\033[44m\033[97m",
        "WARNING": "\033[43m\033[97m",
        "ERROR": "\033[41m\033[97m",
        "CRITICAL": "\033[45m\033[97m",
        "RESET": "\033[0m",
    }

    def format(self, record):
        # Aplicar color solo al nivel del log
        level_color = self.LEVEL_COLORS.get(record.levelname, self.LEVEL_COLORS["INFO"])

        # Formato: [NIVEL] mensaje
        colored_level = f"{level_color}[{record.levelname}]{self.LEVEL_COLORS['RESET']}"
        record.msg = f"{colored_level} {record.msg}"

        return super().format(record)


def setup_complete_logging():
    """Configurar TODOS los loggers de Uvicorn"""
    uvicorn_loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "uvicorn.asgi",
        "uvicorn.server",
    ]

    for logger_name in uvicorn_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(LevelColorFormatter("%(message)s"))
        logger.addHandler(handler)

        # Propagar=False para evitar duplicados
        logger.propagate = False


setup_complete_logging()

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

        if response.status_code >= 400:
            logger.error(
                f"🌐 {timestamp} | {client_ip} | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | Time: {process_time:.3f}s"
            )
            logger.error(f"📦 Response Body: {body_preview}")
        else:
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
