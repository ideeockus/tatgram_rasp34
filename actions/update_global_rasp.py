from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage.rasp_db_updater import export_xlsx_to_db
from bot_storage.Keyboards import ReplyKeyboardMarkup, KeyboardButton
import io
import threading

cancel_rasp_update_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_rasp_update_button = KeyboardButton("Отмена")
cancel_rasp_update_kb.add(cancel_rasp_update_button)


class RaspUpdateSteps(StatesGroup):
    waiting_for_xslx_file = State()
    end_state = State()


class RaspUpdateKeyboards:
    end_keyboard = cancel_rasp_update_kb


# class RaspUpdateThread(threading.Thread):
#     def __init__(self, bot_instance, user_id, file):
#         threading.Thread.__init__(self)
#         self.bot_instance = bot_instance
#         self.user_id = user_id
#         self.file = file
#
#     def run(self):
#         loop = asyncio.new_event_loop()
#         loop.run_until_complete(export_xslx_to_db(self.bot_instance, self.user_id, self.file))


async def make_global_rasp_update(end_state: State, end_keyboard: types.ReplyKeyboardMarkup):
    RaspUpdateSteps.end_state = end_state
    await RaspUpdateSteps.waiting_for_xslx_file.set()
    RaspUpdateKeyboards.end_keyboard = end_keyboard


@dp.message_handler(lambda m: m.text == "Отмена", state=RaspUpdateSteps.waiting_for_xslx_file, content_types=types.ContentType.TEXT)
async def cancel_rasp_update(message: types.Message, state: FSMContext):
    await RaspUpdateSteps.end_state.set()
    await message.reply("Отменено", reply_markup=RaspUpdateKeyboards.end_keyboard)


@dp.message_handler(state=RaspUpdateSteps.waiting_for_xslx_file, content_types=types.ContentType.TEXT)
async def other_message(message: types.Message):
    await message.reply("Отправьте xlsx файл с расписанием в нужном формате")


@dp.message_handler(state=RaspUpdateSteps.waiting_for_xslx_file, content_types=types.ContentType.DOCUMENT)
async def document_gotten(message: types.Message):
    await message.answer("Файл получен, загрузка...")
    await bot.send_chat_action(message.from_user.id, types.ChatActions.TYPING)
    doc_id = message.document.file_id

    doc = await bot.get_file(doc_id)
    file_path = doc.file_path
    loaded_rasp_file: io.BytesIO = await bot.download_file(file_path)
    await message.answer("Файл загружен, обработка...")
    await bot.send_chat_action(message.from_user.id, types.ChatActions.TYPING)

    try:
        rasp_update_thread = threading.Thread(target=export_xlsx_to_db, args=(loaded_rasp_file, message.from_user.id))
        rasp_update_thread.start()
        # rasp_update_thread.join()
        await message.reply("База данных обновлется, это займет какое-то время", reply_markup=RaspUpdateKeyboards.end_keyboard)
    except Exception as error:
        print("При попытке загрузки расписание возникла ошибка")
        print(error)
        await message.answer(f"Возникла ошибка: {error}", reply_markup=RaspUpdateKeyboards.end_keyboard)
    await RaspUpdateSteps.end_state.set()








