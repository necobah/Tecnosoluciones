import re

from services.api_client import obtener_json, numero_valido
from services.exceptions import ServicioExternoError


def consultar_tipo_cambio(
    moneda_origen,
    moneda_destino
):

    moneda_origen = moneda_origen.strip().upper()
    moneda_destino = moneda_destino.strip().upper()

    formato_moneda = re.compile(r"^[A-Z]{3}$")

    if (
        not formato_moneda.fullmatch(moneda_origen)
        or not formato_moneda.fullmatch(moneda_destino)
    ):
        raise ValueError(
            "Ingrese códigos de moneda de tres letras, por ejemplo USD y CLP."
        )

    if moneda_origen == moneda_destino:
        raise ValueError(
            "Seleccione dos monedas diferentes."
        )

    datos = obtener_json(
        f"https://open.er-api.com/v6/latest/{moneda_origen}",
        {}
    )

    tasas = datos.get("rates")
    tasa = tasas.get(moneda_destino)
    fecha = datos.get("time_last_update_utc")

    if (
        datos.get("result") != "success"
        or not numero_valido(tasa)
        or tasa <= 0
        or not isinstance(fecha, str)
    ):
        raise ServicioExternoError(
            "El servicio de monedas devolvió datos no válidos."
        )

    return {
        "fecha": fecha,
        "origen": moneda_origen,
        "destino": moneda_destino,
        "tasa": tasa
    }