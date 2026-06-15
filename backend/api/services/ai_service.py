import json
import logging
from typing import Any, Dict, Optional

from django.conf import settings

from api.models import Question

logger = logging.getLogger(__name__)


def _get_client():
    """Return an OpenAI client if an API key is configured."""
    if not settings.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI

        return OpenAI(api_key=settings.OPENAI_API_KEY)
    except ImportError:
        logger.warning("openai package is not installed")
        return None


def generate_explanation(question: Question) -> str:
    """Generate an AI-powered explanation for a given question.

    Args:
        question: The Question instance to explain.

    Returns:
        A string containing the AI-generated explanation, or a fallback message.
    """
    client = _get_client()
    if not client:
        return _fallback_explanation(question)

    choices_text = "\n".join(
        f"{'✓' if c.is_correct else '○'} {c.choice_text}"
        for c in question.choices.all()
    )
    prompt = (
        "You are a nephrology expert tutor. Provide a detailed, educational explanation "
        "for the following nephrology board-style question. Include reasoning for why the "
        "correct answer is right and why each incorrect option is wrong.\n\n"
        f"Category: {question.category.name}\n"
        f"Difficulty: {question.difficulty}\n\n"
        f"Question:\n{question.question_text}\n\n"
        f"Choices:\n{choices_text}\n\n"
        "Provide a thorough explanation in 4-5 paragraphs."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert nephrology tutor."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("OpenAI API call failed for explanation")
        return _fallback_explanation(question)


def generate_question(topic: str, difficulty: str = "medium") -> Dict[str, Any]:
    """Generate a nephrology question using the OpenAI API.

    Args:
        topic: The nephrology topic for the question.
        difficulty: Difficulty level (easy, medium, hard).

    Returns:
        A dict with keys: question_text, choices (list), correct_answer, explanation.
        Returns an error dict on failure.
    """
    client = _get_client()
    if not client:
        return {"error": "OpenAI API key not configured or package not installed"}

    prompt = (
        f"Generate a {difficulty} nephrology board-style multiple-choice question about "
        f"'{topic}'. Return the response as a JSON object with these keys:\n"
        "- question_text: string\n"
        "- choices: list of strings (4-5 options)\n"
        "- correct_answer: string (the correct choice text)\n"
        "- explanation: string (detailed explanation)\n\n"
        "Make the question clinically relevant and accurate."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a nephrology exam question writer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.8,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        if not isinstance(data, dict) or "question_text" not in data:
            raise ValueError("Unexpected response format from API")
        return data
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response as JSON"}
    except Exception as e:
        logger.exception("OpenAI API call failed for question generation")
        return {"error": f"AI generation failed: {str(e)}"}


def _fallback_explanation(question: Question) -> str:
    """Return a basic explanation using the question's existing data."""
    correct = question.choices.filter(is_correct=True).first()
    correct_text = correct.choice_text if correct else "(unknown)"
    lines = [
        f"**Question:** {question.question_text}",
        f"**Correct Answer:** {correct_text}",
    ]
    if question.explanation:
        lines.append(f"\n**Explanation:**\n{question.explanation}")
    else:
        lines.append(
            "\n*An AI-generated explanation is not available. "
            "Please configure the OPENAI_API_KEY in your environment.*"
        )
    if question.clinical_pearl:
        lines.append(f"\n**Clinical Pearl:** {question.clinical_pearl}")
    return "\n\n".join(lines)
