import pytest
from google.genai import types

from app.llm.base import Message, ToolCall, ToolResult
from app.llm.gemini import to_contents


def test_assistant_vira_model():
    msgs = [Message(role="user", text="oi"), Message(role="assistant", text="olá")]
    out = to_contents(msgs)
    assert [c.role for c in out] == ["user", "model"]
    assert out[1].parts[0].text == "olá"


def test_provider_data_e_repassado_sem_alteracao():
    original = types.Content(role="model", parts=[types.Part(text="x")])
    msgs = [Message(role="assistant", text="x", provider_data=original)]
    assert to_contents(msgs)[0] is original


def test_resultados_de_ferramenta_ficam_em_uma_unica_mensagem():
    msg = Message(
        role="tool",
        tool_results=[ToolResult("a", {"ok": True}), ToolResult("b", {"ok": True})],
    )
    out = to_contents([msg])
    assert len(out) == 1
    assert out[0].role == "user"
    assert len(out[0].parts) == 2


def test_tool_calls_sem_provider_data_e_erro():
    msg = Message(role="assistant", tool_calls=[ToolCall("a", {})])
    with pytest.raises(ValueError):
        to_contents([msg])