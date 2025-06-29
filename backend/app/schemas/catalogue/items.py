from typing import List
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float

class ItemCreate(ItemBase):
    category_ids: List[int] = []

class ItemRead(ItemBase):
    id: int
    categories: List[int]

    @staticmethod
    def from_orm_with_categories(item_orm):
        return ItemRead(
            id=item_orm.id,
            name=item_orm.name,
            description=item_orm.description,
            price=item_orm.price,
            categories=[cat.id for cat in getattr(item_orm, 'categories', [])]
        )

    class Config:
        from_attributes = True