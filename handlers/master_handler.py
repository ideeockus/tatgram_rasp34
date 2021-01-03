from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage import bot_stats
from bot_storage.roles_base import get_all_users
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError
import asyncio
from bot_storage.Keyboards import secret_role_kb, cancel_kb
from aiogram.types import ParseMode
from actions import update_global_rasp
from actions.pupils_rasp import make_pupil_rasp_request
from actions.teachers_rasp import make_teacher_rasp_request
from utils import abg, other


class MasterStates(StatesGroup):
    waiting_for_action = State()  # ожидание действий
    waiting_for_text_to_broadcast = State()
    waiting_for_class_name = State()
    waiting_for_teacher_name = State()
    waiting_for_rasp_file = State()


@dp.message_handler(lambda m: m.text == "Статистика", state=MasterStates.waiting_for_action)
async def stats(message: types.Message):
    usage_stats = bot_stats.get_stats()
    await message.answer(usage_stats)


@dp.message_handler(lambda m: m.text == "Рассылка", state=MasterStates.waiting_for_action)
async def broadcast(message: types.Message):
    await message.answer("Введите текст или картинку для рассылки", reply_markup=cancel_kb)
    await MasterStates.waiting_for_text_to_broadcast.set()


@dp.message_handler(lambda m: m.text == "Отмена", state=MasterStates.all_states)  # waiting_for_text_to_broadcast
async def cancel(message: types.Message):
    await message.answer("Отменено", reply_markup=secret_role_kb)
    await MasterStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text == "Расписание школьников", state=MasterStates.waiting_for_action)
async def pupils_rasp(message: types.Message):
    await make_pupil_rasp_request(message, MasterStates.waiting_for_action, secret_role_kb)


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=MasterStates.waiting_for_action)
async def teachers_rasp(message: types.Message):
    await make_teacher_rasp_request(message, MasterStates.waiting_for_action, secret_role_kb)


@dp.message_handler(state=MasterStates.waiting_for_text_to_broadcast)
async def text_for_broadcast_gotten(message: types.Message):
    print("Текстовая рассылка")
    users_id_set = get_all_users()
    users_count = len(users_id_set)
    bad_users_count = 0
    text_to_broadcast = abg.md_format(message.md_text)
    print(text_to_broadcast)
    # print(message.text)
    # print(message.as_json())
    # print(abg.md_format(message.md_text))
    await message.answer(f"Рассылаю {users_count} пользователям", reply_markup=secret_role_kb)

    progress_percents = 0
    progress_message: types.Message = await message.answer(f"Рассылка: {other.progress_bar(progress_percents)} (0/{users_count})")
    for (index, user_id) in enumerate(users_id_set):
        try:
            await bot.send_message(user_id, text_to_broadcast, parse_mode=ParseMode.MARKDOWN)
        except BotBlocked:
            print(f"Targetu [ID:{user_id}]: blocked by user")
            bad_users_count += 1
        except ChatNotFound:
            print(f"Target [ID:{user_id}]: invalid user ID")
            bad_users_count += 1
        except RetryAfter as e:
            print(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
            bad_users_count += 1
            await asyncio.sleep(e.timeout)
        except UserDeactivated:
            print(f"Target [ID:{user_id}]: user is deactivated")
            bad_users_count += 1
        except TelegramAPIError:
            print(f"Target [ID:{user_id}]: failed")
            bad_users_count += 1
        finally:
            progress_percents = int(round((index + 1) / users_count, 2) * 100)
            await progress_message.edit_text(
                f"Рассылка: {other.progress_bar(progress_percents)} ({index + 1}/{users_count})")
    await message.reply(f"Разослано {users_count-bad_users_count} сообщений. {bad_users_count} не удалось отправить")
    await MasterStates.waiting_for_action.set()


@dp.message_handler(state=MasterStates.waiting_for_text_to_broadcast, content_types=types.ContentType.PHOTO)
async def text_for_broadcast_gotten(message: types.Message):
    print("Рассылка фото")
    users_id_set = get_all_users()
    users_count = len(users_id_set)
    bad_users_count = 0
    photo_to_broadcast = message.photo[-1].file_id
    await message.answer(f"Рассылаю {users_count} пользователям", reply_markup=secret_role_kb)

    progress_percents = 0
    progress_message: types.Message = await message.answer(
        f"Рассылка: {other.progress_bar(progress_percents)} (0/{users_count})")
    for (index, user_id) in enumerate(users_id_set):
        try:
            await bot.send_photo(user_id, photo_to_broadcast)
        except (BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError):
            print(f"Target [ID:{user_id}]: fault")
            # print(e)
            bad_users_count += 1
        finally:
            progress_percents = int(round((index + 1) / users_count, 2) * 100)
            await progress_message.edit_text(
                f"Рассылка: {other.progress_bar(progress_percents)} ({index + 1}/{users_count})")
    await message.reply(f"Разослано {users_count-bad_users_count} сообщений. {bad_users_count} не удалось отправить")
    await MasterStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text == "Загрузить расписание", state=MasterStates.waiting_for_action)
async def upload_rasp(message: types.Message):
    await message.answer("Пришлите мне xlsx файл с расписанием", reply_markup=update_global_rasp.cancel_rasp_update_kb)
    await update_global_rasp.make_global_rasp_update(MasterStates.waiting_for_action, secret_role_kb)



