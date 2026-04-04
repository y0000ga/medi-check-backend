from app.api.routes.auth import router as auth_router
from app.api.routes.user import router as user_router
from app.api.routes.patient import router as patient_router
from app.api.routes.care_relationhip import router as care_relationship_router

# Route 的用途
# 收 request
# 呼叫 service
# 回 response

# 統一匯出

__all__ = ["auth_router","user_router", "patient_router", "care_relationship_router"]
