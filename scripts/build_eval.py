"""Interactive tool to build a retrieval eval set from random chunks.

Usage:
    python scripts/build_eval.py
"""

import json
import random
from pathlib import Path

CHUNKS_PATH = Path("data/chunks.jsonl")
EVAL_PATH = Path("data/eval.jsonl")
SEED = 42


def load_done() -> set[int]:
    if not EVAL_PATH.exists():
        return set()
    done = set()
    with EVAL_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                done.add(json.loads(line)["chunk_index"])
            except (json.JSONDecodeError, KeyError):
                pass
    return done


def main() -> None:
    chunks = [json.loads(line) for line in CHUNKS_PATH.open(encoding="utf-8")]
    done = load_done()
    print(f"{len(chunks)} chunks, {len(done)} already in eval set\n")

    # filter to text chunks with real content
    candidates = [
        c for c in chunks
        if c.get("kind", "text") == "text"
        and len(c["text"]) >= 300
        and c["chunk_index"] not in done
    ]

    random.seed(SEED + len(done))  # shift seed so reruns show new chunks
    random.shuffle(candidates)

    added = 0

    try:
        for c in candidates:
            book_short = c["book"][:50]
            section = f", {c['section']}-§" if c.get("section") else ""
            print(f"\n{'='*70}")
            print(f"[{c['chunk_index']}]  {book_short}, p{c['page']}{section}")
            print(f"{'='*70}")
            print(c["text"][:600])
            if len(c["text"]) > 600:
                print(f"  ... ({len(c['text'])} chars total)")
            print()

            question = input("Question (Enter to skip, Ctrl+C to stop): ").strip()
            if not question:
                print("  skipped")
                continue

            answer = input("Short answer (1-2 sentences): ").strip()
            if not answer:
                print("  skipped")
                continue

            record = {
                "question": question,
                "answer": answer,
                "chunk_index": c["chunk_index"],
                "book": c["book"],
                "page": c["page"],
                "section": c.get("section"),
            }

            with EVAL_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")

            added += 1
            total = len(done) + added
            print(f"  saved ({total} total)")

            if total >= 50:
                print("\n50 questions reached — that's enough for a solid eval.")
                break

    except KeyboardInterrupt:
        print()

    print(f"\nadded {added} questions this session")
    print(f"total: {len(done) + added} -> {EVAL_PATH}")


if __name__ == "__main__":
    main()