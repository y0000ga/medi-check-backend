import uuid

from sqlalchemy.orm import Session
from sqlalchemy import delete, func, select
from app.core.enums.medication import DosageForm
from app.core.validation_rules import (
    MEDICATION_NAME_MAX_LENGTH,
    MEDICATION_NAME_MIN_LENGTH,
)
from app.models import Medication
from app.repositories.helpers import apply_pagination, apply_sort_order
from app.schemas.medication import ListMedicationQuery
from app.core.validators import validate_optional_string_field


def _get_order_column(query: ListMedicationQuery):
    if query.sort_by == "updated_at":
        return Medication.updated_at
    if query.sort_by == "dosage_form":
        return Medication.dosage_form
    if query.sort_by == "name":
        return Medication.name
    if query.sort_by == "patient_id":
        return Medication.patient_id
    return Medication.created_at


def _build_list_stmt(query: ListMedicationQuery):
    stmt = select(Medication).where(
        Medication.patient_id == query.patient_id,
    )

    if query.dosage_form is not None:
        stmt = stmt.where(Medication.dosage_form == query.dosage_form)

    normalized_name = validate_optional_string_field(
        field_name="name",
        value=query.name,
        max_length=MEDICATION_NAME_MAX_LENGTH,
        min_length=MEDICATION_NAME_MIN_LENGTH,
        trim=True,
        empty_as_none=True,
    )

    if normalized_name is not None:
        stmt = stmt.where(Medication.name.ilike(f"%{normalized_name}%"))

    return stmt


def list_medications(db: Session, query: ListMedicationQuery) -> list[Medication]:
    stmt = _build_list_stmt(query=query)
    order_column = _get_order_column(query)
    stmt = apply_pagination(stmt=stmt, page=query.page, page_size=query.page_size)
    stmt = apply_sort_order(
        stmt=stmt, order_column=order_column, sort_order=query.sort_order
    )

    result = db.execute(stmt)
    return list(result.scalars().all())


def count_medications(db: Session, query: ListMedicationQuery) -> int:
    stmt = _build_list_stmt(query)
    # with_only_columns(func.count()) 代表查總數
    # order_by(None) 代表不排序
    stmt = stmt.with_only_columns(func.count()).order_by(None)

    return db.scalar(stmt) or 0


def get_medication_by_id(
    db: Session, medication_id: uuid.UUID
) -> Medication | None:
    stmt = select(Medication).where(
        Medication.id == medication_id
    )
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def create_medication(
    db: Session,
    patient_id: uuid.UUID,
    name: str,
    note: str | None,
    dosage_form: DosageForm,
) -> Medication:
    medication = Medication(
        patient_id=patient_id, name=name, note=note, dosage_form=dosage_form
    )

    db.add(medication)
    db.flush()
    return medication


def delete_medication_by_id(
    medication_id: uuid.UUID,
    db: Session,
) -> None:
    db.execute(
        delete(Medication).where(
            Medication.id == medication_id,
        )
    )

def edit_medication_by_id(
        medication_id:uuid.UUID,
        name:str|None,
        note: str | None,
        dosage_form: DosageForm | None
) -> None:
    return None
