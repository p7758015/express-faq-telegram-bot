# Express FAQ Telegram Bot

Телеграм‑бот‑консультант для службы доставки Express.ru.  
Отвечает на частые вопросы на основе FAQ сайта (RAG: парсинг → векторная база → LLM).

## Функциональность

- Парсинг страницы FAQ `https://www.express.ru/faq` в локальный JSON (`data/raw_faq.json`).
- Построение векторной базы (FAISS) по текстам FAQ.
- Генерация ответов с помощью LLM (OpenAI) **строго на основе FAQ**.
- Telegram‑бот на aiogram 3:
  - команды `/start` и `/help`;
  - клавиатура с быстрыми вопросами: «Тарифы», «Вызов курьера», «Часы работы».
- Логирование диалогов в SQLite (`data/logs.db`):
  - user_id, username;
  - вопрос, ответ;
  - наиболее релевантный вопрос из FAQ и его URL;
  - время запроса.

## Технологии

- Python 3.12
- aiogram 3
- langchain‑community, langchain‑openai, langchain‑core, langchain‑text‑splitters
- FAISS (faiss‑cpu)
- OpenAI API (модель `gpt-4.1-mini` / аналогичная)
- requests, BeautifulSoup4, html2text — парсинг FAQ
- SQLite — хранение логов

## Структура проекта

- `app/config.py` — настройки проекта, пути, чтение `.env`.
- `app/kb.py` — работа с FAQ: загрузка JSON, подготовка документов, построение и загрузка FAISS‑индекса.
- `app/rag.py` — класс `ExpressRAG` (поиск по индексу + обращение к LLM).
- `app/bot.py` — Telegram‑бот на aiogram 3.
- `app/db.py` — инициализация и логирование диалогов в SQLite.
- `scripts/scrape_faq.py` — загрузка и парсинг FAQ в `data/raw_faq.json`.
- `scripts/build_kb.py` — построение FAISS‑индекса в `data/faiss/`.
- `scripts/demo_cli.py` — тестовый CLI‑ассистент для FAQ.
- `scripts/run_bot.py` — запуск Telegram‑бота.

## Установка

```bash
git clone https://github.com/p7758015/express-faq-telegram-bot.git
cd express-faq-telegram-bot

python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Переменные окружения
Создайте файл .env в корне проекта (рядом с requirements.txt):

text
OPENAI_API_KEY=sk-...      # ключ OpenAI (НЕ коммитить)
LLM_PROVIDER=openai        # пока используется openai
BOT_TOKEN=1234567890:ABC...# токен Telegram‑бота (НЕ коммитить)
Файл .env должен быть в .gitignore и не попадать в репозиторий.
```

# Подготовка данных

### Скачать и распарсить FAQ:

```bash
python -m scripts.scrape_faq

В результате появится `data/raw_faq.json`.
```

### Построить векторную базу (FAISS):

```bash
python -m scripts.build_kb
```

Индекс будет сохранён в `data/faiss/`.

### (Опционально) протестировать CLI‑ассистента:

```bash
python -m scripts.demo_cli
```

Примеры вопросов:

- Сколько стоит доставка?
- Можно заказать доставку на выходные?
- Как вызвать курьера?

## Запуск Telegram‑бота

```bash
python -m scripts.run_bot
```

Бот поддерживает:

- `/start` — приветствие и вывод клавиатуры с кнопками:
  * «Тарифы»
  * «Вызов курьера»
  * «Часы работы»
- `/help` — краткая инструкция по темам, с которыми бот работает.

Любой текстовый вопрос пересылается в RAG‑бэкенд, который:

- Находит ближайшие фрагменты FAQ в FAISS‑индексе.
- Передаёт их вместе с вопросом в LLM.
- Возвращает краткий ответ на русском языке.

Все диалоги логируются в `data/logs.db` (таблица `dialog_logs`).

## Безопасность секретов

Ключи OpenAI и токен бота хранятся только в `.env`.

`.env` добавлен в `.gitignore` и не должен попадать в git.

При перевыпуске ключей достаточно обновить значения в `.env` и перезапустить приложение.

## Планы

### Дальнейшие шаги развития проекта:

#### Несколько LLM‑провайдеров

Расширить `LLM_PROVIDER` режимами:

- **yandex** — YandexGPT API (через Yandex Cloud / SDK)
- **gigachat** — GigaChat API от Сбера
- **mock** — локальный режим без внешнего API для разработки

#### Улучшение RAG‑слоя

- Лучше нормализовать текст FAQ (заголовки, списки).
- Добавить категории/теги в metadata документов.
- Поддержать несколько источников (FAQ + тарифы + условия доставки).

#### Расширение Telegram‑интерфейса

- Inline‑кнопка с ссылкой на оригинальный FAQ.
- Кнопка «Не помогло» → логирование проблемных вопросов.
- Простейшая статистика `/admin`‑командой (количество запросов, топ-темы).

#### Деплой на сервер

- Dockerfile + docker-compose.yml.
- Деплой на VPS/PaaS, запуск как systemd‑сервис или контейнер.
- Вариант деплоя целиком в РФ с YandexGPT/GigaChat для работы без VPN.

#### Просмотр логов и аналитика

- Небольшой web-интерфейс (FastAPI) для просмотра `dialog_logs`.
- Фильтрация по дате, пользователю, ключевым словам.
- Экспорт логов в CSV/Excel.
```

