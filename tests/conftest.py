import pytest

from app.db.connection import get_connection
from app.db.schema import init_db


@pytest.fixture
def conn():
    c = get_connection(":memory:")
    init_db(c)
    yield c
    c.close()


@pytest.fixture
def add(conn):
    def _add(
        titulo="Reunião",
        participante="Carlos",
        inicio="2026-11-03T14:00",
        fim="2026-11-03T15:00",
        status="confirmado",
    ):
        conn.execute(
            "INSERT INTO agendamentos (titulo, participante, inicio, fim, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (titulo, participante, inicio, fim, status),
        )
        conn.commit()

    return _add