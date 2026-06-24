"""FastAPI app exposing the résumé tailoring engine over HTTP."""
import sys
import tempfile
from pathlib import Path
from typing import Optional

# Make 'core.*' imports work when uvicorn launches us
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import fitz  # pymupdf
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from core.service import run_full_analysis, FullAnalysis


# ──────────────── Request/response models ────────────────

class AnalyzeTextRequest(BaseModel):
    """Request body when résumé is plain text."""
    resume_text: str = Field(..., description="Plain-text résumé content.")
    jd_text: str = Field(..., description="Plain-text job description.")


# ─────────────────────── App setup ───────────────────────

app = FastAPI(
    title="resume-tailor-agent",
    description="AI-powered résumé tailoring with hallucination-resistant rewrites",
    version="1.0.0",
)


# ───────────────────────── Routes ─────────────────────────

@app.get("/", tags=["meta"])
def root():
    return {
        "name": "resume-tailor-agent",
        "version": "1.0.0",
        "ui": "/ui",
        "docs": "/docs",
        "endpoints": ["/analyze/text", "/analyze/upload"],
    }


@app.post("/analyze/text", tags=["analyze"])
def analyze_text(req: AnalyzeTextRequest) -> FullAnalysis:
    """Analyze a résumé pasted as plain text against a job description."""
    if len(req.resume_text.strip()) < 100:
        raise HTTPException(status_code=400, detail="Résumé text seems too short to be meaningful.")
    if len(req.jd_text.strip()) < 100:
        raise HTTPException(status_code=400, detail="Job description seems too short to be meaningful.")
    
    try:
        return run_full_analysis(req.resume_text, req.jd_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@app.post("/analyze/upload", tags=["analyze"])
async def analyze_upload(
    resume_file: UploadFile = File(..., description="Résumé as .pdf, .txt, or .md"),
    jd_text: str = Form(..., description="Job description as plain text"),
) -> FullAnalysis:
    """Analyze an uploaded résumé file against a pasted job description."""
    suffix = Path(resume_file.filename).suffix.lower()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Use .pdf, .txt, or .md.",
        )
    
    contents = await resume_file.read()
    
    # Extract text based on type
    try:
        if suffix == ".pdf":
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(contents)
                    tmp_path = tmp.name
                doc = fitz.open(tmp_path)
                resume_text = "\n\n".join(page.get_text() for page in doc)
                doc.close()
            finally:
                if tmp_path:
                    Path(tmp_path).unlink(missing_ok=True)
        else:
            resume_text = contents.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {e}")
    
    if len(resume_text.strip()) < 100:
        raise HTTPException(status_code=400, detail="Extracted résumé text is too short.")
    if len(jd_text.strip()) < 100:
        raise HTTPException(status_code=400, detail="Job description is too short.")
    
    try:
        return run_full_analysis(resume_text, jd_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


# ───────────────────────── Static UI ─────────────────────
_STATIC_DIR = Path(__file__).parent / "static"
app.mount("/ui", StaticFiles(directory=str(_STATIC_DIR), html=True), name="ui")