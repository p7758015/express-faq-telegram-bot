from __future__ import annotations

from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .config import settings


@dataclass
class KBPaths:
    raw_faq: Path = settings.raw_faq_path
    faiss_dir: Path = settings.faiss_dir


def load_raw_faq(path: Path | None = None) -> List[dict]:
    paths = KBPaths()
    if path is None:
        path = paths.raw_faq
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data



def build_documents(raw_items: List[dict]) -> List[Document]:
    docs: List[Document] = []
    for item in raw_items:
        question = item.get("question", "").strip()
        answer = item.get("answer", "").strip()
        url = item.get("url", "").strip()

        if not answer:
            continue

        # Контекст = вопрос + ответ, чтобы семантический поиск находил по вопросу
        content = f"Вопрос: {question}\n\nОтвет:\n{answer}"
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "question": question,
                    "url": url,
                },
            )
        )
    return docs


def split_documents(
    docs: List[Document],
    chunk_size: int = 1200,
    chunk_overlap: int = 150,
) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n## ", "\n### ", "\n\n", ". ", "। ", "؟ ", "!", "?", ";", ",", " "
        ],
    )
    return splitter.split_documents(docs)


def build_faiss_index(
    docs: List[Document],
    faiss_dir: Path | None = None,
) -> FAISS:
    paths = KBPaths()
    if faiss_dir is None:
        faiss_dir = paths.faiss_dir

    embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
    index = FAISS.from_documents(docs, embeddings)

    index.save_local(str(faiss_dir))
    return index



def load_faiss_index(faiss_dir: Path | None = None) -> FAISS:
    paths = KBPaths()
    if faiss_dir is None:
        faiss_dir = paths.faiss_dir

    embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
    index = FAISS.load_local(
        str(faiss_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return index

