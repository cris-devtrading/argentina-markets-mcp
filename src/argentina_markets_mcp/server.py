from mcp.server.mcpserver import MCPServer

from argentina_markets_mcp import paper
from argentina_markets_mcp.audit import audited
from argentina_markets_mcp.dolar import get_dolar
from argentina_markets_mcp.risk import KillSwitch, RiskLimits

mcp = MCPServer("argentina-markets")

LIMITS = RiskLimits()
KILL_SWITCH = KillSwitch()
PORTFOLIO = paper.PaperPortfolio()


@mcp.tool()
def ping() -> str:
    """Health check."""
    return "pong"


@mcp.tool()
@audited
def get_dolar_quote(tipo: str = "mep") -> dict:
    """Cotización del dólar en Argentina (compra/venta).

    tipo: mep, ccl, oficial, blue, mayorista, tarjeta o cripto.
    Solo informa cotizaciones; no es asesoramiento financiero.
    """
    return get_dolar(tipo)


@mcp.tool()
@audited
def simulate_order(tipo: str, side: str, amount_ars: float) -> dict:
    """Orden simulada (paper trading) de compra/venta de USD contra ARS.

    side: 'buy' o 'sell'. amount_ars: monto en pesos, positivo.
    Pasa por los guardrails (kill switch, topes, frescura del dato).
    Devuelve status 'filled' o 'rejected' con el motivo.
    """
    return paper.simulate_order(tipo, side, amount_ars, PORTFOLIO, LIMITS, KILL_SWITCH)


@mcp.tool()
@audited
def get_paper_portfolio() -> dict:
    """Estado de la cartera simulada (en memoria; se reinicia con el servidor)."""
    return {
        **PORTFOLIO.snapshot(),
        "kill_switch_engaged": KILL_SWITCH.engaged,
        "kill_switch_reason": KILL_SWITCH.reason,
    }


@mcp.tool()
@audited
def engage_kill_switch(reason: str) -> dict:
    """Activa el kill switch: rechaza todas las órdenes siguientes."""
    KILL_SWITCH.engage(reason)
    return {"kill_switch_engaged": True, "reason": reason}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
