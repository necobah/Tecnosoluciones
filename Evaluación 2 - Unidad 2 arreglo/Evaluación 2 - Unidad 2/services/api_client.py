import math
import requests

from services.exceptions import ServicioExternoError


def obtener_json(url, params):
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


def numero_valido(valor):
    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and math.isfinite(valor)
    )