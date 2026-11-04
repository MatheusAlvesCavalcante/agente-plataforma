import sqlite3
from pathlib import Path


def get_connection(path: str | None = None) -> sqlite3.Connection:
    """Abre uma conexão SQLite. Nos testes, passe ':memory:'."""
    if path is None:
        # Import tardio: os testes não dependem do .env.
        from app.config import settings

        path = settings.database_url.removeprefix("sqlite:///")
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # permite acessar colunas por nome
    conn.execute("PRAGMA foreign_keys = ON")
    return conn