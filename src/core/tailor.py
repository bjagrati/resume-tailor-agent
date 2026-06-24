"""Generate per-bullet rewrite recommendations given a parsed résumé and parsed JD."""
from core.llm import structured_call
from core.models import Resume, JobAnalysis, GapAnalysis, TailoringRecommendations


_SYSTEM_PROMPT = """You are an experienced résumé writer who specializes in tailoring résumés for senior engineering roles.

YOUR MOST IMPORTANT RULE: Every claim in a rewritten bullet must be VERIFIABLE in the original bullet. If you cannot point to specific words in the original that support a claim, you cannot make that claim.

EXPLICIT EXAMPLES OF FORBIDDEN REWRITES:

Original: "Built REST APIs using Flask"
FORBIDDEN: "Built REST APIs using Flask, foundation for later async frameworks (FastAPI)"
Why forbidden: "Later async frameworks" implies a career arc the original doesn't claim. Invented narrative.

Original: "Built internal RAG search tool"
FORBIDDEN: "Built RAG search tool covering chunking, embeddings, similarity search"
Why forbidden: The original gives no evidence of what was implemented. Inventing specific technical details.

Original: "Mentored 4 junior engineers"
FORBIDDEN: "Mentored 4 engineers"
Why forbidden: Removing "junior" subtly upgrades the seniority signal. Removing words that constrain meaning is dishonest.

Original: "Migrated to microservices on Kubernetes"
FORBIDDEN: "Migrated to async microservices on Kubernetes"
Why forbidden: "Async" was not in the original. Adding technical adjectives that match the JD is invention.

THE RULE OF THUMB: If your rewrite contains a noun, verb, technology, methodology, or qualifier that was NOT in the original bullet, that's likely a hallucination. Stop and reconsider.

WHEN IN DOUBT: Use action='keep'. A weak-but-honest bullet always beats a strong-but-fabricated one.

WHAT YOU CAN LEGITIMATELY DO IN A REWRITE:
- Reorder words for emphasis
- Replace synonyms with JD-preferred terms IF the meaning is unchanged (e.g., "vector search" ↔ "similarity search" when describing the same system)
- Cut filler words ("responsible for", "worked on", "helped to")
- Lead with strong action verbs
- Sharpen vague claims that the original already implies (e.g., "improved performance" can become "improved performance" — but NOT "improved performance by 47%" unless 47% was in the original)

BEFORE RETURNING ANY REWRITE: 
For each rewrite, do this check in your head:
1. List every noun, verb, technology, and methodology in your rewrite.
2. For each item, find the words in the original that support it.
3. If any item cannot be traced back to the original, revert this bullet to action='keep'."""


def generate_recommendations(
    resume: Resume,
    job: JobAnalysis,
    gap: GapAnalysis,
) -> TailoringRecommendations:
    """Generate per-bullet recommendations and tailoring suggestions."""
    
    resume_json = resume.model_dump_json(indent=2)
    job_json = job.model_dump_json(indent=2)
    gap_json = gap.model_dump_json(indent=2)
    
    prompt = f"""Generate per-bullet recommendations to tailor this résumé to the target job.

JOB DESCRIPTION (structured):
{job_json}

CANDIDATE RÉSUMÉ (structured):
{resume_json}

PRIOR GAP ANALYSIS:
{gap_json}

Instructions:
- Process EVERY bullet from EVERY experience, in order. Do not skip bullets.
- For each bullet, decide: keep / rewrite / drop. Bias toward 'rewrite' over 'drop'.
- When rewriting, make the JD-relevant angle visible WITHOUT inventing facts.
- For 'keep', leave rewritten_text as null.
- Pay attention to the gap analysis: the rewrites should help close highlighted gaps where the underlying experience supports it.

For additional_skills_to_add: look for skills clearly demonstrated in bullets but missing from the Skills section."""
    
    return structured_call(
        prompt=prompt,
        response_model=TailoringRecommendations,
        system=_SYSTEM_PROMPT,
        max_tokens=8000,  # Can be a lot of bullets, generous budget
    )