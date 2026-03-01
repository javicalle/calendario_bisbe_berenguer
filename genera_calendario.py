import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

URL = "https://consell-lh.playoffinformatica.com/peticioAjaxCompeticioPublica.php?peticioKey=peticio_competicio_publica_calendari&idGrup=899"

EQUIPO = "AFA INSTITUT BISBE BERENGUER"

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

calendar = Calendar()

partidos = soup.find_all("tr", class_="detallEnfrontament")

for partido in partidos:
    fecha_raw = partido.find("td", class_="data").text.strip()
    local = partido.find("td", class_="local").text.strip()
    visitant = partido.find("td", class_="visitant").text.strip()
    lugar = partido.find("td", class_="lloc").text.strip()

    if EQUIPO in local or EQUIPO in visitant:
        fecha_raw = fecha_raw.replace("h", "")
        fecha = datetime.strptime(fecha_raw, "%d-%m-%Y %H:%M")

        evento = Event()
        evento.name = f"{local} vs {visitant}"
        evento.begin = fecha
        evento.duration = {"hours": 1}  # duración estimada
        evento.location = lugar
        evento.description = "Partido liga escolar"

        calendar.events.add(evento)

with open("calendario.ics", "w", encoding="utf-8") as f:
    f.writelines(calendar)

print("Calendario generado correctamente.")
