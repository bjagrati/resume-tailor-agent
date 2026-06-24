"""Pydantic models defining the structured data shapes used across the project."""
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ──────────────────────── Tiny smoke test model ────────────────────────

class SkillExtraction(BaseModel):
    """A list of skills extracted from a piece of text."""
    skills: list[str] = Field(
        ...,
        description="A list of technical or professional skills mentioned in the text",
    )
    seniority_level: Literal["junior", "mid", "senior", "staff", "unspecified"] = Field(
        ...,
        description="The seniority level implied by the text, or 'unspecified' if not clear",
    )

# ──────────────────────── Job Description Analysis ────────────────────────

class JobAnalysis(BaseModel):
    """A structured analysis of a job description, breaking it into the
    components needed to evaluate a résumé's fit."""
    
    job_title: str = Field(
        ...,
        description="The exact job title from the posting (e.g., 'Senior Backend Engineer')",
    )
    
    seniority_level: Literal["intern", "junior", "mid", "senior", "staff", "principal", "unspecified"] = Field(
        ...,
        description="Seniority level. Choose 'unspecified' if the posting doesn't clearly indicate.",
    )
    
    required_skills: list[str] = Field(
        ...,
        description=(
            "Hard skills explicitly marked as required or must-have. "
            "Specific technologies, languages, frameworks, or tools — not soft skills. "
            "Use the CANONICAL category name when the JD lists examples. "
            "For example, 'experience with a major LLM provider (OpenAI, Anthropic, etc.)' "
            "should be extracted as a single skill 'LLM APIs', NOT as separate 'OpenAI' and 'Anthropic' skills. "
            "Strip parenthetical example lists: 'Vector databases (Pinecone, Weaviate)' becomes 'vector databases'. "
            "Do NOT include soft skills like 'communication skills' or 'team player'."
        ),
    )
    
    nice_to_have_skills: list[str] = Field(
        ...,
        description=(
            "Skills mentioned as preferred, bonus, plus, or nice-to-have — but not strictly required. "
            "Apply the same canonical-name and no-parentheticals rules as required_skills. "
            "If a skill is only mentioned once in a 'preferred' section, it goes here."
        ),
    )
    
    key_responsibilities: list[str] = Field(
        ...,
        description=(
            "The 3-7 most important responsibilities of this role, each as a single sentence. "
            "Focus on what the person will DO, not on company benefits or culture."
        ),
    )
    
    years_experience: Optional[int] = Field(
        None,
        description="Minimum years of experience required, as an integer. None if not specified.",
    )
    
    domain_keywords: list[str] = Field(
        ...,
        description=(
            "Domain-specific keywords that an ATS (applicant tracking system) would likely scan for. "
            "Include acronyms, methodologies, and industry jargon from the posting. "
            "Examples: 'CI/CD', 'microservices', 'GDPR', 'OAuth2', 'agile'."
        ),
    )

# ──────────────────────── Résumé Structure ────────────────────────

class ResumeBullet(BaseModel):
    """A single bullet point from a work experience entry."""
    text: str = Field(..., description="The bullet's text, cleaned of leading dashes or bullet characters.")


class Experience(BaseModel):
    """One job/work experience entry on the résumé."""
    company: str = Field(..., description="Company or organization name.")
    title: str = Field(..., description="The candidate's job title at this company.")
    location: Optional[str] = Field(None, description="Location, if mentioned.")
    start_date: Optional[str] = Field(None, description="Start date as written on the résumé (e.g., 'Jan 2022').")
    end_date: Optional[str] = Field(None, description="End date as written, or 'Present' if current.")
    bullets: list[ResumeBullet] = Field(
        ...,
        description="The bullet points describing what the candidate did at this job, in original order.",
    )


class Education(BaseModel):
    """One education entry."""
    institution: str = Field(..., description="School or university name.")
    degree: Optional[str] = Field(None, description="Degree type (e.g., 'B.S. Computer Science').")
    graduation_date: Optional[str] = Field(None, description="Graduation date as written on the résumé.")


class Resume(BaseModel):
    """A structured representation of a candidate's résumé."""
    
    full_name: Optional[str] = Field(None, description="The candidate's full name from the résumé header.")
    
    email: Optional[str] = Field(None, description="The candidate's email address, if shown.")
    
    location: Optional[str] = Field(None, description="The candidate's current location (city, state, or country).")
    
    summary: Optional[str] = Field(
        None,
        description=(
            "The candidate's summary/objective/profile section, if present. "
            "Just the prose, not any heading. Leave None if no summary is on the résumé."
        ),
    )
    
    experiences: list[Experience] = Field(
        ...,
        description="All work experience entries, in the order they appear on the résumé (typically reverse chronological).",
    )
    
    education: list[Education] = Field(
        ...,
        description="Education entries, in the order they appear on the résumé.",
    )
    
    skills: list[str] = Field(
        ...,
        description=(
            "Skills explicitly listed in any 'Skills' or 'Technical Skills' section. "
            "Use the canonical name. Do not invent skills based on what's mentioned in bullets — "
            "only include items from a dedicated skills section."
        ),
    )

# ──────────────────────── Gap Analysis ────────────────────────

class SkillMatch(BaseModel):
    """A skill from the JD and whether the résumé has evidence of it."""
    skill: str = Field(..., description="The canonical skill name from the JD.")
    present: bool = Field(..., description="True if the résumé shows evidence of this skill (in skills list or bullets).")
    evidence: Optional[str] = Field(
        None,
        description="The bullet text or skills-list entry that demonstrates this skill, if present. None if not found.",
    )


class GapAnalysis(BaseModel):
    """Comparison of a candidate's résumé against a job description."""
    
    alignment_score: int = Field(
        ...,
        ge=1, le=10,
        description=(
            "Overall alignment of the résumé to the job, 1-10. "
            "10 = perfect fit. 7-8 = strong match with minor gaps. "
            "5-6 = significant gaps but still plausible. 3-4 = major gaps. 1-2 = wrong job."
        ),
    )
    
    summary: str = Field(
        ...,
        description=(
            "2-3 sentence honest assessment of fit. Specific, not generic. "
            "Mention the strongest matches and the biggest gaps."
        ),
    )
    
    required_skill_matches: list[SkillMatch] = Field(
        ...,
        description="One entry for each required skill in the JD, showing whether the résumé has evidence of it.",
    )
    
    nice_to_have_matches: list[SkillMatch] = Field(
        ...,
        description="Same but for nice-to-have skills.",
    )
    
    strongest_aligned_bullets: list[str] = Field(
        ...,
        description=(
            "The 2-4 résumé bullets that best align with the JD's responsibilities. "
            "Quote them exactly as written in the résumé."
        ),
    )
    
    biggest_gaps: list[str] = Field(
        ...,
        description=(
            "The 2-5 most important gaps — required skills or responsibilities the résumé does not address. "
            "One sentence each, specific."
        ),
    )
    
    missing_keywords: list[str] = Field(
        ...,
        description=(
            "Domain keywords from the JD that don't appear anywhere in the résumé. "
            "These are ATS-relevant terms the candidate should consider adding."
        ),
    )