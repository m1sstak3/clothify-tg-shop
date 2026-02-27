import asyncio
import logging
from aiogram import Bot

async def show_loading_animation(bot: Bot, chat_id: int, text: str = "⏳ Обработка...") -> int:
    """Отображает анимацию загрузки (Android UX, избегаем пустых экранов)."""
    msg = await bot.send_message(chat_id, text)
    return msg.message_id

async def finish_loading_animation(bot: Bot, chat_id: int, message_id: int):
    """Удаляет анимацию загрузки после окончания задачи."""
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.error(f"Error deleting loading animation message: {e}")
