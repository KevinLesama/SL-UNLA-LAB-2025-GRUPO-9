from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Configuración de la Base de Datos
    DATABASE_URL: str = "sqlite:///./mi_base.bd"

    # Estados de los turnos
    ESTADO_PENDIENTE: str = "pendiente"
    ESTADO_CONFIRMADO: str = "confirmado"
    ESTADO_CANCELADO: str = "cancelado"
    ESTADO_ASISTIDO: str = "asistido"

    # Horarios válidos para los turnos
    HORARIOS_VALIDOS: List[str] = [
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", 
        "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00"
    ]

    class Config:
        env_file = ".env"

# Crear una única instancia de la configuración para ser usada en toda la app
settings = Settings()