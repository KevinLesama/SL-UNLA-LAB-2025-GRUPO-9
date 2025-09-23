from sqlalchemy import Column, Integer, String, ForeignKey, Date 
from sqlalchemy.orm import relationship
from base import Base

#Hecho por Nahuel Garcia
class Persona(Base):
    __tablename__ = "personas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(Integer)
    nombre = Column(String)
    email = Column(String)
    telefono = Column(Integer)
    fecha_de_nacimiento = Column(Date)
    habilitado = Column(String, default="si")
    turnos = relationship("Turnos", back_populates="persona")

#Hecho por Kevin Lesama Soto
class Turnos(Base):
    __tablename__ = "turnos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(String)
    hora = Column(String)
    estado = Column(String, default="pendiente")
    persona_id = Column(Integer, ForeignKey('personas.id'))
    persona = relationship("Persona", back_populates="turnos")