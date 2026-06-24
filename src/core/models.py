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