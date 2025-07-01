from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_temp_widget():
    return {"message": "Temp widget endpoint"}
