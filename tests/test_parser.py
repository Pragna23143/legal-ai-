"""Unit tests for DocumentParser and token chunker."""

from pathlib import Path
import sys
import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))
from services.document_parser import DocumentParser
from data.sample_contracts import SAMPLE_CONTRACTS
import config


def test_clean_text():
    raw = "This is a broken obli-\ngation with multi\r\nlines and    extra   spaces."
    cleaned = DocumentParser.clean_text(raw)
    assert "obligation" in cleaned
    assert "\r" not in cleaned
    assert "  " not in cleaned


def test_parse_text_chunking():
    parser = DocumentParser(chunk_size_tokens=100, chunk_overlap_tokens=20)
    sample_text = SAMPLE_CONTRACTS[0]["text"]
    parsed = parser.parse_text(sample_text, filename="test_saas.txt")

    assert parsed.filename == "test_saas.txt"
    assert parsed.total_words > 200
    assert parsed.estimated_tokens > 200
    assert len(parsed.chunks) > 1
    assert parsed.chunks[0].chunk_id == 1
    assert parsed.chunks[0].start_page == 1


def test_parse_pdf_bytes():
    parser = DocumentParser(chunk_size_tokens=150, chunk_overlap_tokens=30)
    pdf_path = config.SAMPLES_DIR / "enterprise-saas.pdf"
    assert pdf_path.exists(), "Sample PDF must exist for this test"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    parsed = parser.parse_pdf_bytes(pdf_bytes, filename="enterprise-saas.pdf")
    assert parsed.total_pages >= 1
    assert len(parsed.pages) == parsed.total_pages
    assert "ENTERPRISE CLOUD SAAS" in parsed.raw_text
    assert len(parsed.chunks) >= 1
