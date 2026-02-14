"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field


class SkillsSchema(BaseModel):
    """Request schema for skill recommendation endpoint."""

    total_skills: str = Field(
        ..., description="Comma-separated list of skills possessed"
    )


class ProfileSchema(BaseModel):
    """Request schema for profile type prediction endpoint."""

    years_of_experience: int = Field(
        default=None, description="Total years of professional experience"
    )
    education_degree: str = Field(
        default=None, description="Highest education degree obtained"
    )
    education_institution: str = Field(
        default=None,
        description="Institution from which the highest degree was obtained",
    )
    total_skills: str = Field(
        default=None, description="Comma-separated list of skills possessed"
    )
    certifications: str = Field(
        default=None, description="Comma-separated list of certifications obtained"
    )
    city: str = Field(default=None, description="City of residence")
    state: str = Field(default=None, description="State of residence")


class ProfilePrediction(BaseModel):
    """Response schema for profile type prediction."""

    output_label: str = Field(..., description="Predicted profile type label")


class SkillRecommendationResponse(BaseModel):
    """Response schema for skill recommendations."""

    recommended_skills: list[str]
