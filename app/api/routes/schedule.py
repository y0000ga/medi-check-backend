import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models import User
from app.schemas.base import ApiResponse
from app.schemas.schedule import (
    CreateScheduleBody,
    CreateSchedulePayload,
    CreateScheduleResponse,
    DeleteSchedulePayload,
    DetailSchedulePayload,
    EditScheduleBody,
    EditSchedulePayload,
    EditScheduleResponse,
    ListScheduleMatchesPayload,
    ListScheduleMatchesQueryParams,
    ListScheduleMatchesResponse,
    ListSchedulesPayload,
    ListSchedulesQueryParams,
    ListSchedulesResponse,
    ScheduleDetailResponse,
)
from app.services.schedule import (
    add_schedule,
    delete_schedule,
    get_schedule_detail,
    get_schedule_list,
    get_schedule_match_list,
    update_schedule,
)

router = APIRouter(tags=["schedule"])


# 取得可存取的排程列表
@router.get("/schedules")
def get_schedules(
    query: ListSchedulesQueryParams = Depends(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ListSchedulesResponse]:
    payload = ListSchedulesPayload(
        page=query.page,
        page_size=query.page_size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
        user_id=user.id,
        patient_ids=query.patient_ids,
    )
    response = get_schedule_list(db=db, payload=payload)
    return success_response(response)


# 取得動態展開後的排程事件
@router.get("/schedule-matches")
def get_schedule_matches(
    query: ListScheduleMatchesQueryParams = Depends(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ListScheduleMatchesResponse]:
    payload = ListScheduleMatchesPayload(
        user_id=user.id,
        patient_ids=query.patient_ids,
        from_date=query.from_date,
        to_date=query.to_date,
    )
    response = get_schedule_match_list(db=db, payload=payload)
    return success_response(response)


# 取得單筆排程
@router.get("/schedules/{schedule_id}")
def get_schedule(
    schedule_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ScheduleDetailResponse]:
    payload = DetailSchedulePayload(user_id=user.id, schedule_id=schedule_id)
    response = get_schedule_detail(db=db, payload=payload)
    return success_response(response)


# 新增藥物排程
@router.post("/medications/{medication_id}/schedules")
def create_schedule(
    medication_id: uuid.UUID,
    body: CreateScheduleBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[CreateScheduleResponse]:
    payload = CreateSchedulePayload(
        **body.model_dump(),
        user_id=user.id,
        medication_id=medication_id,
    )

    response = add_schedule(db=db, payload=payload)
    return success_response(response)


# 修改單筆排程
@router.patch("/schedules/{schedule_id}")
def edit_schedule(
    schedule_id: uuid.UUID,
    body: EditScheduleBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[EditScheduleResponse]:
    payload = EditSchedulePayload(
        **body.model_dump(exclude_unset=True),
        user_id=user.id,
        schedule_id=schedule_id,
    )

    response = update_schedule(db=db, payload=payload)
    return success_response(response)


# 刪除單筆排程
@router.delete("/schedules/{schedule_id}")
def remove_schedule(
    schedule_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[None]:
    payload = DeleteSchedulePayload(user_id=user.id, schedule_id=schedule_id)
    delete_schedule(db=db, payload=payload)
    return success_response(None)
