from app.config import settings
from app.llm.base import Message
from app.llm.gemini import GeminiClient

SYSTEM = "Você é um assistente prestativo. Responda em português do Brasil, de forma curta."


def main() -> None:
    llm = GeminiClient(settings.llm_api_key, settings.llm_model)
    history: list[Message] = []
    print("Chat iniciado. Digite 'sair' para encerrar.\n")

    while True:
        text = input("Você: ").strip()
        if text.lower() in {"sair", "exit"}:
            break
        if not text:
            continue

        history.append({"role": "user", "content": text})
        try:
            answer = llm.generate(history, SYSTEM)
        except Exception as e:
            history.pop()  
            print(f"[erro] {type(e).__name__}: {e}\n")
            continue

        history.append({"role": "assistant", "content": answer})
        print(f"IA: {answer}\n")


if __name__ == "__main__":
    main()