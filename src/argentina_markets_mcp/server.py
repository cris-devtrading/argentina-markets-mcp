from mcp.server.mcpserver import MCPServer

from argentina_markets_mcp.dolar import get_dolar

mcp = MCPServer("argentina-markets")


@mcp.tool()
def ping() -> str:
    """Health check."""
    return "pong"


@mcp.tool()
def get_dolar_quote(tipo: str = "mep") -> dict:
    """Cotización del dólar en Argentina (compra/venta).

    tipo: mep, ccl, oficial, blue, mayorista, tarjeta o cripto.
    Solo informa cotizaciones; no es asesoramiento financiero.
    """
    return get_dolar(tipo)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
