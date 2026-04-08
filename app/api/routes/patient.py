import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models import User
from app.schemas.base import ApiResponse
from app.schemas.patient import (
    CreatePatientBody,
    CreatePatientPayload,
    CreatePatientResponse,
    DetailPatientPayload,
    DetailPatientResponse,
    ListPatientsPayload,
    ListPatientsQueryParams,
    ListPatientsResponse,
)
from app.services.patient import add_new_patient, get_patient_detail, get_patient_list

router = APIRouter(prefix="/patients", tags=["patient"])


# 取得對應病人列表
@router.get("")
def get_patients(
    query: ListPatientsQueryParams = Depends(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ListPatientsResponse]:
    payload = ListPatientsPayload(
        page=query.page,
        page_size=query.page_size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
        user_id=user.id,
    )
    result = get_patient_list(payload=payload, db=db)
    return success_response(result)


# 取得病人詳細資訊
@router.get("/{patient_id}")
def get_patient(
    patient_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[DetailPatientResponse]:
    payload = DetailPatientPayload(
        patient_id=patient_id,
        user_id=user.id,
    )
    result = get_patient_detail(payload=payload, db=db)
    return success_response(result)


@router.post("")
def create_patient(
    body: CreatePatientBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[CreatePatientResponse]:

    payload = CreatePatientPayload(
        email=body.email,
        name=body.name,
        avatar_url=body.avatar_url,
        user_id=user.id,
        birth_date=body.birth_date,
    )

    result = add_new_patient(db=db, payload=payload)

    return success_response(result)
