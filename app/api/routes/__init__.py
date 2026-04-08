from app.api.routes.auth import router as auth_router
from app.api.routes.care_relationship import router as care_relationship_router
from app.api.routes.medication import router as medication_router
from app.api.routes.patient import router as patient_router
from app.api.routes.user import router as user_router

__all__ = [
    "auth_router",
    "care_relationship_router",
    "medication_router",
    "patient_router",
    "user_router",
]
