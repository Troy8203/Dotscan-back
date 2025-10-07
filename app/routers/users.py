from fastapi import APIRouter

router = APIRouter()

users_db = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

@router.get("/")
async def get_users():
    return users_db