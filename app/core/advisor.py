"""
OpenRouter-powered AI Career Advisor.
Handles both structured career advice and chat-based natural language queries.
Uses ChatGPT Nano (via OpenRouter) for intelligent career guidance.
"""

from openai import OpenAI

from app.core.config import settings


def _get_llm_client() -> OpenAI:
    """Get an OpenAI client configured for OpenRouter."""
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is not set. Get a key at https://openrouter.ai/keys")
    return OpenAI(
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
    )


def extract_profile_from_message(message: str) -> dict:
    """
    Use LLM to extract structured career profile info from a natural language message.

    Returns a dict with: skills, years_of_experience, education, certifications
    """
    client = _get_llm_client()

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {
                "role": "system",
                "content": """You are a data extraction assistant. Extract career profile information from the user's message.
Return ONLY a valid JSON object with these fields:
- "skills": comma-separated string of technical skills mentioned (e.g., "Python, SQL, Docker")
- "years_of_experience": integer (0 if not mentioned)
- "education": string (e.g., "Bachelor's", "Master's", "PhD", or "" if not mentioned)
- "certifications": comma-separated string (or "" if none mentioned)
- "is_conversational": boolean (true if the message is purely conversational like greetings, "thank you", "??", or a follow-up question that doesn't provide new skills or profile info)

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
    import re

    try:
        raw = response.choices[0].message.content.strip()
        # Handle markdown code block wrapping (```json ... ``` or ``` ... ```)
        if raw.startswith("```"):
            # Remove opening ``` or ```json line
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            raw = raw.rsplit("```", 1)[0].strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: try to find a JSON object anywhere in the text
            match = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise
    except (json.JSONDecodeError, IndexError, AttributeError):
        return {
            "skills": "general",
            "years_of_experience": 0,
            "education": "",
            "certifications": "",
            "is_conversational": True,
        }


def generate_chat_response(
    user_message: str,
    predicted_profile: str | None = None,
    recommended_skills: list[str] | None = None,
    extracted_info: dict | None = None,
    history: list[dict[str, str]] | None = None,
) -> str:
    """
    Generate a comprehensive, conversational career advice response.

    Combines ML predictions with Groq LLM to create a rich, helpful response.
    """
    client = _get_llm_client()

    skills_to_learn = ", ".join(recommended_skills) if recommended_skills else "N/A"
    extracted_info = extracted_info or {}
    user_skills = extracted_info.get("skills", "Not specified")
    experience = extracted_info.get("years_of_experience", 0)
    education = extracted_info.get("education", "Not specified")
    certs = extracted_info.get("certifications", "None")
    is_conv = extracted_info.get("is_conversational", False)

    # Context string for ML results
    ml_context = ""
    if predicted_profile and not is_conv:
        ml_context = f"""
## ML Analysis Results (from our trained models)
- **Extracted Skills**: {user_skills}
- **AI-Predicted Career Profile**: {predicted_profile}
- **Years of Experience**: {experience or "Not specified"}
- **Education**: {education or "Not specified"}
- **Certifications**: {certs or "None"}
- **Recommended Skills to Learn**: {skills_to_learn}
"""

    prompt = f"""You are Career Intelligence AI — an expert career advisor built on real career data analysis. A user just asked you a question. Here's what you know:

## User's Message
"{user_message}"
{ml_context}

## Your Task
Give a warm, helpful, conversational response. 

- **If the message is a greeting or casual talk (thank you, hello, etc.)**: Respond naturally as a friendly advisor. Don't force a career prediction or recommendation if it feels out of place. Be welcoming.
- **If the user provides skills or asks for an analysis**: 
    1. **Acknowledge** what they told you.
    2. **Share the prediction** — explain their predicted career profile ({predicted_profile}) and why it fits.
    3. **Recommend skills** — Critically evaluate the recommendation list ({skills_to_learn}). Suggest 3-5 most impactful ones.
    4. **Suggest career paths** — 2-3 specific roles.
    5. **Give a quick action plan** — 3 next steps.

IMPORTANT: If `predicted_profile` is provided, stay focused on that path. If the user is just saying thanks or asking a follow-up that doesn't need data, just be a helpful human-like advisor.

IMPORTANT: Do NOT recommend skills that are irrelevant to the predicted career profile. For example, don't suggest machine learning frameworks to a frontend developer, or frontend frameworks to a data scientist. Stay focused and relevant to their career path.

Keep it conversational, encouraging, and specific. Use markdown formatting (bold, lists, headers) for readability. Keep the total response under 350 words. Don't be generic — reference THEIR specific skills and situation."""

    messages = [
        {
            "role": "system",
            "content": "You are Career Intelligence AI, a friendly expert career advisor. You combine hard data (ML predictions) with practical wisdom. Be warm, specific, and actionable. Always use markdown formatting.",
        }
    ]

    # Add conversation history (limited to avoid token overflow)
    if history:
        # OpenRouter/OpenAI expect 'assistant' role instead of 'ai' used in frontend
        for msg in history[-10:]:  # Last 10 messages for context
            role = "assistant" if msg["role"] == "ai" else msg["role"]
            messages.append({"role": role, "content": msg["content"]})

    # Add current prompt
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=messages,
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
    client = _get_llm_client()

    skills_to_learn = ", ".join(recommended_skills) if recommended_skills else "N/A"

    prompt = f"""You are an expert AI career advisor. Based on the following analysis of a professional's profile, provide actionable and personalized career guidance.

## Profile Analysis
- **Current Skills**: {user_skills}
- **Predicted Career Profile**: {predicted_profile}
- **Years of Experience**: {years_of_experience or "Not specified"}
- **Education**: {education or "Not specified"}
- **Certifications**: {certifications or "None"}
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
        model=settings.openrouter_model,
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
