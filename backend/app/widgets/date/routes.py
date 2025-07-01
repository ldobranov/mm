from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_date_widget():
    return {"message": "Date widget endpoint"}
