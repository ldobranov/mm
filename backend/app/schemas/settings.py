from pydantic import BaseModel, Field
from typing import Dict, List, Any

class MenuItemSchema(BaseModel):
    id: Any
    label: Dict[str, str]
    route: str
    visibility: str
    children: List['MenuItemSchema'] = []

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

MenuItemSchema.update_forward_refs()

class SettingsSchema(BaseModel):
    languages: List[str] = Field(default_factory=lambda: ["en"])
    siteName: Dict[str, str] = Field(default_factory=lambda: {"en": "Global Virtual Display"})
    siteContent: Dict[str, str] = Field(default_factory=dict)
    menu: List[MenuItemSchema] = Field(default_factory=list)
