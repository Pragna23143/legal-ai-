"""Context-Aware RAG Engine for Legal Document Question-Answering.

Retrieves top-k relevant clauses/chunks using a weighted legal BM25-style
relevance scorer and formats citation-rich context blocks for Gemini.
"""

from collections import Counter
import math
import re
from typing import Any, Dict, List, Optional, Tuple
from services.document_parser import DocumentChunk, ParsedDocument


class RAGEngine:
    def __init__(self, document: Optional[ParsedDocument] = None):
        self.document = document
        self.chunks: List[DocumentChunk] = document.chunks if document else []
        self._build_index()

    def set_document(self, document: ParsedDocument):
        self.document = document
        self.chunks = document.chunks
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase, clean alphanumeric tokens
        tokens = re.findall(r"[a-zA-Z0-9_\-\$]{2,}", text.lower())
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
            "with", "by", "from", "up", "about", "into", "over", "after", "is", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
            "did", "will", "would", "shall", "should", "may", "might", "must", "can",
            "could", "that", "which", "who", "whom", "this", "these", "those", "it",
            "its", "as", "if", "each", "all", "both", "any", "other", "such"
        }
        return [t for t in tokens if t not in stopwords]

    def _build_index(self):
        """Constructs an inverted index and document frequencies for BM25-style scoring."""
        self.doc_lengths = []
        self.inverted_index = {}  # term -> list of (chunk_idx, term_freq)
        self.doc_count = len(self.chunks)

        if self.doc_count == 0:
            self.avg_doc_length = 0
            return

        for idx, chunk in enumerate(self.chunks):
            tokens = self._tokenize(chunk.text)
            self.doc_lengths.append(len(tokens))
            freqs = Counter(tokens)

            for term, count in freqs.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                self.inverted_index[term].append((idx, count))

        self.avg_doc_length = sum(self.doc_lengths) / max(1, self.doc_count)

    def retrieve(self, query: str, top_k: int = 4) -> List[Tuple[DocumentChunk, float]]:
        """Retrieve top_k chunks matching the query using BM25 relevance scoring."""
        if not self.chunks:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            # Return first few chunks if empty query
            return [(chunk, 0.5) for chunk in self.chunks[:top_k]]

        # BM25 parameters
        k1 = 1.5
        b = 0.75

        scores = [0.0] * self.doc_count

        # High-value legal keywords to boost
        legal_boosts = {
            "penalty": 2.2, "liquidated": 2.5, "damages": 2.0, "termination": 2.0,
            "liability": 2.0, "indemnify": 2.5, "indemnification": 2.5,
            "confidential": 1.8, "non-compete": 2.5, "non-solicitation": 2.5,
            "warranty": 1.8, "breach": 2.2, "arbitration": 2.0, "renewal": 2.0,
            "notice": 1.8, "default": 2.0, "governing": 1.8, "jurisdiction": 1.8,
            "payment": 1.8, "fee": 1.8, "fees": 1.8, "interest": 1.8, "audit": 2.0
        }

        for term in query_tokens:
            if term in self.inverted_index:
                postings = self.inverted_index[term]
                df = len(postings)
                idf = math.log(1 + (self.doc_count - df + 0.5) / (df + 0.5))

                boost = legal_boosts.get(term, 1.0)

                for chunk_idx, tf in postings:
                    doc_len = self.doc_lengths[chunk_idx]
                    denom = tf + k1 * (1 - b + b * (doc_len / max(1.0, self.avg_doc_length)))
                    term_score = idf * ((tf * (k1 + 1)) / denom) * boost
                    scores[chunk_idx] += term_score

        # Also give small boost if query phrase appears in section_heading
        for idx, chunk in enumerate(self.chunks):
            if chunk.section_heading:
                heading_lower = chunk.section_heading.lower()
                for q in query_tokens:
                    if q in heading_lower:
                        scores[idx] += 1.5

        # Rank chunks by score descending
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for idx in ranked_indices:
            if scores[idx] > 0 or len(results) < min(top_k, len(self.chunks)):
                results.append((self.chunks[idx], scores[idx]))
            if len(results) >= top_k:
                break

        return results

    def build_rag_context(self, query: str, top_k: int = 4) -> Tuple[str, List[Dict[str, Any]]]:
        """Constructs a structured context block with clear citation markers for Gemini prompt injection."""
        scored_chunks = self.retrieve(query, top_k=top_k)
        if not scored_chunks:
            return "No document text loaded.", []

        context_blocks = []
        citations = []

        for chunk, score in scored_chunks:
            page_info = (
                f"Page {chunk.start_page}"
                if chunk.start_page == chunk.end_page
                else f"Pages {chunk.start_page}-{chunk.end_page}"
            )
            heading_info = f" [Section: {chunk.section_heading}]" if chunk.section_heading else ""
            citation_tag = f"[Citation: Chunk #{chunk.chunk_id} | {page_info}{heading_info}]"

            context_blocks.append(f"{citation_tag}\n{chunk.text}")

            citations.append({
                "chunk_id": chunk.chunk_id,
                "pages": page_info,
                "start_page": chunk.start_page,
                "end_page": chunk.end_page,
                "section": chunk.section_heading,
                "score": round(score, 3),
                "snippet": chunk.text[:220] + ("..." if len(chunk.text) > 220 else "")
            })

        full_context = "\n\n====================\n\n".join(context_blocks)
        return full_context, citations
