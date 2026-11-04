from dataclasses import dataclass, field
from typing import Any, Literal, Protocol


@dataclass(frozen=True)
class ToolSpec:
    """Como uma ferramenta é apresentada ao modelo."""

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    """Um PEDIDO do modelo. Não é uma execução."""

    name: str
    args: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    name: str
    result: dict[str, Any]


@dataclass
class Message:
    role: Literal["user", "assistant", "tool"]
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)       
    tool_results: list[ToolResult] = field(default_factory=list)   
    provider_data: Any = None  


class LLMClient(Protocol):
    def generate(
        self,
        messages: list[Message],
        system: str,
        tools: list[ToolSpec] | None = None,
    ) -> Message: ...