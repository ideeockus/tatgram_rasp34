from bot import dp
from aiogram import types
from bot_storage.roles_base import get_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard


@dp.message_handler(lambda m: m.text == "Отмена", state="*", content_types=types.ContentType.TEXT)
async def cancel_rasp_update(message: types.Message):
    user_id = message.from_user.id
    user_role = get_role(user_id)
    await get_role_waiting_for_action_state(user_role).set()
    await message.reply("Отменено", reply_markup=get_role_keyboard(user_role))