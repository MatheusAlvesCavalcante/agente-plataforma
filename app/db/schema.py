import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS agendamentos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo       TEXT NOT NULL,
    participante TEXT NOT NULL,
    inicio       TEXT NOT NULL,  -- 'AAAA-MM-DDTHH:MM', horário local
    fim          TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'confirmado'
                 CHECK (status IN ('confirmado', 'cancelado'))
);
CREATE INDEX IF NOT EXISTS idx_agendamentos_inicio ON agendamentos(inicio);
"""


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()