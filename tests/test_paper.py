from datetime import datetime, timezone

import pytest

from argentina_markets_mcp.paper import PaperPortfolio, simulate_order
from argentina_markets_mcp.risk import KillSwitch, RiskLimits

LIMITS = RiskLimits(max_order_ars=200_000, max_position_ars=1_000_000, max_data_age_seconds=3600)
NOW = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)


def fake_quote(tipo):
    return {
        "tipo": "bolsa",
        "compra": 1000.0,
        "venta": 1100.0,
        "fecha_actualizacion": "2026-10-30T11:57:00.000Z",
    }


def run(side, amount, portfolio, kill_switch=None, now=NOW):
    return simulate_order("mep", side, amount, portfolio, LIMITS,
                          kill_switch or KillSwitch(), get_quote=fake_quote, now=now)


def test_compra_ejecuta():
    p = PaperPortfolio(cash_ars=1_000_000)
    r = run("buy", 110_000, p)
    assert r["status"] == "filled"
    assert r["price"] == 1100.0
    assert p.usd == pytest.approx(100.0)
    assert p.cash_ars == pytest.approx(890_000)


def test_venta_ejecuta():
    p = PaperPortfolio(cash_ars=0, usd=100.0)
    r = run("sell", 50_000, p)
    assert r["status"] == "filled"
    assert r["price"] == 1000.0
    assert p.usd == pytest.approx(50.0)
    assert p.cash_ars == pytest.approx(50_000)


def test_dato_viejo_rechaza_y_no_toca_la_cartera():
    p = PaperPortfolio(cash_ars=1_000_000)
    r = run("buy", 100_000, p, now=datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc))
    assert r["status"] == "rejected"
    assert "viejo" in r["reason"]
    assert (p.cash_ars, p.usd) == (1_000_000, 0.0)


def test_kill_switch_rechaza():
    ks = KillSwitch()
    ks.engage("manual")
    p = PaperPortfolio(cash_ars=1_000_000)
    r = run("buy", 100_000, p, kill_switch=ks)
    assert r["status"] == "rejected"
    assert "kill switch" in r["reason"]
    assert p.usd == 0.0


def test_tope_por_orden_rechaza():
    p = PaperPortfolio(cash_ars=1_000_000)
    r = run("buy", 300_000, p)
    assert r["status"] == "rejected"
    assert "tope por orden" in r["reason"]


def test_tope_de_posicion_rechaza():
    p = PaperPortfolio(cash_ars=1_000_000, usd=900.0)  # posición ~945.000 a precio medio
    r = run("buy", 100_000, p)
    assert r["status"] == "rejected"
    assert "posición" in r["reason"]


def test_fondos_insuficientes():
    p = PaperPortfolio(cash_ars=50_000)
    r = run("buy", 100_000, p)
    assert r["status"] == "rejected"
    assert "fondos" in r["reason"]


def test_no_se_puede_vender_lo_que_no_se_tiene():
    p = PaperPortfolio(cash_ars=0, usd=0.0)
    r = run("sell", 10_000, p)
    assert r["status"] == "rejected"
    assert "USD" in r["reason"]


def test_side_invalido_levanta_error():
    with pytest.raises(ValueError):
        run("hold", 1000, PaperPortfolio())


def test_monto_no_positivo_levanta_error():
    with pytest.raises(ValueError):
        run("buy", 0, PaperPortfolio())
