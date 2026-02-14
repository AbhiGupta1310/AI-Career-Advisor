"""
Groq-powered AI Career Advisor.
Handles both structured career advice and chat-based natural language queries.
Uses Llama 3.3 70B via Groq's free API.
"""

from groq import Groq

from app.core.config import settings


def _get_groq_client() -> Groq:
    """Get a Groq client instance."""
    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com"
        )
    return Groq(api_key=settings.groq_api_key)


def extract_profile_from_message(message: str) -> dict:
    """
    Use Groq to extract structured career profile info from a natural language message.

    Returns a dict with: skills, years_of_experience, education, certifications
    """
    client = _get_groq_client()

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": """You are a data extraction assistant. Extract career profile information from the user's message.
Return ONLY a valid JSON object with these fields:
- "skills": comma-separated string of technical skills mentioned (e.g., "Python, SQL, Docker")
- "years_of_experience": integer (0 if not mentioned)
- "education": string (e.g., "Bachelor's", "Master's", "PhD", or "" if not mentioned)
- "certifications": comma-separated string (or "" if none mentioned)

Be thorough in extracting skills — include programming languages, frameworks, tools, methodologies, and soft skills.
If the user asks a general career question without listing skills, extract what you can and set skills to "general".

Return ONLY the JSON. No markdown, no explanation.""",
            },
            {"role": "user", "content": message},
        ],
        temperature=0.1,
        max_tokens=256,
    )

    import json

    try:
        raw = response.choices[0].message.content.strip()
        # Handle potential markdown wrapping
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
    except (json.JSONDecodeError, IndexError):
        return {
            "skills": "general",
            "years_of_experience": 0,
            "education": "",
            "certifications": "",
        }


def generate_chat_response(
    user_message: str,
    predicted_profile: str,
    recommended_skills: list[str],
    extracted_info: dict,
) -> str:
    """
    Generate a comprehensive, conversational career advice response.

    Combines ML predictions with Groq LLM to create a rich, helpful response.
    """
    client = _get_groq_client()

    skills_to_learn = ", ".join(recommended_skills) if recommended_skills else "N/A"
    user_skills = extracted_info.get("skills", "Not specified")
    experience = extracted_info.get("years_of_experience", 0)
    education = extracted_info.get("education", "Not specified")
    certs = extracted_info.get("certifications", "None")

    prompt = f"""You are Career Intelligence AI — an expert career advisor built on real career data analysis. A user just asked you for career guidance. Here's what you know:

## User's Message
"{user_message}"

## ML Analysis Results (from our trained models)
- **Extracted Skills**: {user_skills}
- **AI-Predicted Career Profile**: {predicted_profile}
- **Years of Experience**: {experience or 'Not specified'}
- **Education**: {education or 'Not specified'}
- **Certifications**: {certs or 'None'}
- **Recommended Skills to Learn**: {skills_to_learn}

## Your Task
Give a warm, helpful, conversational response that:

1. **Acknowledge** what the user told you
2. **Share the prediction** — tell them their predicted career profile and why it fits their specific skills
3. **Recommend skills** — CRITICALLY evaluate the ML-recommended skills list. Only recommend skills that are DIRECTLY RELEVANT to the predicted career profile ({predicted_profile}). If a recommended skill seems irrelevant to this career path, SKIP IT and suggest a more relevant alternative instead. Pick the top 3-5 most impactful skills and explain WHY each matters for THIS specific career.
4. **Suggest career paths** — 2-3 specific job roles they should target based on their skills
5. **Give a quick action plan** — 3 concrete next steps they can take this week

IMPORTANT: Do NOT recommend skills that are irrelevant to the predicted career profile. For example, don't suggest machine learning frameworks to a frontend developer, or frontend frameworks to a data scientist. Stay focused and relevant to their career path.

Keep it conversational, encouraging, and specific. Use markdown formatting (bold, lists, headers) for readability. Keep the total response under 350 words. Don't be generic — reference THEIR specific skills and situation."""

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": "You are Career Intelligence AI, a friendly expert career advisor. You combine hard data (ML predictions) with practical wisdom. Be warm, specific, and actionable. Always use markdown formatting.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    return response.choices[0].message.content


def generate_career_advice(
    user_skills: str,
    predicted_profile: str,
    recommended_skills: list[str],
    years_of_experience: int = 0,
    education: str = "",
    certifications: str = "",
) -> str:
    """
    Generate personalized career advice (structured endpoint version).
    Kept for backward compatibility with /career_advice endpoint.
    """
    client = _get_groq_client()

    skills_to_learn = ", ".join(recommended_skills) if recommended_skills else "N/A"

    prompt = f"""You are an expert AI career advisor. Based on the following analysis of a professional's profile, provide actionable and personalized career guidance.

## Profile Analysis
- **Current Skills**: {user_skills}
- **Predicted Career Profile**: {predicted_profile}
- **Years of Experience**: {years_of_experience or 'Not specified'}
- **Education**: {education or 'Not specified'}
- **Certifications**: {certifications or 'None'}
- **Recommended Skills to Learn**: {skills_to_learn}

## Your Task
Provide a concise, actionable career guidance report with these sections:

### 🎯 Career Analysis
A brief analysis of where they stand based on their skills and predicted profile.

### 🛤️ Recommended Career Paths
2-3 specific job roles they should target, with brief reasoning.

### 📚 Learning Roadmap
A prioritized list of 3-5 skills they should learn next from the recommended skills, with why each skill matters.

### 💡 Growth Strategy
2-3 practical tips for career advancement in their field.

Keep it concise, energetic, and actionable. Use markdown formatting. Do NOT use more than 400 words total."""

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": "You are a friendly, expert career advisor who gives concise, actionable advice. Always be encouraging and specific.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    return response.choices[0].message.content
