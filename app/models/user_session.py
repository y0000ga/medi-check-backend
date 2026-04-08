import uuid

from datetime import datetime, UTC

# ForeignKey 這個欄位參考另一張表的欄位
from sqlalchemy import ForeignKey, String, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.core.validation_rules import (
    IP_ADDRESS_MAX_LENGTH,
    REFRESH_TOKEN_HASH_MAX_LENGTH,
    USER_AGENT_MAX_LENGTH,
)

from app.db.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    # user_session ID
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        # primary_key 是什麼意思 -> 代表 table 主 key，必然唯一值
        primary_key=True,
        default=uuid.uuid4,
    )
    # 使用者可能用多個裝置登入，所以 user_id 可重複
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )

    # refresh token 識別碼
    token_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )

    # access token -> 後端登入成功後簽發給前端，前端暫存在記憶體、cookie 或 storage，之後每次打 API 時帶上它
    # 用來續約新通行證的憑證 -> 用來換新的 access token
    refresh_token_hash: Mapped[str] = mapped_column(
        String(REFRESH_TOKEN_HASH_MAX_LENGTH), nullable=False
    )
    # 使用者裝置 -> 通常從 request header 能拿到，但有些 client、測試、機器人、內部服務不一定會帶
    user_agent: Mapped[str | None] = mapped_column(
        String(USER_AGENT_MAX_LENGTH), nullable=True
    )
    # 使用者 IP -> 通常也能拿到，但如果有 proxy、load balancer、localhost、測試 client、某些部署方式，值可能缺失、格式不同，或你拿到的是 proxy IP
    ip_address: Mapped[str | None] = mapped_column(
        String(IP_ADDRESS_MAX_LENGTH), nullable=True
    )
    # 該登入行為過期時間
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # refresh_token 撤銷時間
    # 使用者登出
    # 某裝置被踢掉
    # refresh token 洩漏
    # 想做多裝置 session 管理
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # 創建時間
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    # 更新時間
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
