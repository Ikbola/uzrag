"""OCR every page of every textbook and write cleaned text with metadata.

Usage:
    python scripts/ocr_corpus.py                 
    python scripts/ocr_corpus.py --limit 5       
"""

import argparse
import json
import time
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image

from uzrag.clean import clean

PDF_DIR = Path("data/pdfs")
OUT_DIR = Path("data/corpus")
DPI = 300
LANG = "uzb"
BATCH = 10  


def page_count(pdf: Path) -> int:
    return pdfinfo_from_path(str(pdf))["Pages"]


def process(pdf: Path, limit: int | None) -> dict:
    book_dir = OUT_DIR / pdf.stem
    book_dir.mkdir(parents=True, exist_ok=True)

    total = page_count(pdf)
    last = min(total, limit) if limit else total
    print(f"\n{pdf.stem}\n  {total} pages, processing {last}")

    stats = {"book": pdf.stem, "pages": last, "empty": 0, "chars": 0}
    started = time.time()

    for start in range(1, last + 1, BATCH):
        stop = min(start + BATCH - 1, last)
        images = convert_from_path(pdf, dpi=DPI, first_page=start, last_page=stop)

        for offset, image in enumerate(images):
            n = start + offset
            dest = book_dir / f"p{n:04}.txt"
            if dest.exists():
                continue

            raw = pytesseract.image_to_string(image, lang=LANG)
            text = clean(raw).strip()

            dest.write_text(text, encoding="utf-8")
            stats["chars"] += len(text)
            if len(text) < 100:
                stats["empty"] += 1

        elapsed = time.time() - started
        rate = stop / elapsed
        print(f"  {stop}/{last}  {rate:.1f} pages/s  "
              f"~{(last - stop) / rate / 60:.1f} min left")

    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_stats = []

    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        all_stats.append(process(pdf, args.limit))

    manifest = OUT_DIR / "manifest.json"
    manifest.write_text(json.dumps(all_stats, indent=2, ensure_ascii=False),
                        encoding="utf-8")

    print(f"\n{'book':55} {'pages':>7} {'empty':>7} {'chars':>10}")
    for s in all_stats:
        print(f"{s['book'][:55]:55} {s['pages']:>7} {s['empty']:>7} {s['chars']:>10}")
    print(f"\nmanifest -> {manifest}")

if __name__ == "__main__":
    main()