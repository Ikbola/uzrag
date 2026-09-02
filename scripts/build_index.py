"""Build the FAISS index from chunks.

Usage:
    python scripts/build_index.py
"""

from uzrag.index import build


def main() -> None:
    idx, model = build()

    questions = [
        "Oqsillar qanday tuzilgan?",
        "Goʻroʻgʻli kim boʻlgan?",
        "Turkistonda yangi iqtisodiy siyosat",
    ]
    for q in questions:
        print(f"\n{'='*60}\n{q}\n{'='*60}")
        for r in idx.query(q, model, top_k=3):
            cite = f"{r['book'][:40]}, p{r['page']}"
            if r.get("section"):
                cite += f", {r['section']}-§"
            print(f"  {r['score']:.3f}  {cite}")
            print(f"         {r['text'][:120]}...")


if __name__ == "__main__":
    main()