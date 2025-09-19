from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

class Persona(Base):
    tablename="personas"
    dni = Column(Integer, primary_key=True)
    nombre = Column(String)
    email = Column(String)
    telefono = Column(String)
    fecha_de_nacimiento = Column(String)
    habilitado = Column(String, default="si")




