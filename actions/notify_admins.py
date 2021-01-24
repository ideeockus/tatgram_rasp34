from aiogram import types
from bot_storage.configuration import feedback_tg_id, creator_id
from bot import bot


async def notify_admins(master_info_message: str):
    master_info_message = "Сообщение для администратора:\n"+master_info_message
    if feedback_tg_id == creator_id:
        await bot.send_message(creator_id, master_info_message)
        return
    await bot.send_message(feedback_tg_id, master_info_message)
    await bot.send_message(creator_id, master_info_message)


