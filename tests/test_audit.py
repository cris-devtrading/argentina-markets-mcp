import json

import pytest

from argentina_markets_mcp.audit import audited


def _records(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_registra_llamada_ok(tmp_path, monkeypatch):
    log = tmp_path / "audit.jsonl"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(log))

    @audited
    def f(x):
        return {"x": x}

    assert f(x=1) == {"x": 1}
    rec = _records(log)[0]
    assert rec["tool"] == "f"
    assert rec["status"] == "ok"
    assert rec["kwargs"] == {"x": 1}
    assert rec["result"] == {"x": 1}


def test_registra_error_y_lo_propaga(tmp_path, monkeypatch):
    log = tmp_path / "audit.jsonl"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(log))

    @audited
    def boom():
        raise ValueError("falla")

    with pytest.raises(ValueError):
        boom()
    rec = _records(log)[0]
    assert rec["status"] == "error"
    assert "falla" in rec["error"]
