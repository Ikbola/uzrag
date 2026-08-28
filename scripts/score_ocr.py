"""Measure OCR error rates against hand-corrected gold pages.

Usage:
    python scripts/score_ocr.py
"""

import re
import unicodedata
from pathlib import Path

import jiwer

GOLD_DIR = Path("data/gold")
OCR_DIR = Path("data/ocr")


def collapse(text: str) -> str:
    """Normalize whitespace only — no character substitution."""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    golds = sorted(GOLD_DIR.glob("*.txt"))
    if not golds:
        print("no gold files found")
        return

    print(f"{'page':50} {'CER':>8} {'WER':>8} {'gold':>7} {'ocr':>7}")
    print("-" * 84)

    total_cer = total_wer = 0.0
    scored = 0

    for gold_path in golds:
        ocr_path = OCR_DIR / gold_path.name
        if not ocr_path.exists():
            print(f"{gold_path.name[:50]:50}  no matching OCR file")
            continue

        gold = collapse(gold_path.read_text(encoding="utf-8"))
        hypo = collapse(ocr_path.read_text(encoding="utf-8"))

        cer = jiwer.cer(gold, hypo)
        wer = jiwer.wer(gold, hypo)

        total_cer += cer
        total_wer += wer
        scored += 1

        name = gold_path.stem[:50]
        print(f"{name:50} {cer:>8.1%} {wer:>8.1%} {len(gold):>7} {len(hypo):>7}")

    if scored:
        print("-" * 84)
        print(f"{'mean':50} {total_cer/scored:>8.1%} {total_wer/scored:>8.1%}")


if __name__ == "__main__":
    main()