"""Lesson generation service."""
import logging
from .base import BaseLLMService

logger = logging.getLogger("ai_core")

LESSON_SYSTEM_PROMPT = (
    "You are a professional university lecturer. "
    "Your task is to create detailed lessons in the same language as the topic or context provided.  "
    "Return pure HTML only (no <html>, <head>, or <body> tags). "
    "Use the following tags to present content clearly and structurally: "
    "<h2>, <h3>, <p>, <ul>, <ol>, <li>, <strong>, <em>, <blockquote>, <table>. "
    "Do not use markdown or any format other than HTML. "
    "Do not include any inline CSS style attributes, especially font-family or font-size."
)


class LessonService:
    """Generate lesson content using a given LLM provider."""

    def __init__(self, llm_service: BaseLLMService):
        self.llm_service = llm_service

    def generate(self, topic: str, requirements: str = None, context: str = None) -> str:
        """Generate an HTML lesson for the given topic.

        Args:
            topic: The lesson topic.
            requirements: User-specified requirements for the lesson (optional).
            context: Additional context from RAG chunks (optional, for future use).
        """
        message = f"Create a detailed lesson on the topic: {topic}"

        if requirements:
            message += f"\n\nRequirements:\n{requirements}"

        if context:
            message += (
                "\n\nBelow is reference material retrieved from the knowledge base. "
                "Integrate this content into the lesson where appropriate:\n\n"
                f"{context}"
            )

        return self.llm_service.chat(message, system_prompt=LESSON_SYSTEM_PROMPT)