"""Render textbook pages to images and OCR them with Tesseract.

Usage:
    python scripts/ocr_probe.py --pages 3 4 5
"""

import argparse
import subprocess
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

PDF_DIR = Path("data/pdfs")
PAGE_DIR = Path("data/pages")
OCR_DIR = Path("data/ocr")
DPI = 300
LANG = "uzb"


def render(pdf: Path, pages: list[int]) -> list[Path]:
    out = []
    for n in pages:
        dest = PAGE_DIR / f"{pdf.stem}_p{n:03}.png"
        if dest.exists():
            out.append(dest)
            continue
        images = convert_from_path(pdf, dpi=DPI, first_page=n, last_page=n)
        if not images:
            print(f"  page {n} not found in {pdf.name}")
            continue
        images[0].save(dest)
        out.append(dest)
    return out


def ocr(image: Path) -> str:
    return pytesseract.image_to_string(Image.open(image), lang=LANG)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, nargs="+", default=[10, 11, 12])
    args = ap.parse_args()

    for d in (PAGE_DIR, OCR_DIR):
        d.mkdir(parents=True, exist_ok=True)

    print("tesseract:", subprocess.run(
        ["tesseract", "--version"], capture_output=True, text=True
    ).stdout.splitlines()[0])

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    print(f"{len(pdfs)} PDFs\n")

    for pdf in pdfs:
        print(f"{pdf.name}")
        for img in render(pdf, args.pages):
            text = ocr(img)
            dest = OCR_DIR / f"{img.stem}.txt"
            dest.write_text(text, encoding="utf-8")

            w, h = Image.open(img).size
            preview = " ".join(text.split())[:90]
            print(f"  p{img.stem[-3:]}  {w}x{h}  {len(text):5} chars  {preview}")
        print()


if __name__ == "__main__":
    main()