from bot_storage.configuration import feedback_tg_id, creator_id
from bot import bot


async def notify_admins(master_info_message: str):
    master_info_message = "Сообщение для администратора:\n"+master_info_message
    if feedback_tg_id == creator_id:
        await bot.send_message(creator_id, master_info_message)
        return
    await bot.send_message(feedback_tg_id, master_info_message)
    await bot.send_message(creator_id, master_info_message)


async def notify_admins_photo(master_info_photo):
    if feedback_tg_id == creator_id:
        await bot.send_photo(feedback_tg_id, master_info_photo)
        return
    await bot.send_photo(feedback_tg_id, master_info_photo)
    await bot.send_photo(creator_id, master_info_photo)


async def quiet_admin_notification(master_info_message: str):
    master_info_message = master_info_message
    if feedback_tg_id == creator_id:
        await bot.send_message(creator_id, master_info_message, disable_notification=True)
        return
    await bot.send_message(feedback_tg_id, master_info_message, disable_notification=True)
    await bot.send_message(creator_id, master_info_message, disable_notification=True)


