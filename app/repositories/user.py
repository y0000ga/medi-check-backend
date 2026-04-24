import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from pydantic import EmailStr


def get_user_by_email(db: Session, email: EmailStr) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.scalar(select(User).where(User.id == user_id))


def create_user(db: Session, email: EmailStr, name: str, password_hash: str) -> User:
    user = User(
        email=email,
        name=name,
        password_hash=password_hash,
    )
    db.add(user)
    # 在 object 建立或 Flush 時，會可以拿到 id 值
    # 先把 SQL 送到 DB transaction 裡
    # 但還沒真正 commit
    # 讓 user.id 這種欄位穩定可用
    db.flush()
    return user
