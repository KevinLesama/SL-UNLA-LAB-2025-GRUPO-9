from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

# 1. URL de la base de datos
DATABASE_URL = "sqlite:///mi_base.bd"

# 2. Crear el motor de conexión (engine)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. Crear la fábrica de sesiones
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