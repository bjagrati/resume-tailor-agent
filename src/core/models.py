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