import pytest

from argentina_markets_mcp.dolar import get_dolar, normalize_tipo


def test_aliases():
    assert normalize_tipo("MEP") == "bolsa"
    assert normalize_tipo(" ccl ") == "contadoconliqui"
    assert normalize_tipo("Contado con liqui") == "contadoconliqui"


def test_tipo_invalido():
    with pytest.raises(ValueError):
        normalize_tipo("euro")


def test_get_dolar_usa_el_endpoint_correcto():
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return {
            "nombre": "Bolsa",
            "compra": 1400,
            "venta": 1410,
            "fechaActualizacion": "2026-10-30T15:00:00.000Z",
        }

    result = get_dolar("mep", fetch=fake_fetch)
    assert calls == ["https://dolarapi.com/v1/dolares/bolsa"]
    assert result["compra"] == 1400
    assert result["venta"] == 1410
    assert result["fuente"] == "dolarapi.com"
