from fastapi import FastAPI, HTTPException, Request, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Persona, Turnos, Base
from database import SessionLocal, engine
from datetime import datetime, date, timedelta
from config import settings
from utils import calcular_edad, turnoDisponible, turnoDisponibleEstado, MESES_ESPANOL

app = FastAPI()
Base.metadata.create_all(bind=engine)

# Dependencia que gestiona la sesión por request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Hecho por Kevin Lesama Soto
@app.get("/personas/")
def listar_personas(db: Session = Depends(get_db)):
    try:
        personas = db.query(Persona).all()
        resultado = []
        for p in personas:
            try:
                edad = calcular_edad(p.fecha_de_nacimiento) if p.fecha_de_nacimiento else None
            except Exception:
                edad = None
            resultado.append({
                "id": p.id,
                "dni": p.dni,
                "nombre": p.nombre,
                "email": p.email,
                "telefono": p.telefono,
                "fecha_de_nacimiento": p.fecha_de_nacimiento.isoformat() if p.fecha_de_nacimiento else None,
                "edad": edad,
                "habilitado": p.habilitado
            })
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al recuperar el listado de personas: {str(e)}")

#Hecho por Kevin Lesama Soto
@app.get("/personas/{id}")
def obtener_persona(id: int, db: Session = Depends(get_db)):
    try:
        persona = db.query(Persona).get(id)
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        try:
            edad = calcular_edad(persona.fecha_de_nacimiento) if persona.fecha_de_nacimiento else None
        except Exception:
            edad = None
        return {
            "id": persona.id,
            "dni": persona.dni,
            "nombre": persona.nombre,
            "email": persona.email,
            "telefono": persona.telefono,
            "fecha_de_nacimiento": persona.fecha_de_nacimiento.isoformat() if persona.fecha_de_nacimiento else None,
            "edad": edad,
            "habilitado": persona.habilitado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener la persona: {str(e)}")

#Hecho por Kevin Lesama Soto
@app.post("/personas/")
async def crear_persona(request: Request, db: Session = Depends(get_db)):
    try:
        datos = await request.json()

        if db.query(Persona).filter_by(dni=datos["dni"]).first():
            raise HTTPException(status_code=400, detail="El DNI ya está registrado")
        if db.query(Persona).filter_by(email=datos["email"]).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        if db.query(Persona).filter_by(telefono=datos["telefono"]).first():
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
            habilitado=datos.get("habilitado", True)
        )

        db.add(nueva_persona)
        db.commit()
        db.refresh(nueva_persona)

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
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al crear la persona: {str(e)}")

#Hecho por Nahuel Garcia
@app.put("/personas/{persona_id}")
async def modificar_persona(persona_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        persona = db.query(Persona).get(persona_id)
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
            if db.query(Persona).filter_by(dni=datos["dni"]).first():
                raise HTTPException(status_code=400, detail="El DNI ya está registrado")
            persona.dni = datos["dni"]

        if "email" in datos and datos["email"] != persona.email:
            if db.query(Persona).filter_by(email=datos["email"]).first():
                raise HTTPException(status_code=400, detail="El email ya está registrado")
            persona.email = datos["email"]

        if "telefono" in datos and datos["telefono"] != persona.telefono:
            if db.query(Persona).filter_by(telefono=datos["telefono"]).first():
                raise HTTPException(status_code=400, detail="El teléfono ya está registrado")
            persona.telefono = datos["telefono"]

        if "fecha_de_nacimiento" in datos:
            try:
                datos["fecha_de_nacimiento"] = datetime.strptime(datos["fecha_de_nacimiento"], "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido, use YYYY-MM-DD")

        for campo, valor in datos.items():
            setattr(persona, campo, valor)

        db.commit()
        db.refresh(persona)

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
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al modificar la persona: {str(e)}")

#Hecho por Nahuel Garcia
@app.delete("/personas/{id}", status_code=status.HTTP_200_OK)
def eliminar_persona(id: int, db: Session = Depends(get_db)):
    try:
        persona = db.query(Persona).get(id)
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        
        db.delete(persona)
        db.commit()
        return {"mensaje": "Persona eliminada"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al eliminar la persona: {str(e)}")

#Hecho por Agustin Nicolas Mancini
@app.get("/turnos/")
def listar_turnos(db: Session = Depends(get_db)):
    try:
        turnos = db.query(Turnos).all()
        resultado = [
            {
                "id": t.id,
                "fecha": t.fecha.isoformat(),
                "hora": t.hora,
                "estado": t.estado,
                "persona_id": t.persona_id
            }
            for t in turnos
        ]
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al recuperar el listado de turnos: {str(e)}")

#Hecho por Agustin Nicolas Mancini
@app.get("/turnos/{id}")
def obtener_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.query(Turnos).get(id)
        if turno is None:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        resultado = {
            "id": turno.id,
            "fecha": turno.fecha.isoformat(),
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener el turno: {str(e)}")

#Hecho por Agustin Nicolas Mancini
@app.post("/turnos/", status_code=status.HTTP_201_CREATED)
async def crear_turno(request: Request, db: Session = Depends(get_db)):
    try:
        datos = await request.json()
        fecha_str = datos.get("fecha")
        hora = datos.get("hora")
        persona = db.query(Persona).get(datos.get("persona_id"))
        if persona is None:
            raise HTTPException(status_code=400, detail="Persona no encontrada")

        if not fecha_str or not hora:
            raise HTTPException(status_code=400, detail="La fecha y la hora son obligatorias")

        # --- INICIO DE LA CORRECCIÓN ---
        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido, use YYYY-MM-DD")

        if not turnoDisponible(db, fecha_obj, hora=hora) and not turnoDisponibleEstado(db, fecha_obj, hora):
            raise HTTPException(status_code=400, detail="Esa hora no se encuentra disponible. Seleccione otra hora.")
        # --- FIN DE LA CORRECCIÓN ---
        
        if hora not in settings.HORARIOS_VALIDOS:
            raise HTTPException(status_code=400, detail="La hora debe estar entre 09:00 y 16:00 en intervalos de 30 minutos")

        seis_meses_atras = date.today() - timedelta(days=180)
        turnos_cancelados = (
            db.query(Turnos).filter(
                Turnos.persona_id == persona.id,
                Turnos.estado == settings.ESTADO_CANCELADO,
                Turnos.fecha >= seis_meses_atras
            ).count()
        )
        if turnos_cancelados >= 5 :
            persona.habilitado = False
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="La persona tiene 5 o más turnos cancelados en los últimos 6 meses"
            )
        else:
            persona.habilitado = True
            db.commit()

        # --- CORRECCIÓN CLAVE ---
        nuevo_turno = Turnos(
            fecha=fecha_obj, # Usar el objeto fecha, no el string
            hora=datos.get("hora"),
            estado=datos.get("estado", settings.ESTADO_PENDIENTE),
            persona_id=datos.get("persona_id")
        )
        db.add(nuevo_turno)
        db.commit()
        db.refresh(nuevo_turno)

        resultado = {
            "id": nuevo_turno.id,
            "fecha": nuevo_turno.fecha.isoformat(), # Usar .isoformat() para la respuesta
            "hora": nuevo_turno.hora,
            "estado": nuevo_turno.estado,
            "persona_id": nuevo_turno.persona_id
        }
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al crear el turno: {str(e)}")


#Hecho por Orion Jaime
@app.put("/turnos/{id}")
async def modificar_turno(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        datos = await request.json()
        turno = db.query(Turnos).get(id)
        if turno is None:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        
        if turno.estado == settings.ESTADO_CANCELADO or turno.estado == settings.ESTADO_ASISTIDO:
                raise HTTPException(status_code=400, detail="No se puede modificar un turno cancelado o asistido")

        turno.fecha = datos.get("fecha", turno.fecha)
        turno.hora = datos.get("hora", turno.hora)
        turno.estado = datos.get("estado", turno.estado)

        if "persona_id" in datos:
            persona = db.query(Persona).get(datos["persona_id"])
            if persona is None:
                raise HTTPException(status_code=400, detail="Persona no encontrada")
            turno.persona_id = datos["persona_id"]

        db.commit()
        resultado = {
            "id": turno.id,
            "fecha": turno.fecha,
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al modificar el turno: {str(e)}")

#Hecho por Orion Jaime
@app.delete("/turnos/{id}", status_code=status.HTTP_200_OK)
def eliminar_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.query(Turnos).get(id)
        if turno is None:
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        if turno.estado == settings.ESTADO_ASISTIDO:
            raise HTTPException(status_code=400, detail="No se puede eliminar un turno asistido")

        db.delete(turno)
        db.commit()
        return {"mensaje": "Turno eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al eliminar el turno: {str(e)}")

#Hecho por Kevin Lesama Soto
@app.get("/turnos-disponibles")
def turnos_disponibles(fecha: str, db: Session = Depends(get_db)):
    try:
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

        turnos_ocupados = db.query(Turnos).filter(
            Turnos.fecha == fecha_dt,
            Turnos.estado != settings.ESTADO_CANCELADO
        ).all()

        horarios_ocupados = {t.hora for t in turnos_ocupados}
        horarios_libres = [h for h in settings.HORARIOS_VALIDOS if h not in horarios_ocupados]

        return {"fecha": fecha, "horarios_disponibles": horarios_libres}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener los turnos disponibles: {str(e)}")

#Hecho por Nahuel Garcia
@app.put("/turnos/{id}/cancelar")
async def cancelar_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.query(Turnos).get(id)
        if turno is None:
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        if turno.estado == settings.ESTADO_ASISTIDO:
            raise HTTPException(status_code=400, detail="No se puede cancelar un turno asistido")

        if turno.estado == settings.ESTADO_CANCELADO:
            raise HTTPException(status_code=400, detail="El turno ya está cancelado")

        turno.estado = settings.ESTADO_CANCELADO
        db.commit()
        
        resultado = {
            "id": turno.id,
            "fecha": turno.fecha.isoformat(),
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al cancelar el turno: {str(e)}")

#Hecho por Kevin Lesama Soto
@app.put("/turnos/{id}/confirmar")
async def confirmar_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.query(Turnos).get(id)
        if turno is None:
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        if turno.estado == settings.ESTADO_ASISTIDO:
            raise HTTPException(status_code=400, detail="No se puede confirmar un turno asistido")

        if turno.estado == settings.ESTADO_CANCELADO or turno.estado == settings.ESTADO_CONFIRMADO:
            raise HTTPException(status_code=400, detail="No se puede confirmar un turno cancelado o ya confirmado")
        
        turno.estado = settings.ESTADO_CONFIRMADO
        db.commit()

        resultado = {
            "id": turno.id,
            "fecha": turno.fecha.isoformat(),
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al confirmar el turno: {str(e)}")

#Hecho por Nahuel Garcia
@app.get("/reportes/turnos-por-fecha")
def reportes_turnos_por_fecha(fecha: str, db: Session = Depends(get_db)):
    try:
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido, usar YYYY-MM-DD")

        # Consulta optimizada con JOIN para obtener turnos y personas
        turnos_con_persona = db.query(Turnos, Persona).join(Persona, Turnos.persona_id == Persona.id).filter(Turnos.fecha == fecha_dt).order_by(Persona.nombre, Turnos.hora).all()
        
        if not turnos_con_persona:
            return {"mensaje": "No hay turnos registrados para esta fecha"}

        # Diccionario para agrupar los turnos por persona
        personas_agrupadas = {}
        for turno, persona in turnos_con_persona:
            if persona.dni not in personas_agrupadas:
                personas_agrupadas[persona.dni] = {
                    "persona_nombre": persona.nombre,
                    "persona_dni": persona.dni,
                    "turnos": []
                }
            
            personas_agrupadas[persona.dni]["turnos"].append({
                "id": turno.id,
                "hora": turno.hora,
                "estado": turno.estado
            })

        # Convertir el diccionario a una lista para la respuesta final
        lista_personas = list(personas_agrupadas.values())

        return {"fecha": fecha, "personas": lista_personas}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al generar el reporte: {str(e)}")

#Hecho por Nahuel Garcia
@app.put("/turnos/{id}/cancelar")
async def cancelar_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.query(Turnos).get(id)
        if turno is None:
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        if turno.estado == settings.ESTADO_ASISTIDO:
            raise HTTPException(status_code=400, detail="No se puede cancelar un turno asistido")

        if turno.estado == settings.ESTADO_CANCELADO:
            raise HTTPException(status_code=400, detail="El turno ya está cancelado")

        turno.estado = settings.ESTADO_CANCELADO
        db.commit()
        
        resultado = {
            "id": turno.id,
            "fecha": turno.fecha,
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al cancelar el turno: {str(e)}")

#Hecho por Kevin Lesama Soto
@app.put("/turnos/{id}/confirmar")
async def confirmar_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.query(Turnos).get(id)
        if turno is None:
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        if turno.estado == settings.ESTADO_ASISTIDO:
            raise HTTPException(status_code=400, detail="No se puede confirmar un turno asistido")

        if turno.estado == settings.ESTADO_CANCELADO or turno.estado == settings.ESTADO_CONFIRMADO:
            raise HTTPException(status_code=400, detail="No se puede confirmar un turno cancelado o ya confirmado")
        
        turno.estado = settings.ESTADO_CONFIRMADO
        db.commit()

        resultado = {
            "id": turno.id,
            "fecha": turno.fecha,
            "hora": turno.hora,
            "estado": turno.estado,
            "persona_id": turno.persona_id
        }
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al confirmar el turno: {str(e)}")

#Hecho por Nahuel Garcia
@app.get("/reportes/turnos-por-fecha")
def reportes_turnos_por_fecha(fecha: str, db: Session = Depends(get_db)):
    try:
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido, usar YYYY-MM-DD")

        # Consulta optimizada con JOIN para obtener turnos y personas
        turnos_con_persona = db.query(Turnos, Persona).join(Persona, Turnos.persona_id == Persona.id).filter(Turnos.fecha == fecha_dt).order_by(Persona.nombre, Turnos.hora).all()
        
        if not turnos_con_persona:
            return {"mensaje": "No hay turnos registrados para esta fecha"}

        # Diccionario para agrupar los turnos por persona
        personas_agrupadas = {}
        for turno, persona in turnos_con_persona:
            if persona.dni not in personas_agrupadas:
                personas_agrupadas[persona.dni] = {
                    "persona_nombre": persona.nombre,
                    "persona_dni": persona.dni,
                    "turnos": []
                }
            
            personas_agrupadas[persona.dni]["turnos"].append({
                "id": turno.id,
                "hora": turno.hora,
                "estado": turno.estado
            })

        # Convertir el diccionario a una lista para la respuesta final
        lista_personas = list(personas_agrupadas.values())

        return {"fecha": fecha, "personas": lista_personas}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al generar el reporte: {str(e)}")

#Hecho por Orion Quimey Jaime Adell
@app.get("/reportes/turnos-por-persona")
def reportes_turnos_por_persona(dni: int, db: Session = Depends(get_db)):
    try:
        persona = db.query(Persona).filter_by(dni=dni).first()
        
        if persona is None:
            raise HTTPException(status_code=404, detail=f"Persona con DNI {dni} no encontrada.")

        turnos = db.query(Turnos).filter_by(persona_id=persona.id).all()

        resultado_turnos = [
            {
                "id": t.id,
                "fecha": t.fecha.isoformat(),
                "hora": t.hora,
                "estado": t.estado,
            }
            for t in turnos
        ]
        
        return {
            "dni": persona.dni,
            "nombre": persona.nombre,
            "turnos": resultado_turnos
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener los turnos por persona: {str(e)}")
        
#Hecho por Kevin Lesama Soto
@app.get("/reportes/estado-personas")
def reporte_estado_personas(habilitada: bool, db: Session = Depends(get_db)):
    try:
        personas = db.query(Persona).filter(Persona.habilitado == habilitada).all()
        
        resultado = []
        for p in personas:
            try:
                edad = calcular_edad(p.fecha_de_nacimiento) if p.fecha_de_nacimiento else None
            except Exception:
                edad = None
            
            resultado.append({
                "id": p.id,
                "dni": p.dni,
                "nombre": p.nombre,
                "email": p.email,
                "telefono": p.telefono,
                "fecha_de_nacimiento": p.fecha_de_nacimiento.isoformat() if p.fecha_de_nacimiento else None,
                "edad": edad,
                "habilitado": p.habilitado
            })
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener el reporte: {str(e)}")

#Hecho por Agustin Nicolas Mancini
@app.get("/reportes/turnos-cancelados")
def reportes_turnos_cancelados(min: int, db: Session = Depends(get_db)):
    try:
        # Consulta optimizada que agrupa y cuenta en la base de datos
        personas_con_cancelados = (
            db.query(
                Persona,
                func.count(Turnos.id).label("cantidad_cancelados")
            )
            .join(Turnos, Persona.id == Turnos.persona_id)
            .filter(Turnos.estado == settings.ESTADO_CANCELADO)
            .group_by(Persona.id)
            .having(func.count(Turnos.id) >= min)
            .all()
        )

        if not personas_con_cancelados:
            return {"mensaje": f"No hay personas con {min} o más turnos cancelados"}

        resultado = []
        for persona, cantidad in personas_con_cancelados:
            # Obtener el detalle de los turnos cancelados para esta persona
            turnos_detalle = db.query(Turnos).filter(
                Turnos.persona_id == persona.id,
                Turnos.estado == settings.ESTADO_CANCELADO
            ).all()

            resultado.append({
                "persona_id": persona.id,
                "dni": persona.dni,
                "nombre": persona.nombre,
                "cantidad_cancelados": cantidad,
                "turnos_cancelados": [
                    {
                        "id": t.id,
                        "fecha": t.fecha.isoformat(),
                        "hora": t.hora,
                        "estado": t.estado
                    }
                    for t in turnos_detalle
                ]
            })

        return {"minimo": min, "personas": resultado}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al generar el reporte: {str(e)}")

#Hecho por Orion Quimey Jaime Adell
@app.get("/reportes/turnos-por-persona")
def reportes_turnos_por_persona(dni: int, db: Session = Depends(get_db)):
    try:
        persona = db.query(Persona).filter_by(dni=dni).first()
        
        if persona is None:
            raise HTTPException(status_code=404, detail=f"Persona con DNI {dni} no encontrada.")

        turnos = db.query(Turnos).filter_by(persona_id=persona.id).all()

        resultado_turnos = [
            {
                "id": t.id,
                "fecha": t.fecha,
                "hora": t.hora,
                "estado": t.estado,
            }
            for t in turnos
        ]
        
        return {
            "dni": persona.dni,
            "nombre": persona.nombre,
            "turnos": resultado_turnos
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener los turnos por persona: {str(e)}")
        
#Hecho por Kevin Lesama Soto
@app.get("/reportes/estado-personas")
def reporte_estado_personas(habilitada: bool, db: Session = Depends(get_db)):
    try:
        personas = db.query(Persona).filter(Persona.habilitado == habilitada).all()
        
        resultado = []
        for p in personas:
            try:
                edad = calcular_edad(p.fecha_de_nacimiento) if p.fecha_de_nacimiento else None
            except Exception:
                edad = None
            
            resultado.append({
                "id": p.id,
                "dni": p.dni,
                "nombre": p.nombre,
                "email": p.email,
                "telefono": p.telefono,
                "fecha_de_nacimiento": p.fecha_de_nacimiento.isoformat() if p.fecha_de_nacimiento else None,
                "edad": edad,
                "habilitado": p.habilitado
            })
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al obtener el reporte: {str(e)}")

#Hecho por Agustin Nicolas Mancini
@app.get("/reportes/turnos-cancelados")
def reportes_turnos_cancelados(min: int, db: Session = Depends(get_db)):
    try:
        # Consulta optimizada que agrupa y cuenta en la base de datos
        personas_con_cancelados = (
            db.query(
                Persona,
                func.count(Turnos.id).label("cantidad_cancelados")
            )
            .join(Turnos, Persona.id == Turnos.persona_id)
            .filter(Turnos.estado == settings.ESTADO_CANCELADO)
            .group_by(Persona.id)
            .having(func.count(Turnos.id) >= min)
            .all()
        )

        if not personas_con_cancelados:
            return {"mensaje": f"No hay personas con {min} o más turnos cancelados"}

        resultado = []
        for persona, cantidad in personas_con_cancelados:
            # Obtener el detalle de los turnos cancelados para esta persona
            turnos_detalle = db.query(Turnos).filter(
                Turnos.persona_id == persona.id,
                Turnos.estado == settings.ESTADO_CANCELADO
            ).all()

            resultado.append({
                "persona_id": persona.id,
                "dni": persona.dni,
                "nombre": persona.nombre,
                "cantidad_cancelados": cantidad,
                "turnos_cancelados": [
                    {
                        "id": t.id,
                        "fecha": t.fecha,
                        "hora": t.hora,
                        "estado": t.estado
                    }
                    for t in turnos_detalle
                ]
            })

        return {"minimo": min, "personas": resultado}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al generar el reporte: {str(e)}")

#Hecho por Orion Quimey Jaime Adell
@app.get("/reportes/turnos-cancelados-por-mes")
def reportes_turnos_cancelados_por_mes(db: Session = Depends(get_db)):
    try:
        hoy = date.today()
        # Obtener el primer y último día del mes actual
        primer_dia_mes = hoy.replace(day=1)
        if hoy.month == 12:
            ultimo_dia_mes = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            ultimo_dia_mes = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)

        mes_nombre_es = MESES_ESPANOL[hoy.month - 1]

        turnos_con_persona = (
            db.query(Turnos, Persona)
            .join(Persona, Turnos.persona_id == Persona.id)
            .filter(
                Turnos.estado == settings.ESTADO_CANCELADO,
                Turnos.fecha >= primer_dia_mes,
                Turnos.fecha <= ultimo_dia_mes
            )
            .order_by(Persona.nombre, Turnos.fecha, Turnos.hora)
            .all()
        )

        if not turnos_con_persona:
            return {
                "anio": hoy.year,
                "mes": mes_nombre_es,
                "mensaje": "No hay turnos cancelados en este mes."
            }

        personas_agrupadas = {}
        for turno, persona in turnos_con_persona:
            if persona.dni not in personas_agrupadas:
                personas_agrupadas[persona.dni] = {
                    "persona_nombre": persona.nombre,
                    "persona_dni": persona.dni,
                    "turnos_cancelados": []
                }
            
            personas_agrupadas[persona.dni]["turnos_cancelados"].append({
                "id": turno.id,
                "fecha": turno.fecha.isoformat(),
                "hora": turno.hora,
                "estado": turno.estado
            })

        lista_personas = list(personas_agrupadas.values())

        return {
            "anio": hoy.year,
            "mes": mes_nombre_es,
            "personas": lista_personas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al generar el reporte de cancelados por mes: {str(e)}")



#Hecho por Agustin Nicolas Mancini
@app.get("/reportes/turnos-confirmados")
def reportes_turnos_confirmados(desde: str, hasta: str, db: Session = Depends(get_db)):
    try:
        try:
            fecha_desde = datetime.strptime(desde, "%Y-%m-%d").date()
            fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido, usar YYYY-MM-DD")

        if fecha_desde > fecha_hasta:
            raise HTTPException(status_code=400, detail="La fecha 'desde' no puede ser posterior a 'hasta'")

        # Consulta optimizada con JOIN para obtener turnos y personas
        turnos_con_persona = db.query(Turnos, Persona).join(Persona, Turnos.persona_id == Persona.id).filter(
            Turnos.estado == settings.ESTADO_CONFIRMADO,
            Turnos.fecha >= fecha_desde,
            Turnos.fecha <= fecha_hasta
        ).order_by(Persona.nombre, Turnos.fecha, Turnos.hora).all()

        if not turnos_con_persona:
            return {"mensaje": "No hay turnos confirmados en el rango de fechas especificado"}

        # Diccionario para agrupar los turnos por persona
        personas_agrupadas = {}
        for turno, persona in turnos_con_persona:
            if persona.dni not in personas_agrupadas:
                personas_agrupadas[persona.dni] = {
                    "persona_nombre": persona.nombre,
                    "persona_dni": persona.dni,
                    "turnos": []
                }
            
            personas_agrupadas[persona.dni]["turnos"].append({
                "id": turno.id,
                "fecha": turno.fecha.isoformat(), # <-- CORRECCIÓN CLAVE
                "hora": turno.hora,
                "estado": turno.estado
            })

        # Convertir el diccionario a una lista para la respuesta final
        lista_personas = list(personas_agrupadas.values())

        return {
            "desde": fecha_desde.isoformat(),
            "hasta": fecha_hasta.isoformat(),
            "personas": lista_personas
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al generar el reporte: {str(e)}")