"""Hybrid retrieval: semantic (FAISS) + keyword (BM25), with RRF fusion."""

import json
import re
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from uzrag.index import Index, MODEL_NAME

CHUNKS_PATH = Path("data/chunks.jsonl")
RRF_K = 60  # standard reciprocal rank fusion constant


def tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer for Uzbek."""
    return re.findall(r"[a-zA-Zʻʼ\u0400-\u04FF]{2,}", text.lower())


class HybridIndex:
    def __init__(self, chunks: list[dict], faiss_index: Index,
                 model: SentenceTransformer):
        self.chunks = chunks
        self.faiss_index = faiss_index
        self.model = model

        corpus = [tokenize(c["text"]) for c in chunks]
        self.bm25 = BM25Okapi(corpus)

    def query(self, question: str, top_k: int = 5,
              semantic_weight: float = 1.0,
              bm25_weight: float = 1.0) -> list[dict]:
        # semantic arm
        sem_results = self.faiss_index.query(question, self.model, top_k=50)
        sem_ranks = {r["chunk_index"]: rank
                     for rank, r in enumerate(sem_results)}

        # bm25 arm
        tokens = tokenize(question)
        bm25_scores = self.bm25.get_scores(tokens)
        bm25_top = np.argsort(bm25_scores)[::-1][:50]
        bm25_ranks = {int(idx): rank for rank, idx in enumerate(bm25_top)}

        # reciprocal rank fusion
        all_idxs = set(sem_ranks) | set(bm25_ranks)
        scored = []
        for idx in all_idxs:
            sem_rrf = semantic_weight / (RRF_K + sem_ranks.get(idx, 999))
            bm25_rrf = bm25_weight / (RRF_K + bm25_ranks.get(idx, 999))
            scored.append((idx, sem_rrf + bm25_rrf))

        scored.sort(key=lambda x: -x[1])

        results = []
        for idx, score in scored[:top_k]:
            chunk = dict(self.chunks[idx])
            chunk["score"] = round(score, 4)
            chunk["sem_rank"] = sem_ranks.get(idx, -1)
            chunk["bm25_rank"] = bm25_ranks.get(idx, -1)
            results.append(chunk)

        return results


def build_hybrid() -> HybridIndex:
    model = SentenceTransformer(MODEL_NAME)
    faiss_idx = Index.load(model)
    chunks = [json.loads(l) for l in CHUNKS_PATH.open(encoding="utf-8")]
    return HybridIndex(chunks, faiss_idx, model)