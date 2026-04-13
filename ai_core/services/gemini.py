"""Gemini LLM provider."""
from decouple import config
from langchain_google_genai import ChatGoogleGenerativeAI
from .base import BaseLLMService


class GeminiService(BaseLLMService):
    """Google Gemini provider."""

    def _build_llm(self):
        return ChatGoogleGenerativeAI(
            google_api_key=config("GOOGLE_API_KEY"),
            model="gemini-3-flash-preview",
        )