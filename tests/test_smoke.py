import argentina_markets_mcp
from argentina_markets_mcp.server import ping


def test_version():
    assert argentina_markets_mcp.__version__ == "0.1.0"


def test_ping():
    assert ping() == "pong"
