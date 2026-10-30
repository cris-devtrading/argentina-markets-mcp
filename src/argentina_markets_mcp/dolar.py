import json
import urllib.request

BASE_URL = "https://dolarapi.com/v1/dolares"

ALIASES = {
    "oficial": "oficial",
    "blue": "blue",
    "mep": "bolsa",
    "bolsa": "bolsa",
    "ccl": "contadoconliqui",
    "contadoconliqui": "contadoconliqui",
    "tarjeta": "tarjeta",
    "mayorista": "mayorista",
    "cripto": "cripto",
}


def normalize_tipo(tipo: str) -> str:
    key = tipo.strip().lower().replace(" ", "").replace("_", "")
    if key not in ALIASES:
        valid = ", ".join(sorted(ALIASES))
        raise ValueError(f"Tipo de dólar desconocido: {tipo!r}. Válidos: {valid}")
    return ALIASES[key]


def fetch_json(url: str, timeout: float = 10.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "argentina-markets-mcp/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def get_dolar(tipo: str, fetch=fetch_json) -> dict:
    slug = normalize_tipo(tipo)
    data = fetch(f"{BASE_URL}/{slug}")
    return {
        "tipo": slug,
        "nombre": data.get("nombre"),
        "compra": data.get("compra"),
        "venta": data.get("venta"),
        "fecha_actualizacion": data.get("fechaActualizacion"),
        "fuente": "dolarapi.com",
    }
