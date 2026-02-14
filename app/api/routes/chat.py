"""
Chat endpoint.
Natural language career advice: user sends a message, gets ML predictions + AI guidance.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.advisor import extract_profile_from_message, generate_chat_response
from app.core.model import predict_profile_type, recommend_skills

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    """Chat message from the user."""

    message: str = Field(..., description="User's career question or profile description")


class ChatResponse(BaseModel):
    """AI career advisor response."""

    response: str = Field(description="AI-generated career advice (markdown)")
    predicted_profile: str = Field(description="ML-predicted career profile")
    recommended_skills: list[str] = Field(description="Recommended skills to learn")


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat-based career advice.

    Flow:
    1. Groq extracts skills/experience from natural language
    2. XGBoost predicts career profile
    3. TF-IDF recommends skills
    4. Groq generates comprehensive conversational response
    """
    try:
        # Step 1: Extract structured info from the user's message
        extracted = extract_profile_from_message(request.message)

        skills = extracted.get("skills", "general")

        # Step 2: Run ML predictions
        profile_features = {
            "total_skills": skills,
            "years_of_experience": extracted.get("years_of_experience", 0),
            "education_degree": extracted.get("education", ""),
            "education_institution": "",
            "certifications": extracted.get("certifications", ""),
            "city": "",
            "state": "",
        }

        predicted_profile = predict_profile_type(profile_features)
        recommended = recommend_skills(skills, predicted_profile=predicted_profile) if skills != "general" else []

        # Step 3: Generate comprehensive AI response
        ai_response = generate_chat_response(
            user_message=request.message,
            predicted_profile=predicted_profile,
            recommended_skills=recommended,
            extracted_info=extracted,
        )

        return ChatResponse(
            response=ai_response,
            predicted_profile=predicted_profile,
            recommended_skills=recommended,
        )

    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your request: {str(e)}",
        )
