from datetime import datetime, timezone

from argentina_markets_mcp.risk import KillSwitch, RiskLimits, check_data_fresh, check_order

LIMITS = RiskLimits(max_order_ars=200_000, max_position_ars=1_000_000, max_data_age_seconds=3600)
NOW = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)


def test_datos_frescos_ok():
    assert check_data_fresh("2026-10-30T11:57:00.000Z", LIMITS, now=NOW).allowed


def test_datos_viejos_bloquea():
    assert not check_data_fresh("2026-10-29T11:57:00.000Z", LIMITS, now=NOW).allowed


def test_fecha_invalida_bloquea():
    assert not check_data_fresh("ayer", LIMITS, now=NOW).allowed


def test_orden_ok():
    assert check_order(100_000, 0, LIMITS, KillSwitch()).allowed


def test_orden_grande_bloquea():
    assert not check_order(300_000, 0, LIMITS, KillSwitch()).allowed


def test_posicion_excedida_bloquea():
    assert not check_order(150_000, 900_000, LIMITS, KillSwitch()).allowed


def test_reducir_posicion_permitido():
    assert check_order(-100_000, 1_200_000, LIMITS, KillSwitch()).allowed


def test_kill_switch_bloquea_todo():
    ks = KillSwitch()
    ks.engage("test")
    d = check_order(1, 0, LIMITS, ks)
    assert not d.allowed
    assert "test" in d.reason
