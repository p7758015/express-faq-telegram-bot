from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

import html2text
import requests
from bs4 import BeautifulSoup

from .config import settings


FAQ_URL = "https://www.express.ru/faq"


@dataclass
class FAQItem:
    question: str
    answer: str
    url: str


def fetch_faq_page(url: str = FAQ_URL) -> str:
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_faq_html(html: str, url: str = FAQ_URL) -> List[FAQItem]:
    soup = BeautifulSoup(html, "html.parser")
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.body_width = 0

    items: List[FAQItem] = []

    # Эту часть потом подправим под реальную структуру FAQ
    # Пока ищем блоки FAQ как пары вопрос/ответ
    for block in soup.select("section, div"):
        # Заголовок вопроса
        h = block.find(["h2", "h3", "h4"])
        if not h:
            continue
        question = h.get_text(strip=True)
        if not question:
            continue

        # Текст ответа — берём весь текст блока
        answer_html = "".join(str(child) for child in block.children)
        answer = converter.handle(answer_html).strip()
        if not answer:
            continue

        items.append(FAQItem(question=question, answer=answer, url=url))

    return items


def save_faq_items(items: List[FAQItem], path: str | None = None) -> None:
    if path is None:
        path = str(settings.raw_faq_path)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    data = [item.__dict__ for item in items]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
