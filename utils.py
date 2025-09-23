from datetime import datetime, date, timedelta
from models import Turnos

def calcular_edad(fecha_nacimiento):
    if isinstance(fecha_nacimiento, str):
        fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
    elif isinstance(fecha_nacimiento, date):
        fecha_nac = fecha_nacimiento
    else:
        raise ValueError("Formato de fecha inválido")

    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

def turnoDisponible(session, fecha, hora):
    try:
        horaInicio = datetime.strptime(hora, "%H:%M")
    except ValueError:
        return False
    
    horaFin = horaInicio + timedelta(minutes=30)

    turnos = session.query(Turnos).filter(Turnos.fecha == fecha).all()

    for t in turnos:
        tInicio = datetime.strptime(t.hora, "%H:%M")
        tFin = tInicio + timedelta(minutes=30)

        if (horaInicio < tFin and horaFin > tInicio):
            return False
    return True

def turnoDisponibleEstado(session, fecha, hora):
    try:
        horaInicio = datetime.strptime(hora, "%H:%M")
    except ValueError:
        return False
    
    horaFin = horaInicio + timedelta(minutes=30)

    turnos = session.query(Turnos).filter_by(fecha=fecha, hora=hora).all()
    for t in turnos:
        if t.estado != "cancelado":
            return False
    return True
#si el turno esta cancelado retorna true

HORARIOS_VALIDOS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
    "15:00", "15:30", "16:00"
]