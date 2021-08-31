from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage.rasp_db_updater import export_xlsx_to_db
import io
import threading

from bot_storage.accounts_base import get_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard


class RaspUpdateSteps(StatesGroup):
    waiting_for_xslx_file = State()


async def make_global_rasp_update():
    await RaspUpdateSteps.waiting_for_xslx_file.set()


@dp.message_handler(state=RaspUpdateSteps.waiting_for_xslx_file, content_types=types.ContentType.TEXT)
async def other_message(message: types.Message):
    await message.reply("Отправьте xlsx файл с расписанием в нужном формате")


@dp.message_handler(state=RaspUpdateSteps.waiting_for_xslx_file, content_types=types.ContentType.DOCUMENT)
async def document_gotten(message: types.Message):
    print("File gotten, uploading...")
    user_id = message.from_user.id
    user_role = get_role(user_id)
    user_keyboard = get_role_keyboard(user_role)
    await message.answer("Файл получен, загрузка...")
    await bot.send_chat_action(message.from_user.id, types.ChatActions.TYPING)
    doc_id = message.document.file_id

    doc = await bot.get_file(doc_id)
    file_path = doc.file_path
    loaded_rasp_file: io.BytesIO = await bot.download_file(file_path)
    print("File uploaded, processing...")
    await message.answer("Файл загружен, обработка...")
    await bot.send_chat_action(message.from_user.id, types.ChatActions.TYPING)

    try:
        rasp_update_thread = threading.Thread(target=export_xlsx_to_db, args=(loaded_rasp_file, message.from_user.id))
        rasp_update_thread.start()
        # rasp_update_thread.join()
        await message.reply("База данных обновлется, это займет какое-то время",
                            reply_markup=user_keyboard)
    except Exception as error:
        print("При попытке загрузки расписание возникла ошибка")
        print(error)
        await message.answer(f"Возникла ошибка: {error}", reply_markup=user_keyboard)
    await get_role_waiting_for_action_state(user_role).set()








