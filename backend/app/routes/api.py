from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.item import Item
from app.db.models.category import Category  # Import Category model
from app.schemas.catalogue.items import ItemCreate, ItemRead 

router = APIRouter(
    prefix="/api/v1/items",  # Add a prefix for all routes in this router
    tags=["Items"]           # Group these routes in OpenAPI documentation
)

@router.get("/health", tags=["Health"]) # Keep health check separate or move to a general router
async def health_check():
    return {"status": "healthy"}

@router.get("/", response_model=list[ItemRead]) # Path becomes relative to the prefix
def list_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return [ItemRead.from_orm_with_categories(item) for item in items]

@router.post("/", response_model=ItemRead) # Path becomes relative to the prefix
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(
        name=item.name,
        description=item.description,
        price=item.price
    )
    if item.category_ids:
        db_item.categories = db.query(Category).filter(Category.id.in_(item.category_ids)).all()
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return ItemRead.from_orm_with_categories(db_item)

@router.get("/{item_id}", response_model=ItemRead) # Path becomes relative to the prefix
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemRead.from_orm_with_categories(item)

@router.put("/{item_id}", response_model=ItemRead) # Path becomes relative to the prefix
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(Item).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.name
    db_item.description = item.description
    db_item.price = item.price
    db_item.categories = db.query(Category).filter(Category.id.in_(item.category_ids)).all() if item.category_ids else []
    db.commit()
    db.refresh(db_item)
    return ItemRead.from_orm_with_categories(db_item)

@router.delete("/{item_id}") # Path becomes relative to the prefix
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}