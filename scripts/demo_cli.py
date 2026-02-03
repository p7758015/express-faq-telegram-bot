from app.rag import ExpressRAG


def main() -> None:
    rag = ExpressRAG()
    print("Express FAQ ассистент. Напиши вопрос, 'exit' для выхода.\n")

    while True:
        try:
            q = input("Вопрос> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            break

        if not q:
            continue
        if q.lower() in {"exit", "quit", "выход"}:
            print("Выход.")
            break

        answer = rag.answer(q)
        print("\nОтвет:")
        print(answer)
        print("-" * 40)


if __name__ == "__main__":
    main()
