from app.api.routes.auth import router as auth_router
from app.api.routes.care_invitation import router as care_invitation_router
from app.api.routes.care_relationship import router as care_relationship_router
from app.api.routes.history import router as history_router
from app.api.routes.medication import router as medication_router
from app.api.routes.patient import router as patient_router
from app.api.routes.schedule import router as schedule_router
from app.api.routes.user import router as user_router
from app.api.routes.config import router as config_router

__all__ = [
    "auth_router",
    "care_invitation_router",
    "care_relationship_router",
    "history_router",
    "medication_router",
    "patient_router",
    "schedule_router",
    "user_router",
    "config_router"
]
