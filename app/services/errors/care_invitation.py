from app.core.exceptions import AppException
from app.schemas.base import ValidationErrorDetail


def care_invitation_access_denied_error() -> AppException:
    return AppException(
        status_code=401,
        message="Cannot access CareInvitation",
    )


def invitee_user_not_found_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="invitee_email",
                message="Invitee must already have an account",
                type="not_found",
            )
        ],
    )


def pending_care_invitation_already_exists_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="invitee_email",
                message="A pending invitation already exists for this invitee",
                type="duplicate",
            )
        ],
    )


def care_invitation_not_pending_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="invitation_id",
                message="Only pending invitations can be updated",
                type="invalid",
            )
        ],
    )


def invite_caregiver_patient_id_required_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="patient_id",
                message="patient_id is required when invitation_type is invite_caregiver",
                type="required",
            )
        ],
    )


def invite_patient_patient_id_not_allowed_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="patient_id",
                message="patient_id is not allowed when invitation_type is invite_patient",
                type="invalid",
            )
        ],
    )


def care_invitation_relationship_already_exists_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="invitation_id",
                message="A care relationship already exists for this invitation target",
                type="duplicate",
            )
        ],
    )


def invitee_patient_not_found_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="invitation_id",
                message="Invitee does not have a patient profile",
                type="not_found",
            )
        ],
    )


def cannot_invite_self_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="invitee_email",
                message="You cannot invite yourself",
                type="invalid",
            )
        ],
    )


def care_relationship_already_exists_for_create_error() -> AppException:
    return AppException(
        status_code=400,
        message="Request validation failed",
        details=[
            ValidationErrorDetail(
                field="invitee_email",
                message="An active care relationship already exists",
                type="duplicate",
            )
        ],
    )
