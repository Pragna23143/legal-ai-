"""FastAPI Router for Legal AI Demystifier.

Handles document upload, parsing, analysis pipelines, RAG Q&A,
sample contract presets, and project ZIP exports.
"""

import io
from pathlib import Path
import zipfile
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from api.schemas import ChatRequest, SetApiKeyRequest, TextIngestRequest
import config
from data.sample_contracts import SAMPLE_CONTRACTS, get_sample_by_id
from services.document_parser import DocumentParser, ParsedDocument
from services.gemini_service import GeminiLegalService
from services.rag_engine import RAGEngine

router = APIRouter(prefix="/api")

# In-memory document session state & service instances
parser = DocumentParser(
    chunk_size_tokens=config.CHUNK_SIZE_TOKENS,
    chunk_overlap_tokens=config.CHUNK_OVERLAP_TOKENS,
)
gemini_service = GeminiLegalService()
rag_engine = RAGEngine()

# Current loaded document state
current_doc: Optional[ParsedDocument] = None


def get_current_document() -> ParsedDocument:
    global current_doc
    if current_doc is None:
        # Auto-load the first sample contract by default so the system is immediately ready
        sample = SAMPLE_CONTRACTS[0]
        current_doc = parser.parse_text(sample["text"], filename=f"{sample['id']}.txt")
        rag_engine.set_document(current_doc)
    return current_doc


# =========================================================================
# System & Status Endpoints
# =========================================================================
@router.get("/status")
def get_system_status():
    doc = current_doc
    return {
        "status": "online",
        "gemini_live": gemini_service.is_live(),
        "active_model": gemini_service.model,
        "has_document": doc is not None,
        "current_document": {
            "filename": doc.filename if doc else None,
            "pages": doc.total_pages if doc else 0,
            "words": doc.total_words if doc else 0,
            "chunks": len(doc.chunks) if doc else 0,
            "estimated_tokens": doc.estimated_tokens if doc else 0,
        } if doc else None
    }


@router.post("/settings/key")
def update_gemini_api_key(payload: SetApiKeyRequest):
    new_key = payload.api_key.strip()
    gemini_service.set_api_key(new_key)
    return {
        "success": True,
        "gemini_live": gemini_service.is_live(),
        "message": "Gemini API key updated successfully." if gemini_service.is_live() else "API Key set but client init failed."
    }


# =========================================================================
# Document Ingestion Endpoints
# =========================================================================
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global current_doc
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported for upload. For other formats, use text ingestion."
        )

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        parsed = parser.parse_pdf_bytes(content, filename=file.filename)
        current_doc = parsed
        rag_engine.set_document(parsed)

        return {
            "success": True,
            "message": f"Successfully parsed {file.filename}",
            "metadata": {
                "filename": parsed.filename,
                "total_pages": parsed.total_pages,
                "total_words": parsed.total_words,
                "total_chars": parsed.total_chars,
                "estimated_tokens": parsed.estimated_tokens,
                "chunks_count": len(parsed.chunks),
            },
            "pages_preview": [
                {
                    "page_number": p.page_number,
                    "word_count": p.word_count,
                    "preview": p.text[:300] + ("..." if len(p.text) > 300 else "")
                }
                for p in parsed.pages
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@router.post("/ingest-text")
def ingest_text(payload: TextIngestRequest):
    global current_doc
    try:
        parsed = parser.parse_text(payload.text, filename=payload.filename or "contract.txt")
        current_doc = parsed
        rag_engine.set_document(parsed)

        return {
            "success": True,
            "message": f"Successfully ingested text: {payload.filename}",
            "metadata": {
                "filename": parsed.filename,
                "total_pages": parsed.total_pages,
                "total_words": parsed.total_words,
                "total_chars": parsed.total_chars,
                "estimated_tokens": parsed.estimated_tokens,
                "chunks_count": len(parsed.chunks),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest text: {str(e)}")


# =========================================================================
# Preloaded Samples Endpoints
# =========================================================================
@router.get("/samples")
def list_sample_contracts():
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "category": s["category"],
            "summary_hint": s["summary_hint"],
            "pdf_url": f"/api/samples/download/{s['id']}"
        }
        for s in SAMPLE_CONTRACTS
    ]


@router.post("/samples/load/{sample_id}")
def load_sample_contract(sample_id: str):
    global current_doc
    sample = get_sample_by_id(sample_id)
    parsed = parser.parse_text(sample["text"], filename=f"{sample['id']}.pdf")
    current_doc = parsed
    rag_engine.set_document(parsed)

    return {
        "success": True,
        "sample": {
            "id": sample["id"],
            "title": sample["title"],
            "category": sample["category"],
            "summary_hint": sample["summary_hint"]
        },
        "metadata": {
            "filename": parsed.filename,
            "total_pages": parsed.total_pages,
            "total_words": parsed.total_words,
            "estimated_tokens": parsed.estimated_tokens,
            "chunks_count": len(parsed.chunks),
        }
    }


@router.get("/samples/download/{sample_id}")
def download_sample_pdf(sample_id: str):
    sample_path = config.SAMPLES_DIR / f"{sample_id}.pdf"
    if not sample_path.exists():
        # Generate on the fly if needed
        from data.generate_sample_pdfs import generate_all_sample_pdfs
        generate_all_sample_pdfs()

    if sample_path.exists():
        return FileResponse(
            path=str(sample_path),
            filename=f"{sample_id}.pdf",
            media_type="application/pdf"
        )
    raise HTTPException(status_code=404, detail="Sample PDF not found.")


# =========================================================================
# Generative AI Legal Analysis Endpoints
# =========================================================================
@router.post("/analyze/summary")
def analyze_summary():
    doc = get_current_document()
    try:
        summary_result = gemini_service.generate_summary(doc.raw_text, filename=doc.filename)
        return summary_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation error: {str(e)}")


@router.post("/analyze/risks")
def analyze_risks_and_penalties():
    doc = get_current_document()
    try:
        risks_result = gemini_service.extract_penalties_and_obligations(doc.raw_text, filename=doc.filename)
        return risks_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk and penalty analysis error: {str(e)}")


@router.post("/analyze/compliance")
def analyze_compliance_and_audit():
    doc = get_current_document()
    try:
        compliance_result = gemini_service.audit_compliance_and_risks(doc.raw_text, filename=doc.filename)
        return compliance_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance audit error: {str(e)}")


# =========================================================================
# Interactive Context-Aware RAG Q&A Endpoint
# =========================================================================
@router.post("/chat")
def chat_with_document(payload: ChatRequest):
    doc = get_current_document()
    try:
        # Retrieve relevant chunks using RAG engine
        context_block, citations = rag_engine.build_rag_context(payload.question, top_k=payload.top_k or 4)

        # Generate answer with citations via Gemini
        answer_result = gemini_service.answer_rag_question(
            question=payload.question,
            rag_context=context_block,
            citations=citations
        )
        return answer_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Q&A error: {str(e)}")


# =========================================================================
# Document Text Viewer Endpoint
# =========================================================================
@router.get("/document/raw")
def get_raw_document():
    doc = get_current_document()
    return {
        "filename": doc.filename,
        "raw_text": doc.raw_text,
        "pages": [
            {
                "page_number": p.page_number,
                "text": p.text
            }
            for p in doc.pages
        ]
    }


# =========================================================================
# Downloadable Project ZIP Package Endpoint
# =========================================================================
@router.get("/download-zip")
def download_project_zip():
    """Generates an in-memory ZIP package of the entire project source code."""
    project_root = config.BASE_DIR

    zip_buffer = io.BytesIO()
    ignore_patterns = {
        "__pycache__", ".git", ".pytest_cache", ".venv", "venv", "env",
        ".DS_Store", "Thumbs.db", ".system_generated", "uploads"
    }

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in project_root.rglob("*"):
            # Check exclusions
            parts = file_path.relative_to(project_root).parts
            if any(part in ignore_patterns or part.endswith(".pyc") for part in parts):
                continue
            if file_path.is_file():
                arcname = str(Path("legal-ai-demystifier") / file_path.relative_to(project_root))
                zip_file.write(file_path, arcname=arcname)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=legal-ai-demystifier.zip"
        }
    )
