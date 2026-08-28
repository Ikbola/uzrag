"""Measure CER/WER after each cleaning stage.

Usage:
    python scripts/score_stages.py
"""

import re
import unicodedata
from pathlib import Path

import jiwer

from uzrag.clean import STAGES

GOLD_DIR = Path("data/gold")
OCR_DIR = Path("data/ocr")


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def main() -> None:
    pairs = []
    for gold_path in sorted(GOLD_DIR.glob("*.txt")):
        ocr_path = OCR_DIR / gold_path.name
        if ocr_path.exists():
            pairs.append((
                gold_path.stem,
                gold_path.read_text(encoding="utf-8"),
                ocr_path.read_text(encoding="utf-8"),
            ))

    print(f"{'stage':20} {'CER':>8} {'ΔCER':>8} {'WER':>8} {'ΔWER':>8}")
    print("-" * 56)

    texts = [h for _, _, h in pairs]
    golds = [collapse(g) for _, g, _ in pairs]

    def score(hyps):
        cers = [jiwer.cer(g, collapse(h)) for g, h in zip(golds, hyps)]
        wers = [jiwer.wer(g, collapse(h)) for g, h in zip(golds, hyps)]
        return sum(cers) / len(cers), sum(wers) / len(wers)

    prev_cer, prev_wer = score(texts)
    print(f"{'raw OCR':20} {prev_cer:>8.2%} {'':>8} {prev_wer:>8.2%}")

    for name, fn in STAGES:
        texts = [fn(t) for t in texts]
        cer, wer = score(texts)
        print(f"{name:20} {cer:>8.2%} {cer-prev_cer:>+8.2%} "
              f"{wer:>8.2%} {wer-prev_wer:>+8.2%}")
        prev_cer, prev_wer = cer, wer


if __name__ == "__main__":
    main()