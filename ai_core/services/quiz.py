"""Quiz generation service."""
import json
import logging
import re

from .base import BaseLLMService

logger = logging.getLogger("ai_core")

QUIZ_SYSTEM_PROMPT = (
    "You are an expert educator who creates multiple-choice quiz questions. "
    "Based on the lesson content provided, create detailed quizzes in the same language as the topic or context provided..\n\n"
    "RULES:\n"
    "1. Return ONLY a valid JSON array, no markdown, no explanation outside JSON.\n"
    "2. Each element must have exactly these fields:\n"
    '   - "q": (string) The question text.\n'
    '   - "options": (array of 4 strings) Choices A, B, C, D.\n'
    '   - "correct": (integer 0-3) Index of the correct answer.\n'
    '   - "explain": (string) Brief explanation of the correct answer.\n'
    "3. Vary question difficulty (recall, comprehension, application).\n"
    "4. Distribute correct answers randomly across A, B, C, D.\n"
    "5. Make distractors plausible and non-trivial to eliminate.\n"
    "6. Start your response with [ and end with ], nothing else."
)

DEFAULT_NUM_QUESTIONS = 5
MAX_RETRIES = 2


class QuizGenerationError(Exception):
    """Raised when quiz generation fails after all retries."""


class QuizService:
    """Generate multiple-choice questions from lesson content."""

    def __init__(self, llm_service: BaseLLMService):
        self.llm_service = llm_service

    def generate(self, lesson_content: str, num_questions: int = DEFAULT_NUM_QUESTIONS,
                 difficulty: str = None) -> list:
        """Generate quiz questions from the given lesson content.

        Args:
            lesson_content: The lesson text (plain text or HTML).
            num_questions: Number of questions to generate (1-20, default 5).
            difficulty: Optional level – "easy", "medium", or "hard".

        Returns:
            A list of question dicts matching the expected schema.

        Raises:
            QuizGenerationError: If generation or parsing fails after retries.
        """
        message = self._build_message(lesson_content, num_questions, difficulty)

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                raw = self.llm_service.chat(message, system_prompt=QUIZ_SYSTEM_PROMPT)
                questions = self._parse_response(raw)
                self._validate(questions)
                logger.info(f"Quiz generated: {len(questions)} questions (attempt {attempt})")
                return questions
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                logger.warning(f"Quiz parse attempt {attempt}/{MAX_RETRIES} failed: {exc}")
                # Prepend a correction hint for the next attempt
                message = (
                    "Your previous response was not valid JSON. "
                    "Please respond ONLY with a valid JSON array.\n\n" + message
                )

        raise QuizGenerationError(
            f"Failed to generate quiz after {MAX_RETRIES} attempts: {last_error}"
        )

    # -- Private helpers --------------------------------------------------

    @staticmethod
    def _build_message(lesson_content: str, num_questions: int,
                       difficulty: str = None) -> str:
        """Build the user message sent to the LLM."""
        difficulty_hint = ""
        if difficulty:
            levels = {
                "easy": "easy (recall and recognition)",
                "medium": "medium (comprehension and low application)",
                "hard": "hard (high application and analysis)",
            }
            difficulty_hint = f"\nDifficulty level: {levels.get(difficulty, difficulty)}."

        return (
            f"Based on the lesson content below, create exactly {num_questions} "
            f"multiple-choice questions. Each question must have 4 choices "
            f"A, B, C, D and indicate the correct answer.{difficulty_hint}\n\n"
            f"=== LESSON CONTENT ===\n"
            f"{lesson_content}\n"
            f"=== END OF CONTENT ===\n\n"
            f"Respond with a JSON array only (no markdown or explanation)."
        )

    @staticmethod
    def _parse_response(raw: str) -> list:
        """Extract and parse a JSON array from the LLM response.

        Handles three cases:
        1. Clean JSON – parse directly.
        2. Wrapped in markdown code block – strip fences then parse.
        3. Embedded in extra text – locate outermost [ ] and parse.
        """
        text = raw.strip()

        # Case 1: starts with [
        if text.startswith("["):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        # Case 2: markdown code block ```json ... ```
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Case 3: find outermost [ ... ]
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass

        raise json.JSONDecodeError(
            "Could not extract JSON array from response", text, 0
        )

    @staticmethod
    def _validate(questions: list) -> None:
        """Validate the structure of each question dict.

        Raises:
            ValueError: If any question does not match the expected schema.
        """
        if not isinstance(questions, list) or not questions:
            raise ValueError("Response is not a non-empty list")

        for i, item in enumerate(questions):
            label = f"Question {i + 1}"

            if not isinstance(item, dict):
                raise ValueError(f"{label}: not an object")

            if not item.get("q") or not isinstance(item["q"], str):
                raise ValueError(f"{label}: missing or invalid 'q'")

            opts = item.get("options")
            if not isinstance(opts, list) or len(opts) != 4:
                raise ValueError(f"{label}: 'options' must be an array of 4 strings")

            if not all(isinstance(o, str) and o.strip() for o in opts):
                raise ValueError(f"{label}: each option must be a non-empty string")

            correct = item.get("correct")
            if not isinstance(correct, int) or correct not in (0, 1, 2, 3):
                raise ValueError(f"{label}: 'correct' must be an integer 0-3")

            if "explain" in item and not isinstance(item["explain"], str):
                raise ValueError(f"{label}: 'explain' must be a string")
