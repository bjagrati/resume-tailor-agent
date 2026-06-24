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