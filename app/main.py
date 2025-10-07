from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.routers import images, items, users
import os
from dotenv import load_dotenv

load_dotenv()

name = os.getenv("NAME", "DotScan API Backend")
version = os.getenv("VERSION", "1.0.0")
description = os.getenv("DESCRIPTION", "Api for DotScan")

app = FastAPI(
    title=name,
    version=version,
    description=description,
)

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
