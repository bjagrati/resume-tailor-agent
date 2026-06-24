"""Gap analysis: takes a parsed JD and parsed résumé, returns structured comparison."""
from core.llm import structured_call
from core.models import JobAnalysis, Resume, GapAnalysis


_SYSTEM_PROMPT = """You are an experienced technical recruiter and résumé reviewer.
You give honest, specific feedback — not generic flattery. When a candidate's
résumé doesn't match a role, you say so directly. When it does match well, you
point to the specific evidence. You never invent skills the candidate doesn't have."""


def analyze_gap(resume: Resume, job: JobAnalysis) -> GapAnalysis:
    """Compare a parsed résumé to a parsed job description."""
    
    # Pre-serialize both objects to JSON for the prompt.
    # model_dump_json gives clean JSON; indent=2 makes it readable to Claude.
    resume_json = resume.model_dump_json(indent=2)
    job_json = job.model_dump_json(indent=2)
    
    prompt = f"""Compare this candidate's résumé against the job they're applying for.

JOB DESCRIPTION (structured):
{job_json}

CANDIDATE RÉSUMÉ (structured):
{resume_json}

For each required skill in the JD, check if the résumé has evidence of it (either in the skills list OR in experience bullets). Cite the specific bullet or skill-list entry as evidence when present.

Be honest in the alignment_score — don't inflate. A score of 7 means real fit with a few gaps, not "everyone gets a 7."

For biggest_gaps, focus on REQUIRED skills or important responsibilities that the résumé doesn't address at all. Don't list nice-to-haves as gaps."""
    
    return structured_call(
        prompt=prompt,
        response_model=GapAnalysis,
        system=_SYSTEM_PROMPT,
        max_tokens=4000,
    )