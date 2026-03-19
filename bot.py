import asyncio
import logging
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "bridge.db"

BOT_TOKEN = "8338690421:AAHKbahdicwp4PWtIMDy15P8-3yWNZ_IXK4"
TARGET_GROUP_ID = "-1001641458222"
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN muhit o'zgaruvchisi topilmadi.")

if not TARGET_GROUP_ID:
    raise RuntimeError("TARGET_GROUP_ID muhit o'zgaruvchisi topilmadi yoki noto'g'ri.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("telegram-bridge-bot")

router = Router(name="main")


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS message_links (
                group_chat_id INTEGER NOT NULL,
                group_message_id INTEGER NOT NULL,
                user_chat_id INTEGER NOT NULL,
                user_message_id INTEGER,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_chat_id, group_message_id)
            )
            """
        )
        conn.commit()


def save_link(
    group_chat_id: int,
    group_message_id: int,
    user_chat_id: int,
    user_message_id: Optional[int],
    username: Optional[str],
    full_name: str,
) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO message_links (
                group_chat_id, group_message_id, user_chat_id, user_message_id, username, full_name
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                group_chat_id,
                group_message_id,
                user_chat_id,
                user_message_id,
                username,
                full_name,
            ),
        )
        conn.commit()


def get_user_by_group_message(group_chat_id: int, group_message_id: int) -> Optional[dict]:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT user_chat_id, user_message_id, username, full_name
            FROM message_links
            WHERE group_chat_id = ? AND group_message_id = ?
            """,
            (group_chat_id, group_message_id),
        ).fetchone()
        return dict(row) if row else None


def build_sender_card(message: Message) -> str:
    user = message.from_user
    full_name = user.full_name
    username = f"@{user.username}" if user.username else "yo'q"
    return (
        "📩 <b>Yangi murojaat</b>\n"
        f"👤 <b>F.I.Sh.:</b> {full_name}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"🔗 <b>Username:</b> {username}\n\n"
        "Quyidagi xabarga <b>reply</b> qilib javob bering. "
        "Bot javobni avtomatik ravishda murojaat egasiga yuboradi."
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Assalomu alaykum. Murojaatingizni shu yerga yozib yuboring.\n\n"
        "Matn, rasm, fayl, video, audio yoki voice yuborishingiz mumkin."
    )


@router.message(F.chat.type == ChatType.PRIVATE)
async def from_user_to_group(message: Message, bot: Bot) -> None:
    sender_card = await bot.send_message(
        chat_id=TARGET_GROUP_ID,
        text=build_sender_card(message),
        parse_mode=ParseMode.HTML,
    )
    save_link(
        group_chat_id=TARGET_GROUP_ID,
        group_message_id=sender_card.message_id,
        user_chat_id=message.chat.id,
        user_message_id=message.message_id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )

    forwarded = await bot.copy_message(
        chat_id=TARGET_GROUP_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        reply_parameters=sender_card.as_reply_parameters(),
    )
    save_link(
        group_chat_id=TARGET_GROUP_ID,
        group_message_id=forwarded.message_id,
        user_chat_id=message.chat.id,
        user_message_id=message.message_id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )

    await message.answer(
        "✅ Murojaatingiz qabul qilindi. Javob tayyor bo'lgach shu bot orqali sizga yuboriladi."
    )


@router.message(F.chat.id == TARGET_GROUP_ID, F.reply_to_message.as_("reply_to"))
async def from_group_to_user(message: Message, bot: Bot, reply_to: Message) -> None:
    link = get_user_by_group_message(message.chat.id, reply_to.message_id)
    if not link:
        return

    try:
        await bot.copy_message(
            chat_id=link["user_chat_id"],
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        await message.reply("✅ Javob foydalanuvchiga yuborildi.")
    except Exception as exc:
        logger.exception("Javobni foydalanuvchiga yuborishda xatolik: %s", exc)
        await message.reply(
            "❌ Javobni yuborib bo'lmadi. Foydalanuvchi botni bloklagan bo'lishi mumkin."
        )


@router.message(F.chat.id == TARGET_GROUP_ID)
async def ignore_non_replies(message: Message) -> None:
    return


async def main() -> None:
    init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    me = await bot.get_me()
    logger.info("Bot ishga tushdi: @%s", me.username)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi")
