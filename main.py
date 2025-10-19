from fastapi import FastAPI, HTTPException, Request, status
from models import Persona, Turnos, Base
from database import Session, engine
from datetime import datetime, date, timedelta
from utils import calcular_edad, turnoDisponible, turnoDisponibleEstado, HORARIOS_VALIDOS

app = FastAPI()
Base.metadata.create_all(engine)
"""
#Hecho por Kevin Lesama Soto
@app.get("/personas/")
def listar_personas():
    session = Session()
    personas = session.query(Persona).all()
    resultado = []
    for p in personas:
        try:
            edad = calcular_edad(p.fecha_de_nacimiento)
        except Exception:
            edad = None
        resultado.append({
            "id": p.id,
            "dni": p.dni,
            "nombre": p.nombre,
            "email": p.email,
            "telefono": p.telefono,
            "fecha_de_nacimiento": p.fecha_de_nacimiento,
            "edad": edad,
            "habilitado": p.habilitado
        })
    session.close()
    return resultado
    """
@app.get("/personas/")
def listar_personas():
    session = Session()
    try:
        personas = session.query(Persona).all()
        resultado = []
        for p in personas:
            try:
                edad = calcular_edad(p.fecha_de_nacimiento)
            except Exception:
                edad = None
            resultado.append({
                "id": p.id,
                "dni": p.dni,
                "nombre": p.nombre,
                "email": p.email,
                "telefono": p.telefono,
                "fecha_de_nacimiento": p.fecha_de_nacimiento,
                "edad": edad,
                "habilitado": p.habilitado
            })
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al recuperar el listado de personas: {str(e)}")
    finally:
        session.close()
"""
#Hecho por Kevin Lesama Soto
@app.get("/personas/{id}")
def obtener_persona(id: int):
    session = Session()
    persona = session.query(Persona).get(id)
    if persona is None:
        session.close()
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    try:
        edad = calcular_edad(persona.fecha_de_nacimiento)
    except Exception:
        edad = None
    resultado = {
        "id": persona.id,
        "dni": persona.dni,
        "nombre": persona.nombre,
        "email": persona.email,
        "telefono": persona.telefono,
        "fecha_de_nacimiento": persona.fecha_de_nacimiento,
        "edad": edad,
        "habilitado": persona.habilitado
    }
    session.close()
    return resultado
"""
@app.get("/personas/{id}")
def obtener_persona(id: int):
    session = Session()
    try:
        persona = session.query(Persona).get(id)
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        try:
            edad = calcular_edad(persona.fecha_de_nacimiento)
        except Exception:
            edad = None
        return {
            "id": persona.id,
            "dni": persona.dni,
            "nombre": persona.nombre,
            "email": persona.email,
            "telefono": persona.telefono,
            "fecha_de_nacimiento": persona.fecha_de_nacimiento,
            "edad": edad,
            "habilitado": persona.habilitado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener la persona: {str(e)}")
    finally:
        session.close()

"""

#Hecho por Kevin Lesama Soto
@app.post("/personas/")
async def crear_persona(request: Request):
    session = Session()
    datos = await request.json()

    if session.query(Persona).filter_by(dni=datos["dni"]).first():
        session.close()
        raise HTTPException(status_code=400, detail="El DNI ya está registrado")
    if session.query(Persona).filter_by(email=datos["email"]).first():
        session.close()
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    if session.query(Persona).filter_by(telefono=datos["telefono"]).first():
        session.close()
        raise HTTPException(status_code=400, detail="El teléfono ya está registrado")

    if "telefono" in datos:
        try:
            datos["telefono"] = int(datos["telefono"])
        except ValueError:
            session.close()
            raise HTTPException(status_code=400, detail="El teléfono debe ser un número")
    
    try:
        fecha_nac = datetime.strptime(datos["fecha_de_nacimiento"], "%Y-%m-%d").date()
    except ValueError:
        session.close()
        raise HTTPException(status_code=400, detail="Formato de fecha inválido, use YYYY-MM-DD")

    nueva_persona = Persona(
        dni=datos["dni"],
        nombre=datos["nombre"],
        email=datos["email"],
        telefono=int(datos["telefono"]),
        fecha_de_nacimiento=fecha_nac,
        habilitado=datos.get("habilitado", "si")
    )

    session.add(nueva_persona)
    try:
        session.commit()
        session.refresh(nueva_persona)
    except Exception:
        session.rollback()
        session.close()
        raise HTTPException(status_code=400, detail="Error al crear persona")
    
    resultado = {
        "id": nueva_persona.id,
        "dni": nueva_persona.dni,
        "nombre": nueva_persona.nombre,
        "email": nueva_persona.email,
        "telefono": nueva_persona.telefono,
        "fecha_de_nacimiento": nueva_persona.fecha_de_nacimiento.isoformat(),
        "edad": calcular_edad(nueva_persona.fecha_de_nacimiento),
        "habilitado": nueva_persona.habilitado
    }
    session.close()
    return resultado
"""
@app.post("/personas/")
async def crear_persona(request: Request):
    session = Session()
    try:
        datos = await request.json()

        if session.query(Persona).filter_by(dni=datos["dni"]).first():
            raise HTTPException(status_code=400, detail="El DNI ya está registrado")
        if session.query(Persona).filter_by(email=datos["email"]).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        if session.query(Persona).filter_by(telefono=datos["telefono"]).first():
            raise HTTPException(status_code=400, detail="El teléfono ya está registrado")

        try:
            datos["telefono"] = int(datos["telefono"])
        except ValueError:
            raise HTTPException(status_code=400, detail="El teléfono debe ser un número")
        
        try:
            fecha_nac = datetime.strptime(datos["fecha_de_nacimiento"], "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido, use YYYY-MM-DD")

        nueva_persona = Persona(
            dni=datos["dni"],
            nombre=datos["nombre"],
            email=datos["email"],
            telefono=datos["telefono"],
            fecha_de_nacimiento=fecha_nac,
            habilitado=datos.get("habilitado", "si")
        )

        session.add(nueva_persona)
        session.commit()
        session.refresh(nueva_persona)

        return {
            "id": nueva_persona.id,
            "dni": nueva_persona.dni,
            "nombre": nueva_persona.nombre,
            "email": nueva_persona.email,
            "telefono": nueva_persona.telefono,
            "fecha_de_nacimiento": nueva_persona.fecha_de_nacimiento.isoformat(),
            "edad": calcular_edad(nueva_persona.fecha_de_nacimiento),
            "habilitado": nueva_persona.habilitado
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al crear la persona: {str(e)}")
    finally:
        session.close()
"""

#Hecho por Nahuel Garcia
@app.put("/personas/{persona_id}")
async def modificar_persona(persona_id: int, request: Request):
    session = Session()
    persona = session.query(Persona).get(persona_id)
    if not persona:
        session.close()
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    datos = await request.json()

    if "telefono" in datos:
        try:
            datos["telefono"] = int(datos["telefono"])
        except ValueError:
            session.close()
            raise HTTPException(status_code=400, detail="El teléfono debe ser un número")

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

    if "fecha_de_nacimiento" in datos:
        try:
            datos["fecha_de_nacimiento"] = datetime.strptime(datos["fecha_de_nacimiento"], "%Y-%m-%d").date()
        except ValueError:
            session.close()
            raise HTTPException(status_code=400, detail="Formato de fecha inválido, use YYYY-MM-DD")

    for campo, valor in datos.items():
        setattr(persona, campo, valor)

    try:
        session.commit()
        session.refresh(persona)
    except Exception:
        session.rollback()
        session.close()
        raise HTTPException(status_code=400, detail="Error al modificar persona")

    resultado = {
        "id": persona.id,
        "dni": persona.dni,
        "nombre": persona.nombre,
        "email": persona.email,
        "telefono": persona.telefono,
        "fecha_de_nacimiento": persona.fecha_de_nacimiento.isoformat(),
        "edad": calcular_edad(persona.fecha_de_nacimiento),
        "habilitado": persona.habilitado
    }
    session.close()
    return resultado
"""
@app.put("/personas/{persona_id}")
async def modificar_persona(persona_id: int, request: Request):
    session = Session()
    try:
        persona = session.query(Persona).get(persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona no encontrada")

        datos = await request.json()

        # Validaciones
        if "telefono" in datos:
            try:
                datos["telefono"] = int(datos["telefono"])
            except ValueError:
                raise HTTPException(status_code=400, detail="El teléfono debe ser un número")

        if "dni" in datos and datos["dni"] != persona.dni:
            if session.query(Persona).filter_by(dni=datos["dni"]).first():
                raise HTTPException(status_code=400, detail="El DNI ya está registrado")
            persona.dni = datos["dni"]

        if "email" in datos and datos["email"] != persona.email:
            if session.query(Persona).filter_by(email=datos["email"]).first():
                raise HTTPException(status_code=400, detail="El email ya está registrado")
            persona.email = datos["email"]

        if "telefono" in datos and datos["telefono"] != persona.telefono:
            if session.query(Persona).filter_by(telefono=datos["telefono"]).first():
                raise HTTPException(status_code=400, detail="El teléfono ya está registrado")
            persona.telefono = datos["telefono"]

        if "fecha_de_nacimiento" in datos:
            try:
                datos["fecha_de_nacimiento"] = datetime.strptime(datos["fecha_de_nacimiento"], "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido, use YYYY-MM-DD")

        for campo, valor in datos.items():
            setattr(persona, campo, valor)

        session.commit()
        session.refresh(persona)

        return {
            "id": persona.id,
            "dni": persona.dni,
            "nombre": persona.nombre,
            "email": persona.email,
            "telefono": persona.telefono,
            "fecha_de_nacimiento": persona.fecha_de_nacimiento.isoformat(),
            "edad": calcular_edad(persona.fecha_de_nacimiento),
            "habilitado": persona.habilitado
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al modificar la persona: {str(e)}")
    finally:
        session.close()

"""

#Hecho por Nahuel Garcia
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
"""
@app.delete("/personas/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_persona(id: int):
    session = Session()
    try:
        persona = session.query(Persona).get(id)
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        
        session.delete(persona)
        session.commit()
        return {"mensaje": "Persona eliminada"}

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al eliminar la persona: {str(e)}")
    finally:
        session.close()


#Hecho por Agustin Nicolas Mancini
@app.get("/turnos/")
def listar_turnos():
    session = Session()
    try:
        turnos = session.query(Turnos).all()
        resultado = [
            {
                "id": t.id,
                "fecha": t.fecha,
                "hora": t.hora,
                "estado": t.estado,
                "persona_id": t.persona_id
            }
            for t in turnos
        ]
        session.close()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al recuperar el listado de turnos: {str(e)}")
    finally:
        session.close()

#Hecho por Agustin Nicolas Mancini
@app.get("/turnos/{id}")
def obtener_turno(id: int):
    session = Session()
    try:
        turno = session.query(Turnos).get(id)
        if turno is None:
            session.close()
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        resultado = {
            "id": turno.id,
            "fecha": turno.fecha,
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        session.close()
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener el turno: {str(e)}")
    finally:
        session.close()

#Hecho por Agustin Nicolas Mancini
@app.post("/turnos/", status_code=status.HTTP_201_CREATED)
async def crear_turno(request: Request):
    session = Session()
    try:
        datos = await request.json()
        fecha = datos.get("fecha")
        hora = datos.get("hora")
        persona = session.query(Persona).get(datos.get("persona_id"))
        if persona is None:
            session.close()
            raise HTTPException(status_code=400, detail="Persona no encontrada")

        if not fecha or not hora:
            session.close()
            raise HTTPException(status_code=400, detail="La fecha y la hora son obligatorias")

        if not turnoDisponible(session, datos.get("fecha"), hora = datos.get("hora"))and not turnoDisponibleEstado(session, datos.get("fecha"), datos.get("hora")):
            session.close()
            raise HTTPException(status_code=400, detail="Esa hora no se encuentra disponible. Seleccione otra hora.")
        
        if hora not in HORARIOS_VALIDOS:
            session.close()
            raise HTTPException(status_code=400, detail="La hora debe estar entre 09:00 y 16:00 en intervalos de 30 minutos")

            
        
        seis_meses_atras = date.today() - timedelta(days=180)
        turnos_cancelados = (
            session.query(Turnos).filter(
                Turnos.persona_id == persona.id,
                Turnos.estado == "cancelado",
                Turnos.fecha >= seis_meses_atras
            ).count()
        )
        if turnos_cancelados >= 5 :
            persona.habilitado = "no"
            session.commit()
            session.close()
            raise HTTPException(
                status_code=400,
                detail="La persona tiene 5 o más turnos cancelados en los últimos 6 meses"
            )
        else:
            persona.habilitado = "si"
            session.commit()

        nuevo_turno = Turnos(
            fecha=datos.get("fecha"),
            hora=datos.get("hora"),
            estado=datos.get("estado", "pendiente"),
            persona_id=datos.get("persona_id")
        )
        session.add(nuevo_turno)
        session.commit()
        session.refresh(nuevo_turno)

        resultado = {
            "id": nuevo_turno.id,
            "fecha": nuevo_turno.fecha,
            "hora": nuevo_turno.hora,
            "estado": nuevo_turno.estado,
            "persona_id": nuevo_turno.persona_id
        }
        session.close()
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al crear el turno: {str(e)}")
    finally:
        session.close()

#Hecho por Orion Jaime
@app.put("/turnos/{id}")
async def modificar_turno(id: int, request: Request):
    session = Session()
    try:
        datos = await request.json()
        turno = session.query(Turnos).get(id)
        fecha = datos.get("fecha")
        hora = datos.get("hora")
        if turno is None:
            session.close()
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        
        if turno.estado == "cancelado" or turno.estado == "asistido":
                session.close()
                raise HTTPException(status_code=400, detail="No se puede modificar un turno cancelado o asistido")

        turno.fecha = datos.get("fecha", turno.fecha)
        turno.hora = datos.get("hora", turno.hora)
        turno.estado = datos.get("estado", turno.estado)

        if "persona_id" in datos:
            persona = session.query(Persona).get(datos["persona_id"])
            if persona is None:
                session.close()
                raise HTTPException(status_code=400, detail="Persona no encontrada")
            turno.persona_id = datos["persona_id"]

        session.commit()
        resultado = {
            "id": turno.id,
            "fecha": turno.fecha,
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        session.close()
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al modificar el turno: {str(e)}")
    finally:
        session.close()

#Hecho por Orion Jaime
@app.delete("/turnos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_turno(id: int):
    session = Session()
    try:
        turno = session.query(Turnos).get(id)
        if turno.estado == "asistido":
                session.close()
                raise HTTPException(status_code=400, detail="No se puede eliminar un turno asistido")
        if turno is None:
            session.close()
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        session.delete(turno)
        session.commit()
        session.close()
        return {"mensaje": "Turno eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al eliminar el turno: {str(e)}")
    finally:
        session.close()

#Hecho por Kevin Lesama Soto
@app.get("/turnos-disponibles")
def turnos_disponibles(fecha: str):
    session = Session()
    try:
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            session.close()
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

        turnos_ocupados = session.query(Turnos).filter(
            Turnos.fecha == fecha_dt,
            Turnos.estado != "cancelado"   
        ).all()

        horarios_ocupados = {t.hora for t in turnos_ocupados}

        horarios_libres = [h for h in HORARIOS_VALIDOS if h not in horarios_ocupados]

        session.close()
        return {"fecha": fecha, "horarios_disponibles": horarios_libres}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener los turnos disponibles: {str(e)}")
    finally:
        session.close()

@app.put("/turnos/{id}/cancelar")
async def cancelar_turno(id: int, request: Request):
    session = Session()
    try:
        
        turno = session.query(Turnos).get(id)
 
        if turno is None:
            session.close()
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        if turno.estado == "asistido":
            session.close()
            raise HTTPException(status_code=400, detail="No se puede cancelar un turno asistido")

        if turno.estado == "cancelado":
            session.close()
            raise HTTPException(status_code=400, detail="El turno ya esta Cancelado")

        turno.estado = "cancelado"

        session.commit()
        resultado = {
            "id": turno.id,
            "fecha": turno.fecha,
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        session.close()
        return resultado

    except HTTPException:
        session.close()
        raise
    except Exception as e:
        session.rollback()
        session.close()
    raise HTTPException(status_code=500, detail="Ocurrió un error al cancelar el turno")

@app.put("/turnos/{id}/confirmar")
async def confirmar_turno(id: int, request: Request):
    session = Session()
    try:
        
        turno = session.query(Turnos).get(id)
 
        if turno is None:
            session.close()
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        if turno.estado == "asistido":
            session.close()
            raise HTTPException(status_code=400, detail="No se puede confirmar un turno asistido")

        if turno.estado == "cancelado" or turno.estado == "confirmado":
            session.close()
            raise HTTPException(status_code=400, detail="No se puede confirmar un turno cancelado o ya confirmado")
        


        turno.estado = "confirmado"

        session.commit()
        resultado = {
            "id": turno.id,
            "fecha": turno.fecha,
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        session.close()
        return resultado

    except HTTPException:
        session.close()
        raise
    except Exception as e:
        session.rollback()
        session.close()
    raise HTTPException(status_code=500, detail="Ocurrió un error al confirmar el turno")

