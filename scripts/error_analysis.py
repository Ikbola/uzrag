"""Inventory OCR errors against gold pages, grouped by cause.

Usage:
    python scripts/error_analysis.py
"""

import re
import unicodedata
import unicodedata as ud
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

GOLD_DIR = Path("data/gold")
OCR_DIR = Path("data/ocr")

APOSTROPHES = set("'\u2018\u2019\u0060\u00b4\u02bb\u02bc\u2032")
CYRILLIC = re.compile(r"[\u0400-\u04FF]")


def collapse(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def describe(ch: str) -> str:
    if ch == " ":
        return "SPACE"
    try:
        name = ud.name(ch)
    except ValueError:
        name = "?"
    return f"U+{ord(ch):04X} {ch!r} {name}"


def classify(want: str, got: str) -> str:
    """Bucket a substitution by its likely cause."""
    w, g = set(want), set(got)
    if w & APOSTROPHES and g & APOSTROPHES:
        return "apostrophe variant"
    if w & APOSTROPHES or g & APOSTROPHES:
        return "apostrophe lost/added"
    if CYRILLIC.search(got) and not CYRILLIC.search(want):
        return "cyrillic bleed"
    if want.lower() == got.lower():
        return "case only"
    if want.isdigit() or got.isdigit():
        return "digit confusion"
    return "other"


def analyse(gold: str, hypo: str) -> tuple[Counter, Counter, list]:
    sm = SequenceMatcher(None, gold, hypo, autojunk=False)
    buckets: Counter = Counter()
    pairs: Counter = Counter()
    examples: list = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        want, got = gold[i1:i2], hypo[j1:j2]

        if tag == "replace":
            bucket = classify(want, got)
        elif tag == "delete":
            bucket = "apostrophe lost/added" if set(want) & APOSTROPHES else "dropped"
        else:  # insert
            if got.strip() == "-":
                bucket = "hyphen inserted"
            elif set(got) & APOSTROPHES:
                bucket = "apostrophe lost/added"
            else:
                bucket = "inserted"

        n = max(len(want), len(got))
        buckets[bucket] += n

        if len(want) <= 3 and len(got) <= 3:
            pairs[(want, got)] += 1

        if len(examples) < 400:
            ctx = gold[max(0, i1 - 25):i2 + 25].replace("\n", " ")
            examples.append((bucket, want, got, ctx))

    return buckets, pairs, examples


def main() -> None:
    all_buckets: Counter = Counter()
    all_pairs: Counter = Counter()
    total_gold = 0

    for gold_path in sorted(GOLD_DIR.glob("*.txt")):
        ocr_path = OCR_DIR / gold_path.name
        if not ocr_path.exists():
            continue

        gold = collapse(gold_path.read_text(encoding="utf-8"))
        hypo = collapse(ocr_path.read_text(encoding="utf-8"))
        total_gold += len(gold)

        buckets, pairs, examples = analyse(gold, hypo)
        all_buckets += buckets
        all_pairs += pairs

        print(f"\n{'='*78}\n{gold_path.stem[:70]}\n{'='*78}")
        errs = sum(buckets.values())
        for bucket, n in buckets.most_common():
            print(f"  {bucket:24} {n:5}  {n/errs:6.1%} of errors  "
                  f"{n/len(gold):6.2%} of chars")

        print("\n  first 12 differences:")
        for bucket, want, got, ctx in examples[:12]:
            print(f"    [{bucket:22}] want={want!r:14} got={got!r:14}")
            print(f"      ...{ctx}...")

    print(f"\n\n{'='*78}\nCOMBINED ({total_gold} gold chars)\n{'='*78}")
    errs = sum(all_buckets.values())
    for bucket, n in all_buckets.most_common():
        print(f"  {bucket:24} {n:5}  {n/errs:6.1%} of errors  "
              f"{n/total_gold:6.2%} of chars")

    print("\n  most frequent substitutions:")
    for (want, got), n in all_pairs.most_common(25):
        print(f"    {n:4}x  {describe(want) if len(want)==1 else repr(want):42}"
              f" -> {describe(got) if len(got)==1 else repr(got)}")


if __name__ == "__main__":
    main()