import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models import User
from app.schemas.base import ApiResponse
from app.schemas.history import (
    DetailHistoryPayload,
    EditHistoryBody,
    EditHistoryPayload,
    EditHistoryResponse,
    HistoryDetailResponse,
    ListHistoriesPayload,
    ListHistoriesQueryParams,
    ListHistoriesResponse,
    QuickCheckHistoryBody,
    QuickCheckHistoryPayload,
    QuickCheckHistoryResponse,
)
from app.services.history import (
    get_history_detail,
    get_history_list,
    add_quick_check_history,
    update_history,
)

router = APIRouter(tags=['history'])


@router.get("/histories")
def get_histories(
    query: ListHistoriesQueryParams = Depends(),
    patient_ids: list[uuid.UUID] | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ListHistoriesResponse]:
    """List histories visible to the current user."""
    payload = ListHistoriesPayload(
        page=query.page,
        page_size=query.page_size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
        user_id=user.id,
        patient_ids=patient_ids,
        medication_id=query.medication_id,
        status=query.status,
        from_date=query.from_date,
        to_date=query.to_date,
    )
    response = get_history_list(db=db, payload=payload)
    return success_response(response)


@router.get("/histories/{history_id}")
def get_history(
    history_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[HistoryDetailResponse]:
    """Get a single history detail."""
    payload = DetailHistoryPayload(user_id=user.id, history_id=history_id)
    response = get_history_detail(db=db, payload=payload)
    return success_response(response)


@router.post("/histories/quick-check")
def quick_check_history(
    body: QuickCheckHistoryBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[QuickCheckHistoryResponse]:
    """Create a taken history from a matching schedule event."""
    payload = QuickCheckHistoryPayload(**body.model_dump(), user_id=user.id)
    response = add_quick_check_history(db=db, payload=payload)
    return success_response(response)


@router.patch("/histories/{history_id}")
def edit_history(
    history_id: uuid.UUID,
    body: EditHistoryBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[EditHistoryResponse]:
    """Update a history and mark intake_at edits as manual."""
    payload = EditHistoryPayload(
        **body.model_dump(exclude_unset=True),
        user_id=user.id,
        history_id=history_id,
    )
    response = update_history(db=db, payload=payload)
    return success_response(response)
