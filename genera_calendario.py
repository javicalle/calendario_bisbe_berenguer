import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import hashlib

BASE_URL = "https://consell-lh.playoffinformatica.com/"
CALENDAR_URL = BASE_URL + "peticioAjaxCompeticioPublica.php?peticioKey=peticio_competicio_publica_calendari&idGrup=899"

EQUIPO = "AFA INSTITUT BISBE BERENGUER"
DURACION_HORAS = 1.5
ZONA = ZoneInfo("Europe/Madrid")

response = requests.get(CALENDAR_URL)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
calendar = Calendar()

partidos = soup.find_all("tr", class_="detallEnfrontament")

for partido in partidos:

    fecha_raw = partido.find("td", class_="data").get_text(strip=True)
    local = partido.find("td", class_="local").get_text(" ", strip=True)
    visitante = partido.find("td", class_="visitant").get_text(" ", strip=True)
    lugar = partido.find("td", class_="lloc").get_text(" ", strip=True)

    if EQUIPO not in local and EQUIPO not in visitante:
        continue

    # Fecha
    fecha_raw = fecha_raw.replace("h", "")
    fecha = datetime.strptime(fecha_raw, "%d-%m-%Y %H:%M")
    fecha = fecha.replace(tzinfo=ZONA)

    # Tipo partido
    if EQUIPO in local:
        tipo = "🏠 Local"
        rival = visitante
    else:
        tipo = "🚗 Visitante"
        rival = local

    # Enlace detalle partido
    data_href = partido.get("data-href")
    enlace = BASE_URL + data_href if data_href else BASE_URL

    # Crear evento
    evento = Event()

    evento.name = f"{tipo} vs {rival}"

    evento.begin = fecha
    evento.end = fecha + timedelta(hours=DURACION_HORAS)

    evento.location = lugar

    evento.url = enlace

    evento.description = (
        f"Partido liga escolar\n\n"
        f"Equipo: {EQUIPO}\n"
        f"Rival: {rival}\n"
        f"Condición: {tipo}\n\n"
        f"Lugar:\n{lugar}\n\n"
        f"Detalle del partido:\n{enlace}"
    )

    # UID estable (evita duplicados si se regenera)
    uid_source = f"{fecha}-{local}-{visitante}"
    evento.uid = hashlib.md5(uid_source.encode()).hexdigest()

    calendar.events.add(evento)

with open("calendario.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print("Calendario profesional generado correctamente.")
