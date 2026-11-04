from google import genai
from google.genai import types

from app.llm.base import Message


_ROLE_MAP = {"user": "user", "assistant": "model"}


def to_contents(messages: list[Message]) -> list[types.Content]:
    return [
        types.Content(role=_ROLE_MAP[m["role"]], parts=[types.Part(text=m["content"])])
        for m in messages
    ]


class GeminiClient:
    def __init__(self, api_key: str, model: str):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, messages: list[Message], system: str) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=to_contents(messages),
            config=types.GenerateContentConfig(system_instruction=system),
        )
        return response.text or ""