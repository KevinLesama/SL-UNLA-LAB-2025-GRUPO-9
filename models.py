from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Persona(Base):
    tablename="personas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(Integer)
    nombre = Column(String)
    email = Column(String)
    telefono = Column(String)
    fecha_de_nacimiento = Column(String)
    habilitado = Column(String, default="si")

class Turnos(Base):
    tablename="turnos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(String)
    hora = Column(String)
    estado = Column(String, default="pendiente")
    persona_id = Column(Integer , ForeignKey('persona.id'))



