from aiogram.dispatcher import FSMContext

from bot import dp
from aiogram import types
from bot_storage import accounts_base
from bot_storage.UserStates import get_role_waiting_for_action_state, GuestStates
from bot_storage.Keyboards import get_role_keyboard, guest_kb
from bot_storage.accounts_base import check_account_existence, unlink_account


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/start` command
    """
    user_id = message.from_user.id
    username = message.from_user.username
    print("start", message.from_user)
    await state.finish()
    if check_account_existence(user_id):
        print(f"Аккаунт пользователя {username}[{user_id}] будет откреплен")
        unlink_account(user_id)
        # accounts_db_session.delete(user)
        # accounts_db_session.commit()

    await message.answer("Здравствуйте.\nВыберите опцию", reply_markup=guest_kb)
    await GuestStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text == "Отмена", state="*", content_types=types.ContentType.TEXT)
async def cancel(message: types.Message):
    user_id = message.from_user.id
    user_role = accounts_base.get_role(user_id)
    await get_role_waiting_for_action_state(user_role).set()
    await message.reply("Отменено", reply_markup=get_role_keyboard(user_role))
