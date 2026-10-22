import math
import re

import requests


class ServicioExternoError(Exception):
    """Error controlado al consultar o interpretar un servicio externo."""


def _obtener_json(url, params):
    try:
        respuesta = requests.get(url, params=params, timeout=5)
    except requests.Timeout as exc:
        raise ServicioExternoError(
            "El servicio externo tardó demasiado en responder. Intente nuevamente."
        ) from exc
    except requests.ConnectionError as exc:
        raise ServicioExternoError(
            "No fue posible conectar con el servicio externo."
        ) from exc
    except requests.RequestException as exc:
        raise ServicioExternoError(
            "Ocurrió un problema al realizar la consulta externa."
        ) from exc

    codigo = respuesta.status_code
    if codigo != 200:
        if codigo == 404:
            mensaje = "El servicio externo no encontró el recurso solicitado."
        elif codigo == 429:
            mensaje = "El servicio externo recibió demasiadas consultas. Intente más tarde."
        elif 500 <= codigo <= 599:
            mensaje = "El servicio externo no está disponible temporalmente."
        elif 400 <= codigo <= 499:
            mensaje = "El servicio externo rechazó la consulta. Revise los datos ingresados."
        else:
            mensaje = "El servicio externo respondió con un estado no esperado."
        raise ServicioExternoError(mensaje)

    try:
        return respuesta.json()
    except ValueError as exc:
        raise ServicioExternoError(
            "El servicio externo devolvió una respuesta no válida."
        ) from exc


def _numero_valido(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool) and math.isfinite(valor)


def consultar_clima(ciudad):
    ciudad = ciudad.strip()
    if not ciudad or len(ciudad) > 100:
        raise ValueError("Ingrese una ciudad de entre 1 y 100 caracteres.")

    geocodificacion = _obtener_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": ciudad, "count": 1, "language": "es", "format": "json"},
    )
    resultados = geocodificacion.get("results") if isinstance(geocodificacion, dict) else None
    if not isinstance(resultados, list) or not resultados:
        raise ServicioExternoError("No se encontró la ciudad indicada.")

    ubicacion = resultados[0]
    if not isinstance(ubicacion, dict):
        raise ServicioExternoError("El servicio de ubicación devolvió datos no válidos.")
    latitud = ubicacion.get("latitude")
    longitud = ubicacion.get("longitude")
    if not _numero_valido(latitud) or not _numero_valido(longitud):
        raise ServicioExternoError("El servicio de ubicación devolvió datos no válidos.")

    clima = _obtener_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": latitud,
            "longitude": longitud,
            "current": "temperature_2m,relative_humidity_2m,weather_code",
            "timezone": "auto",
        },
    )
    actual = clima.get("current") if isinstance(clima, dict) else None
    if not isinstance(actual, dict):
        raise ServicioExternoError("El servicio climático devolvió datos no válidos.")

    temperatura = actual.get("temperature_2m")
    humedad = actual.get("relative_humidity_2m")
    codigo = actual.get("weather_code")
    if (
        not _numero_valido(temperatura)
        or not _numero_valido(humedad)
        or not 0 <= humedad <= 100
        or not isinstance(codigo, int)
        or isinstance(codigo, bool)
    ):
        raise ServicioExternoError("El servicio climático devolvió datos no válidos.")

    estados = {
        0: "Despejado",
        1: "Mayormente despejado",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Niebla",
        48: "Niebla con escarcha",
        51: "Llovizna ligera",
        53: "Llovizna moderada",
        55: "Llovizna intensa",
        61: "Lluvia ligera",
        63: "Lluvia moderada",
        65: "Lluvia intensa",
        71: "Nevada ligera",
        73: "Nevada moderada",
        75: "Nevada intensa",
        80: "Chubascos ligeros",
        81: "Chubascos moderados",
        82: "Chubascos fuertes",
        95: "Tormenta",
        96: "Tormenta con granizo ligero",
        99: "Tormenta con granizo intenso",
    }

    return {
        "ciudad": ubicacion.get("name", ciudad),
        "pais": ubicacion.get("country", ""),
        "temperatura": temperatura,
        "humedad": humedad,
        "estado": estados.get(codigo, "Estado no identificado"),
        "hora": actual.get("time", ""),
    }


def consultar_tipo_cambio(moneda_origen, moneda_destino):
    moneda_origen = moneda_origen.strip().upper()
    moneda_destino = moneda_destino.strip().upper()
    formato_moneda = re.compile(r"^[A-Z]{3}$")
    if not formato_moneda.fullmatch(moneda_origen) or not formato_moneda.fullmatch(moneda_destino):
        raise ValueError("Ingrese códigos de moneda de tres letras, por ejemplo USD y CLP.")
    if moneda_origen == moneda_destino:
        raise ValueError("Seleccione dos monedas diferentes.")

    datos = _obtener_json(
        f"https://open.er-api.com/v6/latest/{moneda_origen}",
        {},
    )
    tasas = datos.get("rates") if isinstance(datos, dict) else None
    tasa = tasas.get(moneda_destino) if isinstance(tasas, dict) else None
    fecha = datos.get("time_last_update_utc") if isinstance(datos, dict) else None
    if (
        not isinstance(datos, dict)
        or datos.get("result") != "success"
        or not _numero_valido(tasa)
        or tasa <= 0
        or not isinstance(fecha, str)
    ):
        raise ServicioExternoError("El servicio de monedas devolvió datos no válidos.")

    return {
        "fecha": fecha,
        "origen": moneda_origen,
        "destino": moneda_destino,
        "tasa": tasa,
    }