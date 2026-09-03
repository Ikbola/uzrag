"""Evaluate retrieval accuracy against the hand-written eval set.

Usage:
    python scripts/eval_retrieval.py
"""

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from uzrag.index import Index, META_PATH, INDEX_PATH, MODEL_NAME

EVAL_PATH = Path("data/eval.jsonl")
RESULTS_PATH = Path("results/retrieval_eval.json")


def main() -> None:
    model = SentenceTransformer(MODEL_NAME)
    idx = Index.load(model)

    pairs = [json.loads(l) for l in EVAL_PATH.open(encoding="utf-8")]
    print(f"{len(pairs)} eval questions\n")

    hits = {k: 0 for k in [1, 3, 5, 10]}
    failures = []

    for p in pairs:
        results = idx.query(p["question"], model, top_k=10)
        retrieved_idxs = [r["chunk_index"] for r in results]
        target = p["chunk_index"]

        for k in hits:
            if target in retrieved_idxs[:k]:
                hits[k] += 1

        if target not in retrieved_idxs[:5]:
            top_score = results[0]["score"] if results else 0
            failures.append({
                "question": p["question"],
                "expected_chunk": target,
                "expected_book": p["book"][:40],
                "expected_page": p["page"],
                "top_result_chunk": retrieved_idxs[0] if retrieved_idxs else None,
                "top_result_score": round(top_score, 3),
            })

    n = len(pairs)
    print(f"{'metric':12} {'hits':>6} {'total':>6} {'recall':>8}")
    print("-" * 36)
    for k in hits:
        print(f"recall@{k:<5} {hits[k]:>6} {n:>6} {hits[k]/n:>8.1%}")

    if failures:
        print(f"\n{len(failures)} missed at recall@5:")
        for f in failures:
            print(f"  [{f['expected_chunk']}] {f['expected_book']}, p{f['expected_page']}")
            print(f"    Q: {f['question'][:80]}")
            print(f"    got chunk {f['top_result_chunk']} (score {f['top_result_score']})")

    RESULTS_PATH.parent.mkdir(exist_ok=True)
    RESULTS_PATH.write_text(json.dumps({
        "n_questions": n,
        "recall@1": hits[1] / n,
        "recall@3": hits[3] / n,
        "recall@5": hits[5] / n,
        "recall@10": hits[10] / n,
        "failures_at_5": failures,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nsaved -> {RESULTS_PATH}")


if __name__ == "__main__":
    main()