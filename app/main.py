from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth_router,
    care_invitation_router,
    care_relationship_router,
    history_router,
    medication_router,
    patient_router,
    schedule_router,
    user_router,
    config_router
)
from app.core.exception_handlers import register_exception_handlers
from app.core.settings import get_settings

app = FastAPI(title="Medi-Check-Backend", version="0.1.0")

register_exception_handlers(app)

settings = get_settings()
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

# CORS 問題
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


# 掛上 API
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(care_invitation_router)
app.include_router(care_relationship_router)
app.include_router(history_router)
app.include_router(medication_router)
app.include_router(schedule_router)
app.include_router(config_router)
