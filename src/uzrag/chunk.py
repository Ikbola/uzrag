"""Split cleaned page text into retrievable chunks with citation metadata."""

import re
from dataclasses import dataclass, asdict
from pathlib import Path

TARGET = 700      
MAX = 1100        
MIN = 200         

# Section markers. Tesseract renders § inconsistently as $, 8, or 5.
SECTION = re.compile(
    r"^\s*(\d{1,3})\s*[-–—]\s*(§|\$|8|5)\s*\.?\s*(.{0,80})$"
)

# Exercises and problems share the same "N-word." shape.
EXERCISE = re.compile(
    r"^\s*(\d{1,3})\s*[-–—]\s*(topshiriq|masala|savol|mashq)\s*\.?",
    re.IGNORECASE,
)

SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")


@dataclass
class Chunk:
    text: str
    book: str
    page: int
    section: str | None
    chunk_index: int = 0
    kind: str = "text"

    @property
    def citation(self) -> str:
        base = f"{self.book}, {self.page}-bet"
        return f"{base}, {self.section}-§" if self.section else base


def is_prose(text: str) -> bool:
    """Reject covers, title pages, index pages, and figure debris."""
    stripped = text.strip()
    if len(stripped) < 200:
        return False
    letters = sum(ch.isalpha() for ch in stripped)
    if letters / len(stripped) < 0.65:
        return False
    words = stripped.split()
    if not words:
        return False
    avg_word = sum(len(w) for w in words) / len(words)
    return 3.0 <= avg_word <= 12.0


def split_long(text: str) -> list[str]:
    """Break an over-long paragraph on sentence boundaries."""
    sentences = SENTENCE_END.split(text)
    out, current = [], ""
    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > TARGET:
            out.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        out.append(current.strip())
    return [c for c in out if c]


def chunk_page(text: str, book: str, page: int,
               section: str | None) -> tuple[list[Chunk], str | None]:
    """Chunk one page. Returns chunks and the section in force at page end."""
    chunks: list[Chunk] = []
    if not is_prose(text):
        return chunks, section

    buffer = ""
    kind = "text"
    
    for para in re.split(r"\n\s*\n", text):
        para = " ".join(para.split())
        if not para:
            continue

        heading = SECTION.match(para)
        if heading:
            section = heading.group(1)

        kind = "exercise" if EXERCISE.match(para) else "text"

        if len(para) > MAX:
            if buffer:
                chunks.append(Chunk(buffer, book, page, section, 0))
                buffer = ""
            for piece in split_long(para):
                chunks.append(Chunk(piece, book, page, section, 0))
            continue

        if len(buffer) + len(para) + 1 <= TARGET or len(buffer) < MIN:
            buffer = f"{buffer} {para}".strip()
        else:
            chunks.append(Chunk(buffer, book, page, section, 0))
            buffer = para

    if buffer:
        if len(buffer) < MIN and chunks and len(chunks[-1].text) + len(buffer) <= MAX:
            chunks[-1].text += " " + buffer
        elif len(buffer) >= MIN:
            chunks.append(Chunk(buffer, book, page, section, kind, 0))
    

    return chunks, section