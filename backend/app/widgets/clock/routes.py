from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_clock_widget():
    return {"message": "Clock widget endpoint"}
