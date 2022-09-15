from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage.accounts_base import get_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard
from bot_storage.food_menu import upload_food_menu_from_csv
from utils import send_direct_message

import io
import threading


class FoodMenuUploadSteps(StatesGroup):
    waiting_for_csv = State()


async def make_food_menu_upload():
    await FoodMenuUploadSteps.waiting_for_csv.set()


@dp.message_handler(state=FoodMenuUploadSteps.waiting_for_csv, content_types=types.ContentType.TEXT)
async def other_message(message: types.Message):
    await message.reply("Отправьте csv файл с меню в нужном формате")


@dp.message_handler(state=FoodMenuUploadSteps.waiting_for_csv, content_types=types.ContentType.DOCUMENT)
async def document_gotten(message: types.Message):
    print("file gotten, uploading...")
    user_id = message.from_user.id
    user_role = get_role(user_id)
    user_keyboard = get_role_keyboard(user_role)
    await message.answer("Файл получен, загрузка...")
    await bot.send_chat_action(message.from_user.id, types.ChatActions.TYPING)
    doc_id = message.document.file_id

    doc = await bot.get_file(doc_id)
    file_path = doc.file_path
    file_bytesio: io.BytesIO = await bot.download_file(file_path)
    print("file uploaded, processing...")
    await message.answer("Файл загружен, обработка...")
    await bot.send_chat_action(message.from_user.id, types.ChatActions.TYPING)

    try:
        food_menu_upload_thread = threading.Thread(target=upload_food_menu,
                                                   args=(file_bytesio, message.from_user.id))
        food_menu_upload_thread.start()
        await message.reply("Меню загружается, это займет какое-то время",
                            reply_markup=user_keyboard)
    except Exception as error:
        print("При попытке загрузки меню возникла ошибка")
        print(error)
        await message.answer(f"Возникла ошибка: {error}", reply_markup=user_keyboard)
    await get_role_waiting_for_action_state(user_role).set()


def upload_food_menu(file_bytesio: io.BytesIO, user_id: str):
    try:
        uploaded_amount = upload_food_menu_from_csv(file_bytesio.read().decode("UTF-8"))
        print(f"Зарегестрировано пунктов меню: {uploaded_amount}")
        send_direct_message(user_id, f"Зарегестрировано пунктов меню: {uploaded_amount}")
    except Exception as e:
        print("Ошибка при загрузке меню:", e)
        send_direct_message(user_id, f"Упс! При загрузке базы произошла какая-то ошибка!\n\n{e}")
