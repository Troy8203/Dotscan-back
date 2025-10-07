from fastapi import FastAPI
from app.routers import items, users

app = FastAPI(title="My FastAPI Project")

# Routers
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(users.router, prefix="/users", tags=["Users"])