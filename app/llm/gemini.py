from google import genai
from google.genai import types

from app.llm.base import Message, ToolCall, ToolSpec

_SEM_RESPOSTA = "Não consegui gerar uma resposta (conteúdo vazio ou bloqueado)."


def to_contents(messages: list[Message]) -> list[types.Content]:
    contents: list[types.Content] = []
    for m in messages:
        if m.role == "user":
            contents.append(types.Content(role="user", parts=[types.Part(text=m.text)]))
        elif m.role == "assistant":
            if m.provider_data is not None:
                contents.append(m.provider_data)
            elif m.tool_calls:
                raise ValueError(
                    "Mensagem com tool_calls precisa de provider_data "
                    "(os modelos Gemini 3 exigem as thought signatures)."
                )
            else:
                contents.append(types.Content(role="model", parts=[types.Part(text=m.text)]))
        elif m.role == "tool":
            parts = [
                types.Part.from_function_response(name=r.name, response={"result": r.result})
                for r in m.tool_results
            ]
            contents.append(types.Content(role="user", parts=parts))
    return contents


def _to_tools(tools: list[ToolSpec] | None) -> list[types.Tool] | None:
    if not tools:
        return None
    declarations = [
        {"name": t.name, "description": t.description, "parameters": t.parameters}
        for t in tools
    ]
    return [types.Tool(function_declarations=declarations)]


class GeminiClient:
    def __init__(self, api_key: str, model: str):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(
        self,
        messages: list[Message],
        system: str,
        tools: list[ToolSpec] | None = None,
    ) -> Message:
        response = self._client.models.generate_content(
            model=self._model,
            contents=to_contents(messages),
            config=types.GenerateContentConfig(
                system_instruction=system,
                tools=_to_tools(tools),
            ),
        )

        content = response.candidates[0].content if response.candidates else None
        if content is None:
            return Message(role="assistant", text=_SEM_RESPOSTA)

        parts = content.parts or []
        text = "".join(p.text for p in parts if p.text and not p.thought)
        calls = [
            ToolCall(name=p.function_call.name, args=dict(p.function_call.args or {}))
            for p in parts
            if p.function_call
        ]
        return Message(role="assistant", text=text, tool_calls=calls, provider_data=content)