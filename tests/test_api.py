"""Integration tests for FastAPI endpoints."""

from pathlib import Path
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent.parent))
from main import app
import config

client = TestClient(app)


def test_status_endpoint():
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "active_model" in data


def test_samples_endpoint():
    res = client.get("/api/samples")
    assert res.status_code == 200
    samples = res.json()
    assert len(samples) >= 4
    assert samples[0]["id"] == "enterprise-saas"


def test_load_sample_endpoint():
    res = client.post("/api/samples/load/executive-employment")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["sample"]["id"] == "executive-employment"


def test_analyze_summary_endpoint():
    res = client.post("/api/analyze/summary")
    assert res.status_code == 200
    data = res.json()
    assert "tl_dr" in data
    assert "parties_involved" in data
    assert "core_rights" in data
    assert "rights_conceded" in data


def test_analyze_risks_endpoint():
    res = client.post("/api/analyze/risks")
    assert res.status_code == 200
    data = res.json()
    assert "strict_penalties" in data
    assert "strict_obligations" in data


def test_analyze_compliance_endpoint():
    res = client.post("/api/analyze/compliance")
    assert res.status_code == 200
    data = res.json()
    assert "overall_risk_score" in data
    assert "clause_audits" in data


def test_chat_rag_endpoint():
    res = client.post("/api/chat", json={"question": "What happens if I terminate early?"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "citations" in data


def test_download_zip_endpoint():
    res = client.get("/api/download-zip")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    assert len(res.content) > 1000
