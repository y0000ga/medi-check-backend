from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


DATABASE_URL = "sqlite:///./app.db"

# 建立 SQLAlchemy 的資料庫連線引擎 engine -> 整個 app 連到 DB 的總入
engine = create_engine(  # 建立 SQLAlchemy 和資料庫溝通的核心物件
    # 資料庫位址
    DATABASE_URL,
    # 代表把實際執行的 SQL 印到 console
    # Prod 時要改掉
    echo=True,
)

# 建立一個「Session 工廠」
SessionLocal = sessionmaker(  # 產生 session 的設定器
    # 之後產生的 session 都要連到剛剛那個 engine
    bind=engine,
    # SQLAlchemy 不會在每次查詢前自動把暫存變更送去 DB，會更明確地自己控制 flush() / commit()
    autoflush=False,
    # 不會每做一件事就自動 commit，要自己寫 db.commit()
    autocommit=False,
)

# 每次 API request 來時，提供一個可用的 DB session
# 定義一個 FastAPI dependency function
def get_db():
    db: Session = SessionLocal() # 真正要拿 session
    # 把 db 提供給 route 使用，等 route 執行完，再回來執行 finally
    try:
        yield db #就是把這個 session 借給這次 request 用
    finally:
        db.close()


# 每次 request 來時：
# 開一個 db session
# 交給 route 用
# route 結束後自動關掉