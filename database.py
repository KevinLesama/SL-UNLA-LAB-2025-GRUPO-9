from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings


DATABASE_URL = "sqlite:///mi_base.bd"


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()