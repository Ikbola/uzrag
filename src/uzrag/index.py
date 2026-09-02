"""Build and query a FAISS index over textbook chunks."""

import json
from dataclasses import asdict
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = Path("data/chunks.jsonl")
INDEX_PATH = Path("data/index.faiss")
META_PATH = Path("data/index_meta.json")

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_chunks() -> list[dict]:
    with CHUNKS_PATH.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


class Index:
    def __init__(self, chunks: list[dict], embeddings: np.ndarray):
        self.chunks = chunks
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)

    def query(self, question: str, model: SentenceTransformer,
              top_k: int = 5) -> list[dict]:
        vec = model.encode([question], normalize_embeddings=True)
        scores, ids = self.index.search(vec.astype("float32"), top_k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue
            chunk = dict(self.chunks[idx])
            chunk["score"] = round(float(score), 4)
            results.append(chunk)
        return results

    def save(self) -> None:
        faiss.write_index(self.index, str(INDEX_PATH))
        META_PATH.write_text(
            json.dumps(self.chunks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, model: SentenceTransformer) -> "Index":
        index = faiss.read_index(str(INDEX_PATH))
        chunks = json.loads(META_PATH.read_text(encoding="utf-8"))
        obj = cls.__new__(cls)
        obj.chunks = chunks
        obj.index = index
        return obj


def build() -> tuple[Index, SentenceTransformer]:
    print("loading model...")
    model = SentenceTransformer(MODEL_NAME)

    chunks = load_chunks()
    texts = [c["text"] for c in chunks]
    print(f"encoding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True,
                              batch_size=64, normalize_embeddings=False)

    idx = Index(chunks, np.array(embeddings))
    idx.save()
    print(f"saved index ({idx.index.ntotal} vectors) -> {INDEX_PATH}")
    return idx, model
