from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class RiskLimits:
    max_order_ars: float = 200_000
    max_position_ars: float = 1_000_000
    max_data_age_seconds: float = 3600


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


class KillSwitch:
    def __init__(self) -> None:
        self.engaged = False
        self.reason = ""

    def engage(self, reason: str) -> None:
        self.engaged = True
        self.reason = reason

    def reset(self) -> None:
        self.engaged = False
        self.reason = ""


def check_data_fresh(fecha_iso, limits: RiskLimits, now=None) -> Decision:
    now = now or datetime.now(timezone.utc)
    try:
        ts = datetime.fromisoformat(str(fecha_iso).replace("Z", "+00:00"))
    except ValueError:
        return Decision(False, f"fecha inválida: {fecha_iso!r}")
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    age = (now - ts).total_seconds()
    if age > limits.max_data_age_seconds:
        return Decision(False, f"dato viejo: {age:.0f}s > {limits.max_data_age_seconds:.0f}s")
    return Decision(True, "dato fresco")


def check_order(order_ars: float, position_ars: float, limits: RiskLimits,
                kill_switch: KillSwitch) -> Decision:
    """order_ars con signo: positivo compra, negativo vende."""
    if kill_switch.engaged:
        return Decision(False, f"kill switch activo: {kill_switch.reason}")
    if abs(order_ars) > limits.max_order_ars:
        return Decision(False, f"orden excede el tope por orden ({limits.max_order_ars:,.0f})")
    after = position_ars + order_ars
    reduces = abs(after) < abs(position_ars)
    if abs(after) > limits.max_position_ars and not reduces:
        return Decision(False, f"posición excedería el tope ({limits.max_position_ars:,.0f})")
    return Decision(True, "ok")
