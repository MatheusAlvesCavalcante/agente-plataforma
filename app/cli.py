import logging

from app.config import settings
from app.db.connection import get_connection
from app.llm.base import Message
from app.llm.gemini import GeminiClient
from app.orchestrator.loop import run_turn
from app.orchestrator.prompt import build_system_prompt


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="  >> %(message)s")
    logging.getLogger("app").setLevel(logging.INFO)

    llm = GeminiClient(settings.llm_api_key, settings.llm_model)
    conn = get_connection()
    history: list[Message] = []
    print("Chat iniciado. Digite 'sair' para encerrar.\n")

    while True:
        text = input("Você: ").strip()
        if text.lower() in {"sair", "exit"}:
            break
        if not text:
            continue
        try:
            answer = run_turn(llm, conn, history, text, build_system_prompt())
        except Exception as e:
            print(f"[erro] {type(e).__name__}: {e}\n")
            continue
        print(f"IA: {answer}\n")


if __name__ == "__main__":
    main()