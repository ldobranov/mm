from pydantic import BaseModel
from typing import List, Dict, Any

class Settings(BaseModel):
    languages: List[str]
    siteName: Dict[str, str]
    siteContent: Dict[str, str]
    menu: list

    class Config:
        orm_mode = True
