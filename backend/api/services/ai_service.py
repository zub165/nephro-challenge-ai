import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from django.conf import settings

from api.models import Question
from api.services.ai_learning_service import augment_system_prompt

logger = logging.getLogger(__name__)


def _chat_completion(
    messages: List[Dict[str, str]],
    *,
    max_tokens: int = 800,
    temperature: float = 0.7,
    json_mode: bool = False,
) -> Optional[str]:
    """Call configured LLM (GoDaddy LLaMA/Ollama or OpenAI). Returns content or None."""
    provider = getattr(settings, "AI_PROVIDER", "auto").lower()

    if provider in ("ollama", "llama", "local"):
        return _call_openai_compatible(
            messages,
            base_url=settings.LLAMA_BASE_URL,
            api_key=settings.LLAMA_API_KEY,
            model=settings.LLAMA_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=json_mode,
        )

    if provider == "openai":
        if not settings.OPENAI_API_KEY:
            return None
        return _call_openai_compatible(
            messages,
            base_url=None,
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=json_mode,
        )

    # auto: prefer local LLaMA on GoDaddy VPS, then OpenAI
    content = _call_openai_compatible(
        messages,
        base_url=settings.LLAMA_BASE_URL,
        api_key=settings.LLAMA_API_KEY,
        model=settings.LLAMA_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        json_mode=json_mode,
    )
    if content:
        return content

    if settings.OPENAI_API_KEY:
        return _call_openai_compatible(
            messages,
            base_url=None,
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=json_mode,
        )
    return None


def _call_openai_compatible(
    messages: List[Dict[str, str]],
    *,
    base_url: Optional[str],
    api_key: str,
    model: str,
    max_tokens: int,
    temperature: float,
    json_mode: bool,
) -> Optional[str]:
    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("openai package is not installed")
        return None

    kwargs: Dict[str, Any] = {}
    if base_url:
        kwargs["base_url"] = base_url.rstrip("/")

    client = OpenAI(api_key=api_key or "not-needed", timeout=60.0, **kwargs)

    create_kwargs: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if json_mode:
        create_kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**create_kwargs)
        return response.choices[0].message.content.strip()
    except Exception:
        label = base_url or "openai"
        logger.exception("LLM call failed (%s, model=%s)", label, model)
        return None


def generate_explanation(question: Question) -> str:
    """Generate an AI-powered explanation for a given question."""
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
        "Provide a thorough explanation in 4-5 paragraphs. "
        "For medical education only — not medical advice."
    )

    content = _chat_completion(
        [
            {
                "role": "system",
                "content": augment_system_prompt(
                    "You are an expert nephrology tutor.",
                    topic=question.subcategory or question.category.name,
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.7,
    )
    if content:
        return content
    return _fallback_explanation(question)


def generate_question(topic: str, difficulty: str = "medium") -> Dict[str, Any]:
    """Generate a nephrology MCQ draft via LLaMA (GoDaddy) or OpenAI."""
    prompt = (
        f"Generate a {difficulty} nephrology board-style multiple-choice question about "
        f"'{topic}'. Return ONLY a JSON object with these keys:\n"
        "- question_text: string\n"
        "- choices: list of strings (4 options)\n"
        "- correct_answer: string (must match one choice exactly)\n"
        "- explanation: string (detailed explanation)\n\n"
        "Make the question clinically relevant and accurate."
    )

    content = _chat_completion(
        [
            {
                "role": "system",
                "content": augment_system_prompt(
                    "You are a nephrology exam question writer. Output valid JSON only.",
                    topic=topic,
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.8,
        json_mode=True,
    )

    if not content:
        return {"error": "AI not available. Configure LLAMA_BASE_URL on GoDaddy or OPENAI_API_KEY."}

    try:
        data = json.loads(content)
        if not isinstance(data, dict) or "question_text" not in data:
            raise ValueError("Unexpected response format")
        return data
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response as JSON"}
    except ValueError as e:
        return {"error": str(e)}


def _fallback_explanation(question: Question) -> str:
    """Return explanation from database when LLM is unavailable."""
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
            "\n*AI tutor is unavailable. Set LLAMA_BASE_URL (Ollama on GoDaddy VPS) "
            "or OPENAI_API_KEY in backend .env.*"
        )
    if question.clinical_pearl:
        lines.append(f"\n**Clinical Pearl:** {question.clinical_pearl}")
    return "\n\n".join(lines)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_json(text: str, want_list: bool = False):
    """Robustly extract a JSON object/array from an LLM reply (handles code fences)."""
    if not text:
        return None
    trimmed = text.strip()
    if trimmed.startswith("```"):
        trimmed = trimmed.strip("`")
        if trimmed.startswith("json"):
            trimmed = trimmed[4:]
        trimmed = trimmed.strip()
    try:
        return json.loads(trimmed)
    except json.JSONDecodeError:
        pass
    start = trimmed.find("[") if want_list else trimmed.find("{")
    if start == -1:
        return None
    open_char, close_char = ("[", "]") if want_list else ("{", "}")
    depth = 0
    for i in range(start, len(trimmed)):
        ch = trimmed[i]
        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(trimmed[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def chat_with_tutor(message: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
    """Conversational AI tutor (Ollama/LLaMA on GoDaddy or OpenAI)."""
    system = (
        "You are the Nephro Challenge AI tutor — a friendly, expert nephrology "
        "educator. Answer clinical-concept questions, break down board-style MCQs, "
        "give high-yield pearls, and suggest what to study next. Be concise: aim for "
        "150-250 words unless the user asks for detail. For medical education only — "
        "not medical advice."
    )
    messages = [{"role": "system", "content": system}]
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": message})
    return _chat_completion(messages, max_tokens=400, temperature=0.6)


def detailed_explanation(question: Question, selected_answer: str = "") -> Dict[str, Any]:
    """Structured, deeper explanation for the mobile explanation screen."""
    correct = question.choices.filter(is_correct=True).first()
    correct_text = correct.choice_text if correct else ""
    choices_text = "\n".join(f"{'✓' if c.is_correct else '○'} {c.choice_text}" for c in question.choices.all())
    prompt = (
        "You are a nephrology board exam tutor. For the question below, return ONLY a "
        "JSON object with these keys:\n"
        "- explanation: string (3-4 paragraph teaching explanation)\n"
        "- key_points: list of 3-5 high-yield bullets\n"
        "- references: list of 1-3 authoritative citations (KDIGO/KDOQI/AHA/textbook)\n"
        "- related_topic: string (next topic to study, or empty)\n"
        "- difficulty: 'basic' | 'intermediate' | 'advanced'\n\n"
        f"Question:\n{question.question_text}\n\n"
        f"Choices:\n{choices_text}\n\n"
        f"Correct answer: {correct_text}\n"
        f"Student's selected answer: {selected_answer or '(none)'}\n\n"
        "For medical education only — not medical advice."
    )
    content = _chat_completion(
        [
            {"role": "system", "content": "You are an expert nephrology exam tutor. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.6,
        json_mode=True,
    )

    if content:
        data = _extract_json(content)
        if isinstance(data, dict):
            return {
                "id": f"ai-{question.id}",
                "question_id": str(question.id),
                "explanation": data.get("explanation", question.explanation),
                "key_points": data.get("key_points", []) or [],
                "references": data.get("references", []) or [],
                "related_topic": data.get("related_topic", ""),
                "difficulty": data.get("difficulty", "intermediate"),
                "created_at": _now_iso(),
            }

    references = []
    if question.reference:
        references = [question.reference]
    return {
        "id": f"ai-{question.id}",
        "question_id": str(question.id),
        "explanation": question.explanation or _fallback_explanation(question),
        "key_points": [],
        "references": references,
        "related_topic": "",
        "difficulty": "intermediate",
        "created_at": _now_iso(),
    }


def generate_questions(topic: str, count: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
    """Generate multiple MCQ draft questions on a topic via the LLM."""
    prompt = (
        f"Generate {count} distinct {difficulty} nephrology board-style multiple-choice "
        f"questions about '{topic}'. Return ONLY a JSON array of objects, each with keys:\n"
        "- question_text: string (one sentence)\n"
        "- choices: list of exactly 4 short strings\n"
        "- correct_answer: string (must match one choice exactly)\n"
        "- explanation: string (max 2 sentences)\n\n"
        "Keep answers terse. Make each question clinically relevant and factually accurate."
    )
    content = _chat_completion(
        [
            {"role": "system", "content": "You are a nephrology exam question writer. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=900,
        temperature=0.8,
        json_mode=True,
    )
    if not content:
        return []
    data = _extract_json(content, want_list=True)
    if isinstance(data, list):
        return data[:count]
    if isinstance(data, dict) and isinstance(data.get("questions"), list):
        return data["questions"][:count]
    return []
