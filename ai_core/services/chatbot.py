"""Chatbot service – conversational AI assistant for the LMS."""
import logging
from .base import BaseLLMService

logger = logging.getLogger("ai_core")

CHATBOT_SYSTEM_PROMPT = (
    "You are SkyLearn AI Assistant, a friendly and knowledgeable virtual tutor "
    "for an online learning management system called SkyLearn.\n\n"
    "RULES:\n"
    "1. Answer in the SAME language the user writes in.\n"
    "2. Be concise but helpful. Use short paragraphs.\n"
    "3. You can help with:\n"
    "   - Explaining academic concepts across all subjects\n"
    "   - Answering questions about courses, quizzes, grades\n"
    "   - Giving study tips and learning strategies\n"
    "   - Helping with assignment or homework guidance (do NOT give direct answers)\n"
    "   - General questions about using the SkyLearn platform\n"
    "4. Format responses in plain text. Use bullet points or numbered lists when helpful.\n"
    "5. If the user asks something harmful, unethical, or completely unrelated to "
    "education, politely decline.\n"
    "6. Keep responses under 300 words unless more detail is explicitly requested.\n"
    "7. Be encouraging and supportive in tone."
)


class ChatbotService:
    """Conversational assistant powered by an LLM provider."""

    def __init__(self, llm_service: BaseLLMService):
        self.llm_service = llm_service

    def reply(self, message: str, history: list[dict] | None = None) -> str:
        """Generate a chatbot reply.

        Args:
            message: The user's latest message.
            history: Optional list of previous messages, each with
                     ``{"role": "user"|"assistant", "content": "..."}``.
                     Used to build multi-turn context.

        Returns:
            The assistant's reply as plain text.
        """
        prompt = self._build_prompt(message, history)
        return self.llm_service.chat(prompt, system_prompt=CHATBOT_SYSTEM_PROMPT)

    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(message: str, history: list[dict] | None) -> str:
        """Build the user message with optional conversation history."""
        if not history:
            return message

        # Include recent history (last 10 turns) to stay within token limits
        recent = history[-10:]
        parts = []
        for turn in recent:
            role = "User" if turn["role"] == "user" else "Assistant"
            parts.append(f"{role}: {turn['content']}")
        parts.append(f"User: {message}")
        return "\n".join(parts)
