from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

# 把 service 裡重複的 transaction 寫法包起來
# contextmanager -> 讓這個 function 可以被 with ...: 使用。
@contextmanager
def db_transaction(db: Session) -> Iterator[None]:
    try:
        # with 區塊真正執行的地方
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise
