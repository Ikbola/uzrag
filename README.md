# uzrag — Retrieval over Uzbek school textbooks

A retrieval system that takes a question in Uzbek and returns relevant passages from 10th-grade textbooks, with book, page, and section citations. Built on OCR'd scanned PDFs in a language with minimal existing tooling.

## Results

| Retrieval method | Recall@1 | Recall@3 | Recall@5 | Recall@10 |
|---|---|---|---|---|
| Semantic only (MiniLM) | 7.5% | 20.0% | 30.0% | 37.5% |
| **Hybrid (semantic + BM25)** | **32.5%** | **55.0%** | **70.0%** | **85.0%** |

Evaluated against 40 hand-written questions across three textbooks. Recall@5 is the primary metric: it measures how often the correct passage appears in the top 5 results, which is what a downstream answer-generation model would see.

Adding BM25 keyword matching to semantic search improved recall@5 by 40 points — the single largest improvement in the pipeline. Keyword queries like *"xlorofill tarkibida qaysi element bor?"* are nearly invisible to semantic search but trivial for BM25; conceptual questions like *"Darvin moslanishlarni qanday tushuntirgan?"* benefit from both.

Recall numbers are a lower bound: the eval set marks one chunk as correct per question, but several failures retrieved a different chunk containing an equally valid answer.

## OCR pipeline

The textbooks are page scans with no text layer. Tesseract with the Uzbek language pack produces the raw text; a correction pipeline reduces error rates before indexing.

| Stage | CER | ΔCER | WER | ΔWER |
|---|---|---|---|---|
| Raw Tesseract | 3.99% | | 14.10% | |
| + uznorm apostrophes | 3.73% | −0.26% | 12.14% | −1.96% |
| + dehyphenation | 2.99% | −0.74% | 6.78% | −5.36% |
| + OCR-specific fixes | 2.93% | −0.06% | 6.57% | −0.21% |

Measured against two hand-typed gold pages. Genuine letter-recognition errors account for under 0.2% of characters; the remainder is apostrophe variants, line-break hyphens, and figure-label debris.

Dehyphenation contributes the largest WER improvement (−5.36 points) because each hyphen breaks exactly one word. Apostrophe normalization via [uznorm](https://github.com/Ikbola/uznorm) contributes −1.96 WER — notably more impactful here than in the [uznews](https://github.com/Ikbola/uznews) classification task, where a fine-tuned transformer barely noticed the difference. Retrieval is lexical in a way classification is not: a query for `oʻsimlik` must match the indexed form exactly.

## Corpus

Three 10th-grade textbooks, OCR'd at 300 DPI:

| Book | Pages | Characters | Chunks |
|---|---|---|---|
| Adabiyot (literature) | 314 | 571,919 | 1,016 |
| Biologiya (biology) | 240 | 458,660 | 837 |
| Oʻzbekiston tarixi (history) | 144 | 259,725 | 493 |
| **Total** | **698** | **1,290,304** | **2,346** |

Chunks are paragraph-based with a ~700 character target and 1,100 character cap, falling back to sentence-boundary splitting for long paragraphs. Section markers (§) are tracked across pages and attached as citation metadata.

Textbook PDFs are not redistributed. `data/` is gitignored; the OCR and chunking scripts are published so the corpus can be rebuilt from the source PDFs.

## Architecture

```
PDF scans
  │
  ├─ Tesseract OCR (uzb, 300 DPI)
  │
  ├─ Correction pipeline
  │    ├─ uznorm apostrophe normalization
  │    ├─ dehyphenation across line breaks
  │    ├─ figure caption removal
  │    └─ OCR-specific character fixes
  │
  ├─ Paragraph chunking with section tracking
  │
  ├─ Dual indexing
  │    ├─ Semantic: paraphrase-multilingual-MiniLM-L12-v2 → FAISS
  │    └─ Keyword:  BM25 (rank-bm25)
  │
  ├─ Reciprocal Rank Fusion (k=60)
  │
  └─ FastAPI /search endpoint with citations
```

Reciprocal Rank Fusion is used rather than score averaging because cosine similarity and BM25 scores live on incompatible scales. RRF converts each system's output to ranks and combines those, so a chunk ranked 2nd by both arms outranks one ranked 1st by a single arm.

## Usage

### Setup

```bash
# system dependencies (macOS)
brew install tesseract tesseract-lang poppler

# Python
pip install -e ".[dev]"
```

### Build the corpus

Requires textbook PDFs in `data/pdfs/`.

```bash
python scripts/ocr_corpus.py         
python scripts/build_chunks.py
python scripts/build_index.py        
```

### Run the API

```bash
uvicorn uzrag.api:app --reload
```

`POST /search` with `{"question": "..."}` returns ranked passages with book, page, and section citations. Interactive docs at `http://127.0.0.1:8000/docs`.

### Run evaluations

```bash
python scripts/score_stages.py        # OCR correction pipeline
python scripts/eval_retrieval.py      # semantic-only retrieval
python scripts/eval_hybrid.py         # hybrid retrieval
pytest                                # API contract tests
```

## Limitations

- **Two-page gold set.** OCR error rates are measured against two hand-typed pages — enough for feasibility but not for precise deltas. Expanding to 6–8 pages would tighten the numbers.
- **Single-target eval.** Each question has one marked correct chunk. Questions with valid answers in multiple chunks are penalized, making recall a lower bound.
- **No answer generation.** This is a retrieval system, not a question-answering system. Adding an LLM to generate answers from retrieved passages is the natural next step but out of scope.
- **Section detection is approximate.** Tesseract renders § as `$`, `8`, or `5` inconsistently; the regex catches most but not all markers. 36% of chunks carry section metadata.
- **Verse and figure content.** Two-column verse pages OCR correctly but chunk awkwardly. Figure labels and captions produce debris that passes the prose filter in some cases.
- **Single-seed measurements.** Retrieval metrics are deterministic, but the OCR deltas come from one gold set with no variance estimate.

## Connection to other projects

This is the third in a sequence:

- **[uznorm](https://github.com/Ikbola/uznorm)** — Apostrophe normalization for Uzbek Latin script. Used here as an OCR post-correction stage. Building uzrag exposed a missing character mapping (U+2018) in uznorm.
- **[uznews](https://github.com/Ikbola/uznews)** — Uzbek news topic classification. Found that apostrophe normalization has minimal effect on a fine-tuned transformer classifier; here, the same normalization measurably improves retrieval, because retrieval depends on exact lexical matching where classification does not.
- **uzrag** (this project) — Retrieval over scanned textbooks, where the OCR and normalization problems from the first two projects converge.

## Repository

```
uzrag/
├── scripts/
│   ├── ocr_probe.py          # OCR feasibility probe on sample pages
│   ├── ocr_corpus.py         # full-corpus OCR with cleaning
│   ├── score_ocr.py          # CER/WER against gold pages
│   ├── error_analysis.py     # error inventory by cause
│   ├── score_stages.py       # per-stage correction measurement
│   ├── build_chunks.py       # paragraph chunking
│   ├── build_index.py        # FAISS index construction
│   ├── write_eval.py         # eval set generation
│   ├── eval_retrieval.py     # semantic-only evaluation
│   └── eval_hybrid.py        # hybrid evaluation
│
├── src/uzrag/
│   ├── clean.py              # OCR correction pipeline
│   ├── chunk.py              # chunking with citation metadata
│   ├── index.py              # FAISS semantic index
│   ├── hybrid.py             # BM25 + semantic fusion
│   └── api.py                # FastAPI endpoints
│
├── tests/
│   └── test_search_api.py    # API contract tests
│
├── data/                     # gitignored
│   ├── pdfs/                 # source textbook scans
│   ├── corpus/               # OCR'd text, one file per page
│   ├── gold/                 # hand-typed ground truth pages
│   ├── chunks.jsonl          # chunked corpus
│   ├── eval.jsonl            # 40 question-answer pairs
│   └── index.faiss           # vector index
│
├── results/
│   ├── retrieval_eval.json   # semantic-only metrics
│   └── hybrid_eval.json      # hybrid metrics
│
├── docs/
│   └── sources.md            # corpus provenance
│
└── pyproject.toml
```
