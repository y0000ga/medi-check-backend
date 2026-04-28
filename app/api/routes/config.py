from fastapi import APIRouter
from app.validation.metadata import get_validation_metadata
from app.core.response import success_response

router = APIRouter(prefix="/app-config", tags=["config"])

@router.get("/validation")
def get_validation():
    return success_response(get_validation_metadata())