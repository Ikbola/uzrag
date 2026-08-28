"""Chunk the OCR'd corpus into a JSONL file for indexing.

Usage:
    python scripts/build_chunks.py
"""

import json
from collections import Counter
from pathlib import Path

from uzrag.chunk import chunk_page
from dataclasses import asdict

CORPUS_DIR = Path("data/corpus")
OUT_PATH = Path("data/chunks.jsonl")


def main() -> None:
    all_chunks = []
    stats = Counter()

    for book_dir in sorted(p for p in CORPUS_DIR.iterdir() if p.is_dir()):
        book = book_dir.name
        section = None
        pages = sorted(book_dir.glob("p*.txt"))

        for page_path in pages:
            page = int(page_path.stem[1:])
            text = page_path.read_text(encoding="utf-8")
            chunks, section = chunk_page(text, book, page, section)

            if not chunks:
                stats[f"{book}: skipped"] += 1
            for c in chunks:
                c.chunk_index = len(all_chunks)
                all_chunks.append(c)

            stats[f"{book}: chunks"] += len(chunks)

        print(f"{book[:55]:55} {len(pages):>4} pages  "
              f"{stats[f'{book}: chunks']:>5} chunks  "
              f"{stats[f'{book}: skipped']:>3} skipped")

    with OUT_PATH.open("w", encoding="utf-8") as fh:
        for c in all_chunks:
            fh.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")

    lengths = [len(c.text) for c in all_chunks]
    with_section = sum(1 for c in all_chunks if c.section)

    print(f"\n{len(all_chunks)} chunks -> {OUT_PATH}")
    print(f"  length: min {min(lengths)}  median "
          f"{sorted(lengths)[len(lengths)//2]}  max {max(lengths)}")
    print(f"  with section metadata: {with_section} "
          f"({with_section/len(all_chunks):.0%})")
    print(f"\nexample citation: {all_chunks[len(all_chunks)//2].citation}")


if __name__ == "__main__":
    main()