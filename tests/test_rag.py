"""Unit tests for RAGEngine retrieval and citations."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from services.document_parser import DocumentParser
from services.rag_engine import RAGEngine
from data.sample_contracts import SAMPLE_CONTRACTS


def test_rag_retrieval_and_citations():
    parser = DocumentParser(chunk_size_tokens=150, chunk_overlap_tokens=30)
    sample_text = SAMPLE_CONTRACTS[0]["text"]  # Enterprise SaaS
    doc = parser.parse_text(sample_text, filename="saas.txt")

    rag = RAGEngine(doc)
    results = rag.retrieve("liquidated damages penalty for reverse engineering", top_k=2)

    assert len(results) > 0
    top_chunk, score = results[0]
    assert score > 0
    assert "liquidated damages" in top_chunk.text.lower() or "damages" in top_chunk.text.lower()

    # Test build_rag_context
    context, citations = rag.build_rag_context("early termination fees", top_k=2)
    assert "[Citation:" in context
    assert len(citations) > 0
    assert "pages" in citations[0]
    assert "snippet" in citations[0]
