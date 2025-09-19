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
    turnos = relationship("Turnos", back_populates="persona")

class Turnos(Base):
    tablename="turnos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(String)
    hora = Column(String)
    estado = Column(String, default="pendiente")
    persona_id = Column(Integer , ForeignKey('personas.id'))
    persona = relationship("Persona", back_populates="turnos")
    #agregamos el back_populates en ambas clases para poder llamar los turnos de la persona
    #esto lo podemos usar para traer los turnos de una persona en particular cancelados



