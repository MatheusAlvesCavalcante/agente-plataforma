import sqlite3
from datetime import date, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.tools.base import Tool

MAX_RESULTADOS = 20


class ConsultarAgendamentosInput(BaseModel):
    model_config = ConfigDict(extra="forbid") 

    data_inicio: date | None = None
    data_fim: date | None = None
    participante: str | None = Field(default=None, min_length=1, max_length=100)

    @model_validator(mode="after")
    def _intervalo_valido(self):
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValueError("data_fim não pode ser anterior a data_inicio")
        return self


def consultar_agendamentos(
    conn: sqlite3.Connection, p: ConsultarAgendamentosInput
) -> dict[str, Any]:
    sql = (
        "SELECT id, titulo, participante, inicio, fim, status "
        "FROM agendamentos WHERE status != 'cancelado'"
    )
    params: list[Any] = []

    if p.data_inicio:
        sql += " AND inicio >= ?"
        params.append(f"{p.data_inicio.isoformat()}T00:00")
    if p.data_fim:
        sql += " AND inicio < ?"
        params.append(f"{(p.data_fim + timedelta(days=1)).isoformat()}T00:00")
    if p.participante:
        sql += " AND participante LIKE ?"
        params.append(f"%{p.participante}%")

    sql += " ORDER BY inicio LIMIT ?"
    params.append(MAX_RESULTADOS + 1) 

    rows = conn.execute(sql, params).fetchall()
    truncado = len(rows) > MAX_RESULTADOS
    rows = rows[:MAX_RESULTADOS]
    return {
        "total": len(rows),
        "truncado": truncado,
        "agendamentos": [dict(r) for r in rows],
    }


TOOL = Tool(
    name="consultar_agendamentos",
    description=(
        "Consulta os agendamentos confirmados. Todos os filtros são opcionais e "
        "combináveis. Não retorna agendamentos cancelados. Se 'truncado' for "
        "verdadeiro, existem mais resultados do que os listados."
    ),
    parameters={
        "type": "object",
        "properties": {
            "data_inicio": {
                "type": "string",
                "description": "Data inicial, inclusive, no formato AAAA-MM-DD.",
            },
            "data_fim": {
                "type": "string",
                "description": "Data final, inclusive, no formato AAAA-MM-DD.",
            },
            "participante": {
                "type": "string",
                "description": "Parte do nome do participante.",
            },
        },
    },
    input_model=ConsultarAgendamentosInput,
    executor=consultar_agendamentos,
)