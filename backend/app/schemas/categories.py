from pydantic import BaseModel
from typing import List, Optional
from .items import ItemRead as ItemSchema

class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    selectable: bool = True

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    order: int
    items: List[ItemSchema] = []
    children: List['Category'] = []

    class Config:
        from_attributes = True

Category.update_forward_refs()