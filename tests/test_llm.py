from app.llm.gemini import to_contents


def test_assistant_vira_model():
    msgs = [
        {"role": "user", "content": "oi"},
        {"role": "assistant", "content": "olá"},
    ]
    out = to_contents(msgs)
    assert [c.role for c in out] == ["user", "model"]
    assert out[1].parts[0].text == "olá"