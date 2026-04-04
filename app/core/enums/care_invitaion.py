from enum import StrEnum


class InviteeRole(StrEnum):
    PATIENT = "patient"
    CAREGIVER = "caregiver"

class InvitationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"