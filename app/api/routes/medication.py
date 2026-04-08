import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models import User
from app.schemas.base import ApiResponse
from app.schemas.medication import (
    CreateMedicationPayload,
    CreateMedicationBody,
    CreateMedicationResponse,
    DeleteMedicationPayload,
    DetailMedicationPayload,
    EditMedicationBody,
    EditMedicationPayload,
    EditMedicationResponse,
    ListMedicationPayload,
    ListMedicationQueryParams,
    ListMedicationResponse,
    MedicationDetailResponse,
)
from app.services.medication import (
    add_medication,
    delete_medication,
    get_medication_detail,
    get_medication_list,
    update_medication,
)


router = APIRouter(tags=["medication"])


# 取得藥物列表
@router.get("/patients/{patient_id}/medications")
def get_medications(
    patient_id: uuid.UUID,
    query: ListMedicationQueryParams = Depends(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ListMedicationResponse]:

    payload = ListMedicationPayload(
        user_id=user.id,
        dosage_form=query.dosage_form,
        patient_id=patient_id,
        name=query.name,
        page=query.page,
        page_size=query.page_size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
    )

    response = get_medication_list(db=db, payload=payload)
    return success_response(response)


# 取得個別藥物資訊
@router.get("/medications/{medication_id}")
def get_medication(
    medication_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[MedicationDetailResponse]:

    payload = DetailMedicationPayload(
        user_id=user.id,
        medication_id=medication_id,
    )

    response = get_medication_detail(payload=payload, db=db)
    return success_response(response)


# 新增藥物
@router.post("/patients/{patient_id}/medications")
def create_medication(
    patient_id: uuid.UUID,
    body: CreateMedicationBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[CreateMedicationResponse]:
    payload = CreateMedicationPayload(
        user_id=user.id,
        dosage_form=body.dosage_form,
        patient_id=patient_id,
        name=body.name,
        note=body.note,
    )

    response = add_medication(payload=payload, db=db)

    return success_response(response)


@router.patch("/medications/{medication_id}")
def edit_medication(
    medication_id: uuid.UUID,
    body: EditMedicationBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[EditMedicationResponse]:
    payload = EditMedicationPayload(
        **body.model_dump(exclude_unset=True),
        medication_id=medication_id,
        user_id=user.id,
    )
    response = update_medication(payload=payload, db=db)
    return success_response(response)


# 刪除特定藥品
@router.delete("/medications/{medication_id}")
def remove_medication(
    medication_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[None]:
    payload = DeleteMedicationPayload(user_id=user.id, medication_id=medication_id)
    delete_medication(payload=payload, db=db)
    return success_response(None)
