import pytest

from app.llm.base import Message, ToolCall
from app.orchestrator.loop import MAX_PASSOS, run_turn


class FakeLLM:
    """Modelo de mentira: devolve respostas roteirizadas, sem rede."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.chamadas = 0

    def generate(self, messages, system, tools=None):
        self.chamadas += 1
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


def chama(nome="consultar_agendamentos", **args):
    return Message(role="assistant", tool_calls=[ToolCall(nome, args)])


def test_fluxo_com_ferramenta(conn, add):
    add(participante="Carlos")
    llm = FakeLLM([chama(), Message(role="assistant", text="Você tem 1 reunião.")])
    history = []
    resposta = run_turn(llm, conn, history, "o que tenho?", "sistema")
    assert resposta == "Você tem 1 reunião."
    assert [m.role for m in history] == ["user", "assistant", "tool", "assistant"]
    resultado = history[2].tool_results[0].result
    assert resultado["ok"] is True
    assert resultado["dados"]["total"] == 1


def test_parametros_invalidos_voltam_ao_modelo_como_erro(conn):
    llm = FakeLLM([chama(data_inicio="amanhã"), Message(role="assistant", text="Qual data?")])
    history = []
    run_turn(llm, conn, history, "reuniões amanhã", "sistema")
    assert history[2].tool_results[0].result["erro"] == "parametros_invalidos"


def test_limite_de_passos(conn):
    llm = FakeLLM([chama() for _ in range(MAX_PASSOS + 5)])
    history = []
    resposta = run_turn(llm, conn, history, "oi", "sistema")
    assert llm.chamadas == MAX_PASSOS
    assert "limite" in resposta
    assert history[-1].role == "assistant"


def test_falha_do_llm_nao_deixa_historico_inconsistente(conn):
    llm = FakeLLM([chama(), RuntimeError("falhou")])
    history = [Message(role="user", text="antiga"), Message(role="assistant", text="resp")]
    with pytest.raises(RuntimeError):
        run_turn(llm, conn, history, "nova", "sistema")
    assert len(history) == 2