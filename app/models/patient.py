import uuid

from app.db.base import Base
from app.validation.rules import AVATAR_URL_RULE, NAME_RULE

from datetime import datetime, UTC
from sqlalchemy import Uuid, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column


# 病人身分資料
class Patient(Base):
    __tablename__ = "patients"

    # patient ID
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    # 病人本人綁定的 user account id -> 但有些病人其實沒有登入使用該 APP，所以可能由照顧者自行建立
    # 所以為空也是很正常的
    linked_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True, unique=True
    )
    # 病人名稱 # 如果有 linked_user_id 就接他的
    name: Mapped[str] = mapped_column(String(NAME_RULE["max_length"]), nullable=False)

    # 病人生日 # 如果有 linked_user_id 就接他的
    birth_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 病人圖片 (之後要考慮 Storage 的問題)
    avatar_url: Mapped[str | None] = mapped_column(
        String(AVATAR_URL_RULE["max_length"]), nullable=True
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
