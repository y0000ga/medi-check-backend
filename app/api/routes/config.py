from fastapi import APIRouter
from app.validation.metadata import get_validation_metadata

router = APIRouter(prefix="/app-config", tags=["config"])

@router.get("/validation")
def get_validation():
    return get_validation_metadata()