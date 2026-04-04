from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models.user import User
from app.schemas.base import ApiResponse
from app.schemas.patient import (
    ListPatientsPayload,
    ListPatientsRequest,
    ListPatientsResponse,
)
from app.services.patient import get_patients_list

router = APIRouter(prefix="/patient", tags=["patient"])


@router.get("/list")
def get_patients(
    request_data: ListPatientsRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ListPatientsResponse]:
    payload = ListPatientsPayload(
        page=request_data.page,
        page_size=request_data.page_size,
        user_id=user.id,
    )
    result = get_patients_list(payload=payload, db=db)
    return success_response(result)


@router.get("detail")
def get_patient_detail():
    return success_response(None)
