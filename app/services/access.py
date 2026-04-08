from dataclasses import dataclass

from app.core.enums.care_relationship import PermissionLevel
from app.models import Medication, Patient


@dataclass(frozen=True)
class PatientAccess:
    patient: Patient
    permission_level: PermissionLevel


@dataclass(frozen=True)
class MedicationAccess:
    medication: Medication
    permission_level: PermissionLevel
