import uuid
from datetime import datetime, UTC
from sqlalchemy import String, Boolean, DateTime, Enum, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.core.enums.user import UserStatus


from app.db.base import Base


# 定義 DB 的 User 使用者資料
class User(Base):
    __tablename__ = "users"

    # userID
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        # primary_key 是什麼意思 -> 代表 table 主 key，必然唯一值
        primary_key=True,
        default=uuid.uuid4,
    )

    # 使用者名稱 - 最多 100 字
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 使用者 Email
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        # 概念方向是「查詢會更快」，但 O(N) 這句不準。索引不是因為資料先被排序所以變成 O(N)；
        # 實際上索引通常是為了避免整張表掃描，查詢成本通常比全表掃描更低。
        # 你這裡只要記得一句就夠了：email 常拿來查使用者，所以很適合加 index。再加上你有 unique=True，資料庫也常會建立唯一索引。
        index=True,
    )
    # 經過加密的使用者密碼
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # 使用者圖片 (之後要考慮 Storage 的問題)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Email 是否認證 (之後再做 Email 認證的功能)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    # 使用者帳號狀態
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False
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
