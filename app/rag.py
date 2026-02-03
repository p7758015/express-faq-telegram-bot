from __future__ import annotations

from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI

from .config import settings
from .kb import load_faiss_index


SYSTEM_PROMPT = (
    "Ты — ассистент службы доставки Express.ru. "
    "Отвечай только на основе предоставленного контекста FAQ. "
    "Отвечай кратко, по-деловому, на русском языке. "
    "Если в контексте нет ответа, честно скажи, что в FAQ об этом не сказано."
)


class ExpressRAG:
    def __init__(self, index: FAISS | None = None) -> None:
        self.index = index or load_faiss_index()
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.1,
            openai_api_key=settings.openai_api_key,
        )

    def retrieve(self, query: str, k: int = 6) -> List[Document]:
        return self.index.similarity_search(query, k=k)

    def build_context(self, docs: List[Document]) -> str:
        parts: List[str] = []
        for i, doc in enumerate(docs, start=1):
            q = doc.metadata.get("question", "")
            url = doc.metadata.get("url", "")
            parts.append(
                f"[Фрагмент {i}] Вопрос: {q}\nИсточник: {url}\n\n{doc.page_content}"
            )
        return "\n\n---\n\n".join(parts)

    def answer(self, query: str) -> str:
        docs = self.retrieve(query, k=6)
        context = self.build_context(docs)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Контекст FAQ:\n"
                    f"{context}\n\n"
                    "Вопрос пользователя:\n"
                    f"{query}"
                ),
            },
        ]

        resp = self.llm.invoke(messages)
        return resp.content
