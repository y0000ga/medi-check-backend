from fastapi import APIRouter, Depends

from app.core.response import success_response
from app.dependencies.user import get_current_user
from app.models.user import User
from app.schemas.base import ApiResponse


router = APIRouter(prefix="/medication", tags=["medication"])

@router.get('/list')
def get_medications(user:User = Depends(get_current_user)) -> ApiResponse[None]:
    return success_response(None)