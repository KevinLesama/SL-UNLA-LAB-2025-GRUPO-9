
from fastapi import FastAPI, HTTPException, Request, status
from models import Persona
from database import Session, engine
from models import Base

app = FastAPI()
Base.metadata.create_all(engine)

@app.get("/personas/")
def listar_personas():
    session = Session()
    personas = session.query(Persona).all()
    resultado = [
        {
            "id": p.id,
            "dni": p.dni,
            "nombre": p.nombre,
            "email": p.email,
            "telefono": p.telefono,
            "fecha_de_nacimiento": p.fecha_de_nacimiento,
            "habilitado": p.habilitado
        }
        for p in personas
    ]
    session.close()
    return resultado

@app.get("/personas/{id}")
def obtener_persona(id: int):
    session = Session()
    persona = session.query(Persona).get(id)
    if persona is None:
        session.close()
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    resultado = {
        "id": persona.id,
        "dni": persona.dni,
        "nombre": persona.nombre,
        "email": persona.email,
        "telefono": persona.telefono,
        "fecha_de_nacimiento": persona.fecha_de_nacimiento,
        "habilitado": persona.habilitado
    }
    session.close()
    return resultado

@app.post("/personas/", status_code=status.HTTP_201_CREATED)
async def crear_persona(request: Request):
    session = Session()
    datos = await request.json()
    if session.query(Persona).filter_by(dni=datos.get("dni")).first():
        session.close()
        raise HTTPException(status_code=400, detail="El DNI ya está registrado")
    if session.query(Persona).filter_by(email=datos.get("email")).first():
        session.close()
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    if session.query(Persona).filter_by(telefono=datos.get("telefono")).first():
        session.close()
        raise HTTPException(status_code=400, detail="El teléfono ya está registrado")

    nueva_persona = Persona(
        dni=datos.get("dni"),
        nombre=datos.get("nombre"),
        email=datos.get("email"),
        telefono=datos.get("telefono"),
        fecha_de_nacimiento=datos.get("fecha_de_nacimiento"),
        habilitado=datos.get("habilitado", "si")
    )
    session.add(nueva_persona)
    try:
        session.commit()
        session.refresh(nueva_persona)
    except Exception:
        session.rollback()
        session.close()
        raise HTTPException(status_code=400, detail="Error al crear persona (email duplicado o datos inválidos)")
    resultado = {
        "id": nueva_persona.id,
        "dni": nueva_persona.dni,
        "nombre": nueva_persona.nombre,
        "email": nueva_persona.email,
        "telefono": nueva_persona.telefono,
        "fecha_de_nacimiento": nueva_persona.fecha_de_nacimiento,
        "habilitado": nueva_persona.habilitado
    }
    session.close()
    return resultado

@app.put("/personas/{id}")
async def modificar_persona(id: int, request: Request):
    session = Session()
    datos = await request.json()
    persona = session.query(Persona).get(id)
    if persona is None:
        session.close()
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    
    if "dni" in datos and datos["dni"] != persona.dni:
        if session.query(Persona).filter_by(dni=datos["dni"]).first():
            session.close()
            raise HTTPException(status_code=400, detail="El DNI ya está registrado")
        persona.dni = datos["dni"]
    if "email" in datos and datos["email"] != persona.email:
        if session.query(Persona).filter_by(email=datos["email"]).first():
            session.close()
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        persona.email = datos["email"]
    if "telefono" in datos and datos["telefono"] != persona.telefono:
        if session.query(Persona).filter_by(telefono=datos["telefono"]).first():
            session.close()
            raise HTTPException(status_code=400, detail="El teléfono ya está registrado")
        persona.telefono = datos["telefono"]

    persona.nombre = datos.get("nombre", persona.nombre)
    persona.fecha_de_nacimiento = datos.get("fecha_de_nacimiento", persona.fecha_de_nacimiento)
    persona.habilitado = datos.get("habilitado", persona.habilitado)

    session.commit()
    resultado = {
        "id": persona.id,
        "dni": persona.dni,
        "nombre": persona.nombre,
        "email": persona.email,
        "telefono": persona.telefono,
        "fecha_de_nacimiento": persona.fecha_de_nacimiento,
        "habilitado": persona.habilitado
    }
    session.close()
    return resultado


@app.delete("/personas/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_persona(id: int):
    session = Session()
    persona = session.query(Persona).get(id)
    if persona is None:
        session.close()
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    session.delete(persona)
    
    session.commit()
    session.close()
    return {"mensaje": "Persona eliminada"}
