from fastapi import APIRouter, HTTPException
from app.schemas.item import Item, ItemCreate
from app.services.item_service import get_items_service, create_item_service, get_item_service, update_item_service, delete_item_service

router = APIRouter()

@router.get("/", response_model=list[Item])
async def get_items():
    return get_items_service()

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate):
    return create_item_service(item)

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    return get_item_service(item_id)

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    return update_item_service(item_id, item)

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    return delete_item_service(item_id)
