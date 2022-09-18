from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage.accounts_base import upload_new_accounts_from_csv
from bot_storage.accounts_base import get_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard
from utils import send_direct_message

import io
import threading


class AccountsUploadSteps(StatesGroup):
    waiting_for_accounts_csv = State()


async def make_accounts_upload():
    await AccountsUploadSteps.waiting_for_accounts_csv.set()


@dp.message_handler(state=AccountsUploadSteps.waiting_for_accounts_csv, content_types=types.ContentType.TEXT)
async def other_message(message: types.Message):
    await message.reply("Отправьте csv файл с расписанием в нужном формате")


@dp.message_handler(state=AccountsUploadSteps.waiting_for_accounts_csv, content_types=types.ContentType.DOCUMENT)
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
    accounts_file_bytesio: io.BytesIO = await bot.download_file(file_path)
    print("file uploaded, processing...")
    await message.answer("Файл загружен, обработка...")
    await bot.send_chat_action(message.from_user.id, types.ChatActions.TYPING)

    def upload_accounts(accounts_file_bytesio: io.BytesIO, user_id: str):
        try:
            uploaded_accounts_amount = upload_new_accounts_from_csv(accounts_file_bytesio.read().decode("UTF-8"))
            print(f"Зарегестрировано аккаунтов: {uploaded_accounts_amount}")
            send_direct_message(user_id, f"Зарегестрировано аккаунтов: {uploaded_accounts_amount}")
        except Exception as e:
            print("Ошибка при загрузке аккаунтов:", e)
            send_direct_message(user_id, f"Упс! При загрузке базы произошла какая-то ошибка!\n\n{e}")

    try:
        # accounts_upload_thread = threading.Thread(target=upload_new_accounts_from_csv, args=(accounts_file_bytesio, message.from_user.id))
        accounts_upload_thread = threading.Thread(target=upload_accounts, args=(accounts_file_bytesio, message.from_user.id))
        accounts_upload_thread.start()
        await message.reply("База аккаунтов загружается, это займет какое-то время",
                            reply_markup=user_keyboard)
    except Exception as error:
        print("При попытке загрузки аккаунтов возникла ошибка")
        print(error)
        await message.answer(f"Возникла ошибка: {error}", reply_markup=user_keyboard)
    await get_role_waiting_for_action_state(user_role).set()








