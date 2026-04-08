from enum import StrEnum


class InvitationType(StrEnum):
    INVITE_PATIENT = "invite_patient"
    INVITE_CAREGIVER = "invite_caregiver"


class InvitationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"
