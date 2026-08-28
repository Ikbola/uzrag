"""OCR post-correction for Uzbek textbook scans.

Each stage is separable so its contribution to error rate can be measured
independently. Stages are ordered so that later ones see cleaner input.
"""

import re

from uznorm.normalize import normalize_apostrophes

# Tesseract-specific confusions observed in this corpus. Deliberately kept
# out of uznorm: these are OCR artifacts, not orthographic variants.
OCR_CONFUSIONS = {
    "\u00a3": "\u02bb",   # £ misread for the okina
}

# Cyrillic letters that are visually identical to Latin ones. Only applied
# inside otherwise-Latin words — see fix_cyrillic_bleed.
CYRILLIC_LOOKALIKES = str.maketrans({
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p",
    "\u0441": "c", "\u0443": "y", "\u0445": "x", "\u0410": "A",
    "\u0412": "B", "\u0415": "E", "\u041a": "K", "\u041c": "M",
    "\u041d": "H", "\u041e": "O", "\u0420": "P", "\u0421": "C",
    "\u0422": "T", "\u0425": "X",
})

CYRILLIC = re.compile(r"[\u0400-\u04FF]")
LATIN = re.compile(r"[a-zA-Z]")

# A figure caption line: "7-rasm. ..." or "12-jadval. ..."
FIGURE_CAPTION = re.compile(r"^\s*\d+\s*-\s*(rasm|jadval|chizma)\b.*$",
                            re.IGNORECASE)


def apply_uznorm(text: str) -> str:
    """Stage 1 — orthographic apostrophe normalization."""
    return normalize_apostrophes(text)


def dehyphenate(text: str) -> str:
    """Stage 2 — rejoin words split across line breaks.

    Only joins when a hyphen ends a line and the next line starts with a
    lowercase letter, which distinguishes typesetting hyphens from real
    compound hyphens that happen to fall at a line end.
    """
    return re.sub(r"(\w)[-\u2010\u2011]\s*\n\s*([a-zʻʼ])", r"\1\2", text)


def strip_figures(text: str) -> str:
    """Stage 3 — drop figure and table caption lines.

    Only unambiguous captions ("7-rasm. ...") are removed. Diagram label
    debris is left for the chunking stage, where page structure is
    available; a line-shape heuristic tried here removed valid verse lines
    and made error rates worse.
    """
    return "\n".join(
        line for line in text.split("\n")
        if not FIGURE_CAPTION.match(line)
    )


def fix_cyrillic_bleed(text: str) -> str:
    """Stage 4 — map lookalike Cyrillic letters inside Latin words."""
    def fix_word(m: re.Match) -> str:
        word = m.group(0)
        if CYRILLIC.search(word) and LATIN.search(word):
            return word.translate(CYRILLIC_LOOKALIKES)
        return word

    return re.sub(r"\S+", fix_word, text)


def fix_ocr_confusions(text: str) -> str:
    """Stage 5 — corpus-specific character substitutions."""
    for wrong, right in OCR_CONFUSIONS.items():
        text = text.replace(wrong, right)
    return text


STAGES = [
    ("uznorm", apply_uznorm),
    ("dehyphenate", dehyphenate),
    ("strip_figures", strip_figures),
    ("cyrillic_bleed", fix_cyrillic_bleed),
    ("ocr_confusions", fix_ocr_confusions),
]


def clean(text: str) -> str:
    for _, fn in STAGES:
        text = fn(text)
    return text