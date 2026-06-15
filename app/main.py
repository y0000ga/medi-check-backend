from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth_router,
    care_invitation_router,
    care_relationship_router,
    config_router,
    history_router,
    medication_router,
    patient_router,
    schedule_router,
    user_router,
)
from app.core.exception_handlers import register_exception_handlers
from app.core.settings import get_settings
from app.db.session import ping_db

app = FastAPI(title="Medi-Check-Backend", version="0.1.0")

register_exception_handlers(app)

settings = get_settings()
cors_origins = settings.cors_origins_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/live")
def health_live():
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    db_ok = ping_db()
    return {"status": "ok" if db_ok else "degraded", "db": db_ok}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(care_invitation_router)
app.include_router(care_relationship_router)
app.include_router(history_router)
app.include_router(medication_router)
app.include_router(schedule_router)
app.include_router(config_router)
