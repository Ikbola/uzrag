"""Evaluate hybrid retrieval against the eval set.

Usage:
    python scripts/eval_hybrid.py
"""

import json
from pathlib import Path

from uzrag.hybrid import build_hybrid

EVAL_PATH = Path("data/eval.jsonl")
RESULTS_PATH = Path("results/hybrid_eval.json")


def main() -> None:
    hybrid = build_hybrid()

    pairs = [json.loads(l) for l in EVAL_PATH.open(encoding="utf-8")]
    print(f"{len(pairs)} eval questions\n")

    hits = {k: 0 for k in [1, 3, 5, 10]}
    failures = []

    for p in pairs:
        results = hybrid.query(p["question"], top_k=10)
        retrieved = [r["chunk_index"] for r in results]
        target = p["chunk_index"]

        for k in hits:
            if target in retrieved[:k]:
                hits[k] += 1

        if target not in retrieved[:5]:
            r0 = results[0] if results else {}
            failures.append({
                "question": p["question"],
                "expected": target,
                "got": r0.get("chunk_index"),
                "sem_rank": r0.get("sem_rank"),
                "bm25_rank": r0.get("bm25_rank"),
            })

    n = len(pairs)
    print(f"{'metric':12} {'hits':>6} {'total':>6} {'recall':>8}")
    print("-" * 36)
    for k in hits:
        r = hits[k] / n
        print(f"recall@{k:<5} {hits[k]:>6} {n:>6} {r:>8.1%}")

    if failures:
        print(f"\n{len(failures)} missed at recall@5:")
        for f in failures:
            print(f"  [{f['expected']}] Q: {f['question'][:70]}")

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