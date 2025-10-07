from app.schemas.item import ItemCreate

items_db = []

def get_items_service():
    return items_db

def create_item_service(item: ItemCreate):
    new_item = item.dict()
    new_item["id"] = len(items_db) + 1
    items_db.append(new_item)
    return new_item

def get_item_service(item_id: int):
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise ValueError("Item not found")

def update_item_service(item_id: int, updated_item: ItemCreate):
    for item in items_db:
        if item["id"] == item_id:
            item.update(updated_item.dict())
            return item
    raise ValueError("Item not found")

def delete_item_service(item_id: int):
    for index, item in enumerate(items_db):
        if item["id"] == item_id:
            items_db.pop(index)
            return {"message": "Item deleted"}
    raise ValueError("Item not found")
