"""Top-level orchestration: takes raw inputs, runs the full pipeline, returns a complete analysis."""
from pathlib import Path

from pydantic import BaseModel

from core.llm import structured_call
from core.models import JobAnalysis, Resume, GapAnalysis, TailoringRecommendations
from core.comparator import analyze_gap
from core.tailor import generate_recommendations


# Path trick consistent with the rest of the codebase
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class FullAnalysis(BaseModel):
    """The complete tailoring analysis bundled together."""
    job: JobAnalysis
    resume: Resume
    gap: GapAnalysis
    recommendations: TailoringRecommendations


def parse_job_description(jd_text: str) -> JobAnalysis:
    """Parse a raw job description into a structured JobAnalysis."""
    return structured_call(
        prompt=(
            "Analyze this job description carefully. Extract all required components into the structured format.\n\n"
            f"Job description:\n{jd_text}"
        ),
        response_model=JobAnalysis,
        max_tokens=3000,
    )


def parse_resume(resume_text: str) -> Resume:
    """Parse a raw résumé (plain text) into a structured Resume."""
    return structured_call(
        prompt=(
            "Parse this résumé carefully into the structured format. "
            "Preserve bullet text exactly as written; only strip leading dashes or bullet characters.\n\n"
            f"Résumé:\n{resume_text}"
        ),
        response_model=Resume,
        max_tokens=4000,
    )


def run_full_analysis(resume_text: str, jd_text: str) -> FullAnalysis:
    """End-to-end: takes raw text, returns complete structured analysis with recommendations."""
    
    print("  [1/4] Parsing job description...")
    job = parse_job_description(jd_text)
    
    print("  [2/4] Parsing résumé...")
    resume = parse_resume(resume_text)
    
    print("  [3/4] Analyzing gaps...")
    gap = analyze_gap(resume, job)
    
    print("  [4/4] Generating bullet recommendations...")
    recommendations = generate_recommendations(resume, job, gap)
    
    return FullAnalysis(
        job=job,
        resume=resume,
        gap=gap,
        recommendations=recommendations,
    )