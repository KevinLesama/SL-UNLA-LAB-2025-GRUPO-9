from sqlalchemy import Column, Integer, String
from database import Base

class Persona(Base):
    tablename="personas"
    dni = Column(Integer, primary_key=True)
    nombre = Column(String)
    email = Column(String)
    telefono = Column(String)
    fecha_de_nacimiento = Column(String)
    habilitado = Column(String, default="si")




