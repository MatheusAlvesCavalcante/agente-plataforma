from datetime import datetime, timedelta

from app.db.connection import get_connection
from app.db.schema import init_db


def _at(dias: int, hhmm: str) -> str:
    dia = (datetime.now() + timedelta(days=dias)).date()
    return f"{dia.isoformat()}T{hhmm}"


ROWS = [
    ("Reunião de alinhamento", "Carlos Souza", _at(1, "14:00"), _at(1, "15:00"), "confirmado"),
    ("Almoço de negócios", "Carlos Almeida", _at(1, "12:00"), _at(1, "13:00"), "confirmado"),
    ("Reunião cancelada", "Carlos Souza", _at(1, "17:00"), _at(1, "18:00"), "cancelado"),
    ("Consulta", "Dra. Marta", _at(2, "09:30"), _at(2, "10:30"), "confirmado"),
    ("Revisão do projeto", "Beatriz Lima", _at(3, "16:00"), _at(3, "17:00"), "confirmado"),
    ("Planejamento mensal", "Equipe", _at(10, "10:00"), _at(10, "11:30"), "confirmado"),
]


def main() -> None:
    conn = get_connection()
    init_db(conn)
    conn.execute("DELETE FROM agendamentos")  # só para desenvolvimento
    conn.executemany(
        "INSERT INTO agendamentos (titulo, participante, inicio, fim, status) "
        "VALUES (?, ?, ?, ?, ?)",
        ROWS,
    )
    conn.commit()
    print(f"{len(ROWS)} agendamentos criados.")


if __name__ == "__main__":
    main()