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
| Paper trading | `simulate_order` runs quote, freshness check, risk check and a simulated fill against an in-memory portfolio; rejections are logged too | yes |

Not built yet: BYMA equities/options/bonds tools, a persistent portfolio, and a strategy/agent loop on top of these tools.

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

- `simulate_order(tipo, side, amount_ars)`: simulated buy/sell of USD against ARS. Buys fill at the ask, sells at the bid, no short positions. Returns `filled` or `rejected` with the reason.
- `get_paper_portfolio()`: current simulated cash, USD and kill-switch state (in memory, resets on restart).
- `engage_kill_switch(reason)`: rejects all further orders. There is intentionally no tool to disengage it; restart the server.

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
