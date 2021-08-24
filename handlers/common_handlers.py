from aiogram.dispatcher import FSMContext

from bot import dp
from aiogram import types
# from bot_storage.roles_base import get_role
from bot_storage import accounts_base
from bot_storage.UserStates import get_role_waiting_for_action_state, GuestStates
from bot_storage.Keyboards import get_role_keyboard, guest_kb


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/start` command
    """
    print("start", message.from_user)
    await state.finish()
    # await message.answer("Здравствуйте. \n Выберите свою роль", reply_markup=choose_role_kb)
    await message.answer("Здравствуйте.\nВыберите опцию", reply_markup=guest_kb)
    await GuestStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text == "Отмена", state="*", content_types=types.ContentType.TEXT)
async def cancel(message: types.Message):
    user_id = message.from_user.id
    user_role = accounts_base.get_role(user_id)
    await get_role_waiting_for_action_state(user_role).set()
    await message.reply("Отменено", reply_markup=get_role_keyboard(user_role))
