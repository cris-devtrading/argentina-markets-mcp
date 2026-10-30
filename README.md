# argentina-markets-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes Argentine market data to AI agents, plus the building blocks for a paper-trading agent with deterministic risk guardrails and an auditable decision log.

> **Paper trading only. Not financial advice.** Quotes come from a public third-party API and may be delayed or inaccurate.

## Status

Early stage, solo project. What works today:

| Component | What it does | Tests |
|---|---|---|
| `get_dolar_quote` tool | MEP, CCL, official, blue, wholesale, card and crypto dollar quotes via [dolarapi.com](https://dolarapi.com) (no API key) | yes |
| Audit log | `@audited` decorator writes one JSON line per tool call (timestamp, args, result or error, duration) | yes |
| Risk module | Kill switch, per-order cap, position cap (reducing a position is always allowed), data-freshness check | yes |

Not built yet: BYMA equities/options/bonds tools, and the paper-trading agent that wires the risk module to the tools.

## Quick start

Requires Python 3.10+ (developed and tested on 3.12).

    git clone https://github.com/cris-devtrading/argentina-markets-mcp.git
    cd argentina-markets-mcp
    uv venv --python 3.12 && source .venv/bin/activate
    uv pip install -e ".[dev]"
    pytest

Run the server over stdio:

    python -m argentina_markets_mcp.server

## Tools

- `ping`: health check.
- `get_dolar_quote(tipo="mep")`: returns buy/sell and the source timestamp. `tipo` accepts `mep`, `ccl`, `oficial`, `blue`, `mayorista`, `tarjeta`, `cripto`.

## Audit log

Every call to an audited tool appends a line to `audit_log.jsonl` (override with the `AUDIT_LOG_PATH` environment variable). The file is git-ignored. A logging failure never breaks the tool.

## Risk guardrails

`risk.py` contains pure, network-free functions, so they are easy to test:

- `KillSwitch`: when engaged, every order is rejected.
- `check_order`: rejects orders above the per-order cap, and orders that would push a position above its cap unless they reduce it.
- `check_data_fresh`: rejects stale or invalid quote timestamps.

The default limits in `RiskLimits` are placeholders, not recommendations. Configure them for your own case.

## Secrets

No credentials belong in this repo. Copy `.env.example` to `.env` (git-ignored) for local settings.

## License

MIT
