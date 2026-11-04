import logging
import sqlite3
from typing import Any

from pydantic import ValidationError

from app.tools import agendamentos
from app.tools.base import Tool

logger = logging.getLogger(__name__)

TOOLS: dict[str, Tool] = {t.name: t for t in [agendamentos.TOOL]}


def execute(conn: sqlite3.Connection, name: str, args: dict[str, Any]) -> dict[str, Any]:
    tool = TOOLS.get(name)
    if tool is None:
        return {"ok": False, "erro": "ferramenta_desconhecida"}

    try:
        params = tool.input_model.model_validate(args)
    except ValidationError as e:
        detalhes = [
            {"campo": ".".join(str(x) for x in err["loc"]), "motivo": err["msg"]}
            for err in e.errors()
        ]
        return {"ok": False, "erro": "parametros_invalidos", "detalhes": detalhes}

    try:
        dados = tool.executor(conn, params)
    except Exception:
        logger.exception("Falha ao executar a ferramenta %s", name)
        return {"ok": False, "erro": "erro_interno"}

    return {"ok": True, "dados": dados}