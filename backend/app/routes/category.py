from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models.category import Category
from app.schemas.categories import Category as CategorySchema, CategoryCreate
from app.routes.deps import get_current_admin_user
from app.db.models.users import User

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

class CategoryReorderItem(BaseModel):
    id: int
    parent_id: Optional[int] = None
    order: Optional[int] = None

@router.post("/", response_model=CategorySchema)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Create a new category."""
    if db.query(Category).filter(Category.name == category.name).first():
        raise HTTPException(status_code=400, detail="Category name must be unique")
    max_order = db.query(Category).filter(Category.parent_id == category.parent_id).order_by(Category.order.desc()).first()
    next_order = (max_order.order + 1) if max_order and max_order.order is not None else 0
    db_category = Category(
        name=category.name,
        parent_id=category.parent_id,
        selectable=category.selectable,
        order=next_order
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[CategorySchema])
def read_categories(db: Session = Depends(get_db)):
    """Return all categories ordered by parent and order."""
    return db.query(Category).order_by(Category.parent_id, Category.order).all()

@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Update a category by ID."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    if db.query(Category).filter(Category.name == category.name, Category.id != category_id).first():
        raise HTTPException(status_code=400, detail="Category name must be unique")
    db_category.name = category.name
    db_category.parent_id = category.parent_id
    db_category.selectable = category.selectable
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Delete a category by ID."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()

@router.post("/reorder", status_code=204)
def reorder_categories(
    categories: List[CategoryReorderItem] = Body(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Reorder categories based on drag-and-drop from the frontend."""
    cat_map = {item.id: item for item in categories}
    db_categories = db.query(Category).all()
    for db_category in db_categories:
        item = cat_map.get(db_category.id)
        if item is not None:
            db_category.parent_id = item.parent_id
            db_category.order = item.order
    db.commit()