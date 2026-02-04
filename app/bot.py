from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from .config import settings
from .rag import ExpressRAG
from .db import init_db, log_dialog


logger = logging.getLogger(__name__)


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Тарифы"),
                KeyboardButton(text="Вызов курьера"),
            ],
            [
                KeyboardButton(text="Часы работы"),
                KeyboardButton(text="/help"),
            ],
        ],
        resize_keyboard=True,
    )


async def on_startup(bot: Bot) -> None:
    init_db()
    me = await bot.get_me()
    logger.info("Bot started as %s", me.username)


def build_rag() -> ExpressRAG:
    return ExpressRAG()


def setup_handlers(dp: Dispatcher, rag: ExpressRAG) -> None:
    @dp.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        await message.answer(
            "Привет! Я FAQ‑ассистент Express.ru.\n"
            "Задай вопрос о доставке, тарифах, работе курьеров и т.п.",
            reply_markup=main_keyboard(),
        )

    @dp.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        text = (
            "Я отвечаю на частые вопросы по доставке Express.ru:\n"
            "• Вызов и работа курьера\n"
            "• Оформление заказа и накладные\n"
            "• Расчёт стоимости и оплата\n"
            "• Тарифы и срочная доставка\n"
            "• Часы работы офисов\n\n"
            "Нажми кнопку на клавиатуре или просто задай вопрос текстом."
        )
        await message.answer(text, reply_markup=main_keyboard())

    @dp.message(F.text)
    async def handle_question(message: Message) -> None:
        text = (message.text or "").strip()
        if not text:
            return

        await message.chat.do("typing")

        try:
            # используем вариант, который возвращает ответ и документы
            answer, docs = rag.answer_with_docs(text)
        except Exception as e:
            logger.exception("RAG error: %s", e)
            await message.answer(
                "Не получилось получить ответ от модели. "
                "Попробуй ещё раз чуть позже."
            )
            return

        top_q = docs[0].metadata.get("question") if docs else None
        top_url = docs[0].metadata.get("url") if docs else None

        from_user = message.from_user
        log_dialog(
            user_id=from_user.id if from_user else None,
            username=from_user.username if from_user else None,
            question=text,
            answer=answer,
            top_question=top_q,
            top_url=top_url,
        )

        await message.answer(answer, reply_markup=main_keyboard())

    @dp.message()
    async def handle_other(message: Message) -> None:
        await message.answer(
            "Пока я понимаю только текстовые вопросы. "
            "Напиши, пожалуйста, вопрос текстом."
        )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN не задан в .env")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    rag = build_rag()
    setup_handlers(dp, rag)

    await dp.start_polling(bot, on_startup=on_startup)


if __name__ == "__main__":
    asyncio.run(main())
