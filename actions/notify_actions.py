from bot_storage.configuration import feedback_tg_ids
from bot import bot


async def notify_admins(master_info_message: str):
    master_info_message = "Сообщение для администратора:\n"+master_info_message
    for feedback_tg_id in feedback_tg_ids:
        await bot.send_message(feedback_tg_id, master_info_message)


async def notify_admins_photo(master_info_photo):
    for feedback_tg_id in feedback_tg_ids:
        await bot.send_photo(feedback_tg_id, master_info_photo)


async def quiet_admin_notification(master_info_message: str):
    master_info_message = master_info_message
    for feedback_tg_id in feedback_tg_ids:
        await bot.send_message(feedback_tg_id, master_info_message, disable_notification=True)


