import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models import User
from app.schemas.base import ApiResponse
from app.schemas.care_invitation import (
    AcceptCareInvitationPayload,
    AcceptCareInvitationResponse,
    CreateCareInvitationBody,
    CreateCareInvitationPayload,
    CreateCareInvitationResponse,
    DeclineCareInvitationPayload,
    DeclineCareInvitationResponse,
    ListCareInvitationPayload,
    ListCareInvitationQueryParams,
    ListCareInvitationResponse,
    RevokeCareInvitationPayload,
    RevokeCareInvitationResponse,
)
from app.services.care_invitation import (
    accept_invitation,
    add_care_invitation,
    decline_invitation,
    get_care_invitation_list,
    revoke_invitation,
)

router = APIRouter(prefix="/care-invitations", tags=["care-invitation"])


@router.get("")
def get_care_invitations(
    query: ListCareInvitationQueryParams = Depends(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ListCareInvitationResponse]:
    payload = ListCareInvitationPayload(
        page=query.page,
        page_size=query.page_size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
        user_id=user.id,
        user_email=user.email,
        direction=query.direction,
        status=query.status,
    )
    response = get_care_invitation_list(payload=payload, db=db)
    return success_response(response)


@router.post("")
def create_care_invitation(
    body: CreateCareInvitationBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[CreateCareInvitationResponse]:
    payload = CreateCareInvitationPayload(
        user_id=user.id,
        patient_id=body.patient_id,
        invitee_email=body.invitee_email,
        invitation_type=body.invitation_type,
        permission_level=body.permission_level,
    )
    response = add_care_invitation(payload=payload, db=db)
    return success_response(response)


@router.post("/{invitation_id}/revoke")
def revoke_care_invitation_route(
    invitation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[RevokeCareInvitationResponse]:
    payload = RevokeCareInvitationPayload(
        user_id=user.id,
        invitation_id=invitation_id,
    )
    response = revoke_invitation(payload=payload, db=db)
    return success_response(response)


@router.post("/{invitation_id}/decline")
def decline_care_invitation_route(
    invitation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[DeclineCareInvitationResponse]:
    payload = DeclineCareInvitationPayload(
        user_id=user.id,
        user_email=user.email,
        invitation_id=invitation_id,
    )
    response = decline_invitation(payload=payload, db=db)
    return success_response(response)


@router.post("/{invitation_id}/accept")
def accept_care_invitation_route(
    invitation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[AcceptCareInvitationResponse]:
    payload = AcceptCareInvitationPayload(
        user_id=user.id,
        user_email=user.email,
        invitation_id=invitation_id,
    )
    response = accept_invitation(payload=payload, db=db)
    return success_response(response)
