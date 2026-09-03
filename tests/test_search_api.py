"""Tests for the retrieval API."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from uzrag.api import app

client = TestClient(app)

INDEX_EXISTS = Path("data/index.faiss").exists()
needs_index = pytest.mark.skipif(not INDEX_EXISTS, reason="run build_index.py first")


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_rejects_short_query():
    r = client.post("/search", json={"question": "ha"})
    assert r.status_code == 422


def test_rejects_missing_field():
    r = client.post("/search", json={})
    assert r.status_code == 422


@needs_index
def test_search_returns_valid_shape():
    r = client.post("/search", json={"question": "Oqsillar nima?"})
    assert r.status_code == 200
    body = r.json()
    assert body["question"] == "Oqsillar nima?"
    assert len(body["results"]) == 5


@needs_index
def test_results_have_citations():
    r = client.post("/search", json={"question": "Oqsillar nima?"})
    for result in r.json()["results"]:
        assert "book" in result
        assert "page" in result
        assert "citation" in result
        assert "bet" in result["citation"]


@needs_index
def test_top_k_respected():
    r = client.post("/search", json={"question": "Oqsillar nima?", "top_k": 3})
    assert len(r.json()["results"]) == 3


@needs_index
def test_gorogli_finds_adabiyot():
    r = client.post("/search", json={"question": "Goʻroʻgʻli kim boʻlgan?"})
    books = [res["book"] for res in r.json()["results"]]
    assert any("Adabiyot" in b for b in books), f"expected Adabiyot in {books}"