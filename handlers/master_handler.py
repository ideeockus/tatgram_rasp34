from aiogram import types
# from aiogram.dispatcher.filters.state import State, StatesGroup
from bot_storage.UserStates import MasterStates
from bot import dp, bot
from bot_storage import bot_stats
from bot_storage.roles_base import get_all_users, get_role
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError
import asyncio
import datetime
from bot_storage.Keyboards import secret_role_kb, cancel_kb
from aiogram.types import ParseMode
from actions import update_global_rasp, broadcast_action
from actions.pupils_rasp import make_pupil_rasp_request
from actions.teachers_rasp import make_teacher_rasp_request
from utils import abg, other
from actions.notify_admins import notify_admins, notify_admins_photo
import time
from bot_storage import UserStates
from bot_storage.Keyboards import choose_role_kb
from bot_storage.configuration import allow_broadcasts


# class MasterStates(StatesGroup):
#     waiting_for_action = State()  # ожидание действий
#     waiting_for_text_to_broadcast = State()
#     waiting_for_class_name = State()
#     waiting_for_teacher_name = State()
#     waiting_for_rasp_file = State()

async def validate_master(message: types.Message) -> bool:
    user_id = message.from_user.id
    user_name = message.from_user.username
    user_full_name = message.from_user.full_name
    if get_role(user_id) == "master":
        print(f"master role validated for user {user_name}[{user_id}] ({user_full_name})")
        return True
    else:
        print(f"master role for user {user_name}[{user_id}] ({user_full_name}) NOT VALIDATED")
        await message.answer("Выберие свою роль", reply_markup=choose_role_kb)
        await UserStates.MainStates.wait_for_role.set()
        return False


@dp.message_handler(lambda m: m.text == "Отмена", state=MasterStates.all_states)  # waiting_for_text_to_broadcast
async def cancel(message: types.Message):
    print("cancellation by master")
    if not await validate_master(message):
        return

    await message.answer("Отменено", reply_markup=secret_role_kb)
    await MasterStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text == "Статистика", state=MasterStates.waiting_for_action)
async def stats(message: types.Message):
    print("show statistics to master")
    if not await validate_master(message):
        return

    usage_stats = bot_stats.get_stats()
    await message.answer(usage_stats)


@dp.message_handler(lambda m: m.text == "Рассылка", state=MasterStates.waiting_for_action)
async def broadcast(message: types.Message):
    print("broadcast by master")
    if not await validate_master(message):
        return

    await broadcast_action.make_broadcast(message)
    # await message.answer("Введите текст или картинку для рассылки", reply_markup=cancel_kb)
    # await MasterStates.waiting_for_text_to_broadcast.set()


@dp.message_handler(lambda m: m.text == "Расписание школьников", state=MasterStates.waiting_for_action)
async def pupils_rasp(message: types.Message):
    print("pupils rasp by master")
    if not await validate_master(message):
        return

    await make_pupil_rasp_request(message)


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=MasterStates.waiting_for_action)
async def teachers_rasp(message: types.Message):
    print("teachers rasp by master")
    if not await validate_master(message):
        return

    await make_teacher_rasp_request(message)


# @dp.message_handler(state=MasterStates.waiting_for_text_to_broadcast)
# async def text_for_broadcast_gotten(message: types.Message):
#     broadcast_start_time = datetime.datetime.now()
#     print("text broadcast by master")
#     if not await validate_master(message):
#         return
#
#     users_id_set = get_all_users()
#     users_count = len(users_id_set)
#     bad_users_count = 0
#     text_to_broadcast = abg.md_format(message.md_text)
#     print(text_to_broadcast)
#     # print(message.text)
#     # print(message.as_json())
#     # print(abg.md_format(message.md_text))
#     await MasterStates.waiting_for_action.set()
#     await message.answer(f"Рассылаю {users_count} пользователям", reply_markup=secret_role_kb)
#
#     if not allow_broadcasts:
#         broadcast_from_text = f"От пользователя {message.from_user.username}[{message.from_user.id}]\n" \
#                               f"{message.from_user.full_name}\n поступил запрос на рассылку текста: \n" \
#                               f"{message.text}\n\n" \
#                               f"Вы видите это сообщение, потомучто рассылки отключены в настройках бота"
#         print(broadcast_from_text)
#         await notify_admins(broadcast_from_text)
#         return
#
#     progress_percents = 0
#     progress_message: types.Message = await message.answer(
#         f"Рассылка: {other.progress_bar(progress_percents)} (0/{users_count})")
#
#     for (index, user_id) in enumerate(users_id_set):
#         try:
#
#             pass
#             time.sleep(0.2)
#             await bot.send_message(user_id, text_to_broadcast, parse_mode=ParseMode.MARKDOWN)
#             pass
#
#         except BotBlocked:
#             print(f"Targetu [ID:{user_id}]: blocked by user")
#             bad_users_count += 1
#         except ChatNotFound:
#             print(f"Target [ID:{user_id}]: invalid user ID")
#             bad_users_count += 1
#         except RetryAfter as e:
#             print(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
#             bad_users_count += 1
#             await asyncio.sleep(e.timeout)
#         except UserDeactivated:
#             print(f"Target [ID:{user_id}]: user is deactivated")
#             bad_users_count += 1
#         except TelegramAPIError:
#             print(f"Target [ID:{user_id}]: failed")
#             bad_users_count += 1
#         finally:
#             progress_percents = int(round((index + 1) / users_count, 2) * 100)
#             await progress_message.edit_text(
#                 f"Рассылка: {other.progress_bar(progress_percents)} ({index + 1}/{users_count})")
#     broadcast_length_time = (datetime.datetime.now() - broadcast_start_time).seconds
#     print(broadcast_length_time, "секунд заняла рассылка. Рассылка окончена")
#     await message.reply(
#         f"Разослано {users_count - bad_users_count} сообщений. {bad_users_count} не удалось отправить.\n"
#         f"Рассылка заняла {broadcast_length_time} секунд")
#
#
# @dp.message_handler(state=MasterStates.waiting_for_text_to_broadcast, content_types=types.ContentType.PHOTO)
# async def photo_for_broadcast_gotten(message: types.Message):
#     broadcast_start_time = datetime.datetime.now()
#     print("image broadcast from master")
#     if not await validate_master(message):
#         return
#
#     users_id_set = get_all_users()
#     users_count = len(users_id_set)
#     bad_users_count = 0
#     photo_to_broadcast = message.photo[-1].file_id
#     await MasterStates.waiting_for_action.set()
#     await message.answer(f"Рассылаю {users_count} пользователям", reply_markup=secret_role_kb)
#
#     if not allow_broadcasts:
#         broadcast_from_text = f"От пользователя {message.from_user.username}[{message.from_user.id}]\n" \
#                               f"{message.from_user.full_name}\n поступил запрос на рассылку изображения\n\n" \
#                               f"Вы видите это сообщение, потомучто рассылки отключены в настройках бота"
#         print(broadcast_from_text)
#         await notify_admins(broadcast_from_text)
#         await notify_admins_photo(photo_to_broadcast)
#         return
#
#     progress_percents = 0
#     progress_message: types.Message = await message.answer(
#         f"Рассылка: {other.progress_bar(progress_percents)} (0/{users_count})")
#     for (index, user_id) in enumerate(users_id_set):
#         try:
#             pass
#             time.sleep(0.2)
#             await bot.send_photo(user_id, photo_to_broadcast)
#             pass
#
#         except (BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError):
#             print(f"Target [ID:{user_id}]: fault")
#             # print(e)
#             bad_users_count += 1
#         finally:
#             progress_percents = int(round((index + 1) / users_count, 2) * 100)
#             await progress_message.edit_text(
#                 f"Рассылка: {other.progress_bar(progress_percents)} ({index + 1}/{users_count})")
#
#     broadcast_length_time = (datetime.datetime.now() - broadcast_start_time).seconds
#     print(broadcast_length_time, "секунд заняла рассылка. Рассылка окончена")
#     await message.reply(
#         f"Разослано {users_count - bad_users_count} сообщений. {bad_users_count} не удалось отправить.\n"
#         f"Рассылка заняла {broadcast_length_time} секунд")

@dp.message_handler(lambda m: m.text == "Загрузить расписание", state=MasterStates.waiting_for_action)
async def upload_rasp(message: types.Message):
    print("master upload new rasp_table")
    if not await validate_master(message):
        return

    await message.answer("Пришлите мне xlsx файл с расписанием", reply_markup=cancel_kb)
    await update_global_rasp.make_global_rasp_update()
