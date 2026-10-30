# argentina-markets-mcp

MCP server (Python, mcp>=2.0, API `MCPServer`, no `FastMCP`) exposing Argentine
market data, plus paper-trading with deterministic risk guardrails.

## Rules
- Paper trading only. Never add real order execution or broker calls.
- Never commit secrets. `.env` and `audit_log.jsonl` are git-ignored.
- Every change needs tests that run without internet (inject fake quotes).
- Run `pytest` before every commit; keep commits small.
- Guardrails are deterministic and live in `risk.py`. The kill switch can be
  engaged by a tool but must never be disengageable by a tool.
- Standard library for HTTP (`urllib`); avoid new dependencies unless needed.

## Layout
src/argentina_markets_mcp/: dolar.py (connector), audit.py (@audited),
risk.py (limits, kill switch), paper.py (simulate_order), server.py (tools).

## Dev
```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e ".[dev]" && pytest
```
