from datetime import datetime, date

def calcular_edad(fecha_nacimiento_str):
    fecha_nac = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))