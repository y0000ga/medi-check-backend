from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    auth_router,
    user_router,
    patient_router,
    care_relationship_router,
)
from app.core.exception_handlers import register_exception_handlers

app = FastAPI(title="Medi-Check-Backend", version="0.1.0")

register_exception_handlers(app)

# CORS 問題
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    ],
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
app.include_router(care_relationship_router)
