from services.api_client import obtener_json, numero_valido
from services.exceptions import ServicioExternoError


def consultar_clima(ciudad):

    ciudad = ciudad.strip()

    if not ciudad or len(ciudad) > 100:
        raise ValueError(
            "Ingrese una ciudad de entre 1 y 100 caracteres."
        )

    geocodificacion = obtener_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {
            "name": ciudad,
            "count": 1,
            "language": "es",
            "format": "json"
        }
    )

    resultados = (
        geocodificacion.get("results")
        if isinstance(geocodificacion, dict)
        else None
    )

    if not isinstance(resultados, list) or not resultados:
        raise ServicioExternoError(
            "No se encontró la ciudad indicada."
        )

    ubicacion = resultados[0]

    latitud = ubicacion.get("latitude")
    longitud = ubicacion.get("longitude")

    if (
        not numero_valido(latitud)
        or not numero_valido(longitud)
    ):
        raise ServicioExternoError(
            "El servicio de ubicación devolvió datos no válidos."
        )

    clima = obtener_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": latitud,
            "longitude": longitud,
            "current": "temperature_2m,relative_humidity_2m,weather_code",
            "timezone": "auto"
        }
    )

    actual = clima.get("current")

    temperatura = actual.get("temperature_2m")
    humedad = actual.get("relative_humidity_2m")
    codigo = actual.get("weather_code")

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
        99: "Tormenta con granizo intenso"
    }

    return {
        "ciudad": ubicacion.get("name", ciudad),
        "pais": ubicacion.get("country", ""),
        "temperatura": temperatura,
        "humedad": humedad,
        "estado": estados.get(
            codigo,
            "Estado no identificado"
        ),
        "hora": actual.get("time", "")
    }