"""Textbook retrieval API.

Usage:
    uvicorn uzrag.api:app --reload
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from uzrag.hybrid import build_hybrid, HybridIndex

app = FastAPI(
    title="uzrag",
    description="Retrieval over Uzbek 10th-grade textbooks",
    version="0.1.0",
)

_index: HybridIndex | None = None


def get_index() -> HybridIndex:
    global _index
    if _index is None:
        if not Path("data/index.faiss").exists():
            raise HTTPException(503, "Index not built. Run scripts/build_index.py first.")
        _index = build_hybrid()
    return _index


class Query(BaseModel):
    question: str = Field(..., min_length=5, description="Question in Uzbek")
    top_k: int = Field(default=5, ge=1, le=20)


class Result(BaseModel):
    text: str
    book: str
    page: int
    section: str | None
    citation: str
    score: float


class Response(BaseModel):
    question: str
    results: list[Result]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "index_built": Path("data/index.faiss").exists()}


@app.post("/search", response_model=Response)
def search(query: Query) -> Response:
    idx = get_index()
    raw = idx.query(query.question, top_k=query.top_k)

    results = []
    for r in raw:
        sec = r.get("section")
        cite = f"{r['book']}, {r['page']}-bet"
        if sec:
            cite += f", {sec}-§"
        results.append(Result(
            text=r["text"],
            book=r["book"],
            page=r["page"],
            section=sec,
            citation=cite,
            score=r["score"],
        ))

    return Response(question=query.question, results=results)