from mcp.server.fastmcp import FastMCP

mcp = FastMCP("argentina-markets")


@mcp.tool()
def ping() -> str:
    """Health check. Replace with real market-data tools."""
    return "pong"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
