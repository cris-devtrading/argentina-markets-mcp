from dataclasses import dataclass

from argentina_markets_mcp.dolar import get_dolar
from argentina_markets_mcp.risk import KillSwitch, RiskLimits, check_data_fresh, check_order

EPS = 1e-9


@dataclass
class PaperPortfolio:
    cash_ars: float = 1_000_000.0
    usd: float = 0.0

    def snapshot(self) -> dict:
        return {"cash_ars": round(self.cash_ars, 2), "usd": round(self.usd, 6)}


def simulate_order(tipo, side, amount_ars, portfolio, limits, kill_switch,
                   get_quote=get_dolar, now=None) -> dict:
    """Compra o vende USD (MEP/CCL/etc.) contra ARS en una cartera simulada.

    Compra al precio `venta`, vende al precio `compra`. Sin posiciones en corto.
    La posición se valúa a precio medio para los topes de riesgo.
    """
    side = side.strip().lower()
    if side not in ("buy", "sell"):
        raise ValueError("side debe ser 'buy' o 'sell'")
    if amount_ars <= 0:
        raise ValueError("amount_ars debe ser positivo")

    quote = get_quote(tipo)
    base = {"tipo": quote.get("tipo", tipo), "side": side, "amount_ars": amount_ars}

    def reject(reason):
        return {**base, "status": "rejected", "reason": reason,
                "portfolio": portfolio.snapshot()}

    fresh = check_data_fresh(quote.get("fecha_actualizacion"), limits, now=now)
    if not fresh.allowed:
        return reject(fresh.reason)

    compra, venta = quote.get("compra"), quote.get("venta")
    if not compra or not venta or compra <= 0 or venta <= 0:
        return reject("cotización inválida")

    price = venta if side == "buy" else compra
    mid = (compra + venta) / 2
    position_ars = portfolio.usd * mid
    signed = amount_ars if side == "buy" else -amount_ars

    decision = check_order(signed, position_ars, limits, kill_switch)
    if not decision.allowed:
        return reject(decision.reason)

    if side == "buy":
        if amount_ars > portfolio.cash_ars + EPS:
            return reject("fondos insuficientes")
        portfolio.cash_ars -= amount_ars
        portfolio.usd += amount_ars / price
    else:
        if amount_ars > portfolio.usd * price + EPS:
            return reject("no hay USD suficientes para vender")
        portfolio.cash_ars += amount_ars
        portfolio.usd = max(0.0, portfolio.usd - amount_ars / price)

    return {**base, "status": "filled", "reason": "ok", "price": price,
            "portfolio": portfolio.snapshot()}
