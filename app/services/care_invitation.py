import uuid

from sqlalchemy.orm import Session

from app.core.enums.care_invitaion import InvitationStatus, InvitationType
from app.models.care_invitation import CareInvitation
from app.repositories.care_invitation import (
    accept_care_invitation,
    count_care_invitations,
    create_care_invitation,
    decline_care_invitation,
    get_care_invitation_by_id,
    get_pending_care_invitation,
    get_pending_care_invitation_for_relationship,
    list_care_invitations,
    revoke_care_invitation,
)
from app.repositories.care_relationship import (
    add_care_relationship,
    get_active_care_relationship,
)
from app.repositories.patient import get_patient_by_user_id
from app.repositories.user import get_user_by_email
from app.schemas.care_invitation import (
    AcceptCareInvitationPayload,
    AcceptCareInvitationResponse,
    CareInvitationResponse,
    CreateCareInvitationPayload,
    CreateCareInvitationResponse,
    DeclineCareInvitationPayload,
    DeclineCareInvitationResponse,
    ListCareInvitationPayload,
    ListCareInvitationResponse,
    RevokeCareInvitationPayload,
    RevokeCareInvitationResponse,
)
from app.schemas.care_relationship import DetailCareRelationshipQuery
from app.services.errors.care_invitation import (
    cannot_invite_self_error,
    care_invitation_access_denied_error,
    care_invitation_not_pending_error,
    care_invitation_relationship_already_exists_error,
    care_relationship_already_exists_for_create_error,
    invite_caregiver_patient_id_required_error,
    invite_patient_patient_id_not_allowed_error,
    invitee_patient_not_found_error,
    invitee_user_not_found_error,
    inviter_patient_not_found_error,
    pending_care_invitation_already_exists_error,
)
from app.services.transactions import db_transaction


def _build_care_invitation_response(
    invitation: CareInvitation,
    inviter_name: str,
    invitee_name: str | None,
) -> CareInvitationResponse:
    return CareInvitationResponse(
        id=invitation.id,
        inviter_user_id=invitation.inviter_user_id,
        inviter_name=inviter_name,
        patient_id=invitation.patient_id,
        invitee_email=invitation.invitee_email,
        invitee_user_id=invitation.invitee_user_id,
        invitee_name=invitee_name,
        invitation_type=invitation.invitation_type,
        permission_level=invitation.permission_level,
        status=invitation.status,
        sent_at=invitation.sent_at,
        accepted_at=invitation.accepted_at,
        declined_at=invitation.declined_at,
        revoked_at=invitation.revoked_at,
        expired_at=invitation.expired_at,
    )


def get_care_invitation_list(
    *,
    payload: ListCareInvitationPayload,
    db: Session,
) -> ListCareInvitationResponse:
    rows = list_care_invitations(db=db, query=payload)
    total_size = count_care_invitations(db=db, query=payload)
    return ListCareInvitationResponse(
        page=payload.page,
        total_size=total_size,
        list=[
            _build_care_invitation_response(invitation, inviter_name, invitee_name)
            for invitation, inviter_name, invitee_name in rows
        ],
    )


def _create_care_invitation(
    *,
    payload: CreateCareInvitationPayload,
    db: Session,
) -> CreateCareInvitationResponse:
    pending_invitation = get_pending_care_invitation(
        db=db,
        inviter_user_id=payload.user_id,
        patient_id=payload.patient_id,
        invitee_email=payload.invitee_email,
        invitation_type=payload.invitation_type,
    )
    if pending_invitation is not None:
        raise pending_care_invitation_already_exists_error()

    with db_transaction(db):
        invitation = create_care_invitation(
            db=db,
            inviter_user_id=payload.user_id,
            patient_id=payload.patient_id,
            invitee_email=payload.invitee_email,
            invitation_type=payload.invitation_type,
            permission_level=payload.permission_level,
        )

    db.refresh(invitation)
    return CreateCareInvitationResponse(id=invitation.id)


def _ensure_not_inviting_self(
    *,
    inviter_user_id: uuid.UUID,
    invitee_user_id: uuid.UUID,
) -> None:
    if inviter_user_id == invitee_user_id:
        raise cannot_invite_self_error()


def _ensure_no_active_relationship_on_create(
    *,
    caregiver_user_id: uuid.UUID,
    patient_id: uuid.UUID,
    db: Session,
) -> None:
    existing_relationship = get_active_care_relationship(
        db=db,
        query=DetailCareRelationshipQuery(
            caregiver_user_id=caregiver_user_id,
            patient_id=patient_id,
        ),
    )
    if existing_relationship is not None:
        raise care_relationship_already_exists_for_create_error()


def _ensure_no_pending_invitation_for_relationship(
    *,
    caregiver_user_id: uuid.UUID,
    patient_id: uuid.UUID,
    db: Session,
) -> None:
    existing_invitation = get_pending_care_invitation_for_relationship(
        db=db,
        caregiver_user_id=caregiver_user_id,
        patient_id=patient_id,
    )
    if existing_invitation is not None:
        raise pending_care_invitation_already_exists_error()


def _add_invite_patient(
    *,
    payload: CreateCareInvitationPayload,
    db: Session,
) -> CreateCareInvitationResponse:
    if payload.patient_id is not None:
        raise invite_patient_patient_id_not_allowed_error()

    invitee_user = get_user_by_email(db=db, email=payload.invitee_email)
    if invitee_user is None:
        raise invitee_user_not_found_error()

    _ensure_not_inviting_self(
        inviter_user_id=payload.user_id,
        invitee_user_id=invitee_user.id,
    )

    invitee_patient = get_patient_by_user_id(db=db, user_id=invitee_user.id)
    if invitee_patient is None:
        raise invitee_patient_not_found_error()

    _ensure_no_active_relationship_on_create(
        caregiver_user_id=payload.user_id,
        patient_id=invitee_patient.id,
        db=db,
    )
    _ensure_no_pending_invitation_for_relationship(
        caregiver_user_id=payload.user_id,
        patient_id=invitee_patient.id,
        db=db,
    )

    return _create_care_invitation(payload=payload, db=db)


def _add_invite_caregiver(
    *,
    payload: CreateCareInvitationPayload,
    db: Session,
) -> CreateCareInvitationResponse:
    invitee_user = get_user_by_email(db=db, email=payload.invitee_email)
    if invitee_user is None:
        raise invitee_user_not_found_error()

    _ensure_not_inviting_self(
        inviter_user_id=payload.user_id,
        invitee_user_id=invitee_user.id,
    )

    inviter_patient = get_patient_by_user_id(db=db, user_id=payload.user_id)
    if inviter_patient is None:
        raise inviter_patient_not_found_error()

    patient_id = inviter_patient.id

    _ensure_no_active_relationship_on_create(
        caregiver_user_id=invitee_user.id,
        patient_id=patient_id,
        db=db,
    )
    _ensure_no_pending_invitation_for_relationship(
        caregiver_user_id=invitee_user.id,
        patient_id=patient_id,
        db=db,
    )

    return _create_care_invitation(
        payload=payload.model_copy(update={"patient_id": patient_id}),
        db=db,
    )


def add_patient_invitation(
    *,
    payload: CreateCareInvitationPayload,
    db: Session,
) -> CreateCareInvitationResponse:
    return _add_invite_patient(
        payload=payload.model_copy(
            update={"invitation_type": InvitationType.INVITE_PATIENT}
        ),
        db=db,
    )


def add_caregiver_invitation(
    *,
    payload: CreateCareInvitationPayload,
    db: Session,
) -> CreateCareInvitationResponse:
    return _add_invite_caregiver(
        payload=payload.model_copy(
            update={"invitation_type": InvitationType.INVITE_CAREGIVER}
        ),
        db=db,
    )


def revoke_invitation(
    *,
    payload: RevokeCareInvitationPayload,
    db: Session,
) -> RevokeCareInvitationResponse:
    invitation = get_care_invitation_by_id(db=db, invitation_id=payload.invitation_id)
    if invitation is None or invitation.inviter_user_id != payload.user_id:
        raise care_invitation_access_denied_error()

    if invitation.status != InvitationStatus.PENDING:
        raise care_invitation_not_pending_error()

    with db_transaction(db):
        revoke_care_invitation(invitation=invitation)

    db.refresh(invitation)
    return RevokeCareInvitationResponse(id=invitation.id)


def decline_invitation(
    *,
    payload: DeclineCareInvitationPayload,
    db: Session,
) -> DeclineCareInvitationResponse:
    invitation = get_care_invitation_by_id(db=db, invitation_id=payload.invitation_id)
    if invitation is None:
        raise care_invitation_access_denied_error()

    can_decline = (
        invitation.invitee_user_id == payload.user_id
        or invitation.invitee_email == payload.user_email
    )
    if not can_decline:
        raise care_invitation_access_denied_error()

    if invitation.status != InvitationStatus.PENDING:
        raise care_invitation_not_pending_error()

    with db_transaction(db):
        decline_care_invitation(invitation=invitation)

    db.refresh(invitation)
    return DeclineCareInvitationResponse(id=invitation.id)


def accept_invitation(
    *,
    payload: AcceptCareInvitationPayload,
    db: Session,
) -> AcceptCareInvitationResponse:
    invitation = get_care_invitation_by_id(db=db, invitation_id=payload.invitation_id)
    if invitation is None:
        raise care_invitation_access_denied_error()

    can_accept = (
        invitation.invitee_user_id == payload.user_id
        or invitation.invitee_email == payload.user_email
    )
    if not can_accept:
        raise care_invitation_access_denied_error()

    if invitation.status != InvitationStatus.PENDING:
        raise care_invitation_not_pending_error()

    if invitation.invitation_type == InvitationType.INVITE_PATIENT:
        patient = get_patient_by_user_id(db=db, user_id=payload.user_id)
        if patient is None:
            raise invitee_patient_not_found_error()

        caregiver_user_id = invitation.inviter_user_id
        patient_id = patient.id
    else:
        patient_id = invitation.patient_id
        if patient_id is None:
            raise invite_caregiver_patient_id_required_error()
        caregiver_user_id = payload.user_id

    existing_relationship = get_active_care_relationship(
        db=db,
        query=DetailCareRelationshipQuery(
            caregiver_user_id=caregiver_user_id,
            patient_id=patient_id,
        ),
    )
    if existing_relationship is not None:
        raise care_invitation_relationship_already_exists_error()

    with db_transaction(db):
        add_care_relationship(
            db=db,
            caregiver_user_id=caregiver_user_id,
            created_by_user_id=invitation.inviter_user_id,
            patient_id=patient_id,
            invitation_id=invitation.id,
            permission_level=invitation.permission_level,
        )
        accept_care_invitation(invitation=invitation)

    db.refresh(invitation)
    return AcceptCareInvitationResponse(id=invitation.id)
