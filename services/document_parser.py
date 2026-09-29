"""Document Ingestion, Text Extraction, and Token Chunking Service using PyMuPDF.

Extracts text from PDF documents page by page, cleans formatting,
detects legal headings, and produces token-aware sliding window chunks
preserving document and page metadata.
"""

from dataclasses import dataclass, field
import io
import re
from typing import Any, Dict, List, Optional
import pymupdf  # PyMuPDF


@dataclass
class DocumentChunk:
    chunk_id: int
    text: str
    start_page: int
    end_page: int
    token_count: int
    char_count: int
    section_heading: Optional[str] = None


@dataclass
class ParsedPage:
    page_number: int
    text: str
    word_count: int
    char_count: int


@dataclass
class ParsedDocument:
    filename: str
    total_pages: int
    total_words: int
    total_chars: int
    estimated_tokens: int
    raw_text: str
    pages: List[ParsedPage] = field(default_factory=list)
    chunks: List[DocumentChunk] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "total_pages": self.total_pages,
            "total_words": self.total_words,
            "total_chars": self.total_chars,
            "estimated_tokens": self.estimated_tokens,
            "pages": [
                {
                    "page_number": p.page_number,
                    "word_count": p.word_count,
                    "char_count": p.char_count,
                    "preview": p.text[:200] + "..." if len(p.text) > 200 else p.text
                }
                for p in self.pages
            ],
            "chunks_count": len(self.chunks),
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "text": c.text,
                    "start_page": c.start_page,
                    "end_page": c.end_page,
                    "token_count": c.token_count,
                    "section_heading": c.section_heading
                }
                for c in self.chunks
            ]
        }


class DocumentParser:
    def __init__(self, chunk_size_tokens: int = 400, chunk_overlap_tokens: int = 80):
        self.chunk_size_tokens = chunk_size_tokens
        self.chunk_overlap_tokens = chunk_overlap_tokens

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic token estimation: roughly 0.75 words per token or ~4 chars per token."""
        words = len(re.findall(r"\w+", text))
        chars = len(text)
        # Blend word and character heuristics for balanced estimation
        return max(1, int(max(words * 1.3, chars / 4)))

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize linebreaks, remove hyphenation at line breaks, strip excessive whitespace."""
        # Unhyphenate words broken across lines: e.g. "obli-\ngation" -> "obligation"
        cleaned = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)
        # Normalize carriage returns
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse 3+ newlines into 2
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        # Collapse multiple inline spaces/tabs
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        return cleaned.strip()

    def parse_pdf_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> ParsedDocument:
        """Ingest a PDF from raw bytes using PyMuPDF."""
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        pages: List[ParsedPage] = []
        raw_text_parts: List[str] = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text")
            cleaned_page = self.clean_text(page_text)
            words = len(cleaned_page.split())
            chars = len(cleaned_page)

            pages.append(
                ParsedPage(
                    page_number=page_idx + 1,
                    text=cleaned_page,
                    word_count=words,
                    char_count=chars,
                )
            )
            raw_text_parts.append(f"--- [Page {page_idx + 1}] ---\n{cleaned_page}")

        full_raw_text = "\n\n".join(raw_text_parts)
        doc.close()

        chunks = self.chunk_pages(pages)

        total_words = sum(p.word_count for p in pages)
        total_chars = sum(p.char_count for p in pages)
        estimated_tokens = self.estimate_tokens(full_raw_text)

        return ParsedDocument(
            filename=filename,
            total_pages=len(pages),
            total_words=total_words,
            total_chars=total_chars,
            estimated_tokens=estimated_tokens,
            raw_text=full_raw_text,
            pages=pages,
            chunks=chunks,
        )

    def parse_text(self, text: str, filename: str = "pasted_contract.txt") -> ParsedDocument:
        """Parse raw or pasted text, simulating single or multi-page layout if page breaks exist."""
        cleaned = self.clean_text(text)
        # Check if page break markers exist
        page_splits = re.split(r"(?:---+\s*\[?Page\s*(\d+)\]?\s*---+)|(?:\f)", cleaned, flags=re.IGNORECASE)

        pages: List[ParsedPage] = []
        if len(page_splits) > 1:
            # Multi-page detected
            current_num = 1
            for part in page_splits:
                if not part:
                    continue
                if part.isdigit():
                    current_num = int(part)
                    continue
                part_clean = part.strip()
                if part_clean:
                    pages.append(
                        ParsedPage(
                            page_number=current_num,
                            text=part_clean,
                            word_count=len(part_clean.split()),
                            char_count=len(part_clean),
                        )
                    )
                    current_num += 1
        else:
            # Approximate pages based on ~500 words per page if text is long
            words = cleaned.split()
            words_per_page = 450
            if len(words) > words_per_page:
                for i in range(0, len(words), words_per_page):
                    page_slice = " ".join(words[i : i + words_per_page])
                    pages.append(
                        ParsedPage(
                            page_number=(i // words_per_page) + 1,
                            text=page_slice,
                            word_count=len(page_slice.split()),
                            char_count=len(page_slice),
                        )
                    )
            else:
                pages.append(
                    ParsedPage(
                        page_number=1,
                        text=cleaned,
                        word_count=len(words),
                        char_count=len(cleaned),
                    )
                )

        chunks = self.chunk_pages(pages)
        total_words = sum(p.word_count for p in pages)
        total_chars = sum(p.char_count for p in pages)
        estimated_tokens = self.estimate_tokens(cleaned)

        raw_formatted = "\n\n".join(
            [f"--- [Page {p.page_number}] ---\n{p.text}" for p in pages]
        )

        return ParsedDocument(
            filename=filename,
            total_pages=len(pages),
            total_words=total_words,
            total_chars=total_chars,
            estimated_tokens=estimated_tokens,
            raw_text=raw_formatted,
            pages=pages,
            chunks=chunks,
        )

    def chunk_pages(self, pages: List[ParsedPage]) -> List[DocumentChunk]:
        """Produce overlapping chunks while retaining exact page origin numbers."""
        # First flatten sentences/clauses with page tracking
        tokens_with_meta = []
        heading_pattern = re.compile(
            r"^(?:(?:Section|Article|Clause|\d+\.|\([a-z]\))\s+[A-Z0-9\s,\-\:]{3,50}|[A-Z\s]{4,40}:?$)",
            re.MULTILINE,
        )

        current_heading = "General Terms"
        for page in pages:
            lines = page.text.split("\n")
            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue
                # Check if this line is a heading
                if heading_pattern.match(line_str) and len(line_str) < 80:
                    current_heading = line_str

                # Split line into words
                words = line_str.split()
                for w in words:
                    tokens_with_meta.append((w, page.page_number, current_heading))

        if not tokens_with_meta:
            return []

        chunks: List[DocumentChunk] = []
        chunk_id = 1
        step = max(1, self.chunk_size_tokens - self.chunk_overlap_tokens)
        total_tokens = len(tokens_with_meta)

        for i in range(0, total_tokens, step):
            window = tokens_with_meta[i : i + self.chunk_size_tokens]
            if not window:
                break

            words_in_window = [item[0] for item in window]
            pages_in_window = [item[1] for item in window]
            headings_in_window = [item[2] for item in window if item[2]]

            chunk_text = " ".join(words_in_window)
            start_page = min(pages_in_window)
            end_page = max(pages_in_window)
            token_count = self.estimate_tokens(chunk_text)
            char_count = len(chunk_text)
            primary_heading = headings_in_window[0] if headings_in_window else "Terms & Conditions"

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    start_page=start_page,
                    end_page=end_page,
                    token_count=token_count,
                    char_count=char_count,
                    section_heading=primary_heading,
                )
            )
            chunk_id += 1

            if i + self.chunk_size_tokens >= total_tokens:
                break

        return chunks
