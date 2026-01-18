from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def check_status():
    return {"status": "healthy"}
