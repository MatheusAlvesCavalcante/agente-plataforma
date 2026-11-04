import logging
import sqlite3

from app.llm.base import LLMClient, Message, ToolResult, ToolSpec
from app.tools.registry import TOOLS, execute

logger = logging.getLogger(__name__)

MAX_PASSOS = 5


def _specs() -> list[ToolSpec]:
    return [ToolSpec(t.name, t.description, t.parameters) for t in TOOLS.values()]


def run_turn(
    llm: LLMClient,
    conn: sqlite3.Connection,
    history: list[Message],
    user_text: str,
    system: str,
) -> str:
    """Processa uma mensagem do usuário e devolve o texto final da resposta."""
    inicio = len(history)
    history.append(Message(role="user", text=user_text))
    try:
        for _ in range(MAX_PASSOS):
            reply = llm.generate(history, system, tools=_specs())
            history.append(reply)

            if not reply.tool_calls:
                return reply.text

            resultados = []
            for call in reply.tool_calls:
                resultado = execute(conn, call.name, call.args)
                logger.info("ferramenta=%s args=%s ok=%s", call.name, call.args, resultado["ok"])
                resultados.append(ToolResult(name=call.name, result=resultado))
            history.append(Message(role="tool", tool_results=resultados))
    except Exception:
        del history[inicio:]  # não deixa uma rodada pela metade no histórico
        raise

    aviso = "Não consegui concluir a tarefa dentro do limite de passos."
    history.append(Message(role="assistant", text=aviso))
    return aviso