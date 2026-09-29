"""Legal AI Demystifier - Main FastAPI Application Server.

Generative AI platform for demystifying complex legal documents, agreements,
penalties, and compliance risks using PyMuPDF and Google Gemini API.
"""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from api.routes import router as api_router
import config
from data.generate_sample_pdfs import generate_all_sample_pdfs

# Configure logging
logging.basicConfig(
    level=logging.INFO if config.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("legal_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing Legal AI Demystifier application...")
    try:
        generate_all_sample_pdfs()
        logger.info("Sample contract PDFs validated.")
    except Exception as e:
        logger.warning(f"Could not generate sample PDFs at startup: {e}")

    yield

    # Teardown tasks
    logger.info("Shutting down Legal AI Demystifier.")


app = FastAPI(
    title="Generative AI for Demystifying Legal Documents",
    description="Enterprise LLM document processing engine translating complex agreements into plain English, uncovering hidden penalties, and conducting compliance audits.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local development and API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router)

# Mount static directory for HTML, CSS, JavaScript assets
if config.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = config.STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Legal AI Demystifier Backend Running. Static index.html not yet built."}


if __name__ == "__main__":
    print("=" * 70)
    print("  ⚖️  GENERATIVE AI FOR DEMYSTIFYING LEGAL DOCUMENTS")
    print(f"  🌐 Server URL: http://{config.HOST}:{config.PORT}")
    print(f"  🤖 Active Gemini Model: {config.GEMINI_MODEL}")
    print(f"  🔑 Live Gemini API: {'ENABLED' if config.GEMINI_API_KEY else 'OFFLINE SIMULATED (Enter key in UI)'}")
    print("=" * 70)
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)
