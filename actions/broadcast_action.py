import asyncio
import time
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from actions.notify_admins import notify_admins, notify_admins_photo
from bot import dp, bot
from bot_storage.configuration import allow_broadcasts
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError
from aiogram.utils.markdown import bold, code, italic, text, escape_md
from aiogram.types import ParseMode
from bot_storage.Keyboards import cancel_kb, broadcast_choose_target_kb
from libs import Roles, role_by_name
from utils import other, abg
from utils.abg import md_shielding
from bot_storage.roles_base import get_role, get_all_users, get_users_by_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard

# cancel_feedback_kb = ReplyKeyboardMarkup(resize_keyboard=True)
# cancel_feedback_button = KeyboardButton("Отмена")
# cancel_feedback_kb.add(cancel_feedback_button)


class BroadcastSteps(StatesGroup):
    waiting_for_broadcast_target = State()
    waiting_for_broadcast_message = State()
    # end_state = State()


# class FeedbackKeyboards:
#     end_keyboard = cancel_kb


async def make_broadcast(message: types.Message):
    # FeedbackSteps.end_state = end_state
    await message.reply("Выберите цель для рассылки\n\nИли введите id юзера",
                        reply_markup=broadcast_choose_target_kb)
    await BroadcastSteps.waiting_for_broadcast_target.set()
    # await BroadcastSteps.waiting_for_broadcast_message.set()
    # FeedbackKeyboards.end_keyboard = end_keyboard


# @dp.message_handler(lambda m: m.text == "Отмена",
#                     state=FeedbackSteps.waiting_for_feedback_text, content_types=types.ContentType.TEXT)
# async def feedback_text_gotten(message: types.Message, state: FSMContext):
#     await FeedbackSteps.end_state.set()
#     await message.reply("Отменено", reply_markup=FeedbackKeyboards.end_keyboard)

@dp.message_handler(state=BroadcastSteps.waiting_for_broadcast_target, content_types=types.ContentType.TEXT)
async def choose_broadcast_target(message: types.Message, state: FSMContext):
    broadcast_target_text = message.text
    broadcast_target_dict = {
        "Учителям": "teacher",
        "Ученикам": "pupil",
        "Родителям": "parent",
        "Старостам": "headman",
        "Общая рассылка": "all"
    }
    broadcast_target: str = broadcast_target_text if broadcast_target_text.isdigit() \
        else broadcast_target_dict.get(broadcast_target_text)
    await state.update_data(broadcast_target=broadcast_target)
    await BroadcastSteps.waiting_for_broadcast_message.set()
    await message.reply("Введите текст или картинку для рассылки", reply_markup=cancel_kb)


# @dp.message_handler(state=BroadcastSteps.waiting_for_broadcast_message, content_types=types.ContentType.TEXT)
# async def feedback_text_gotten(message: types.Message, state: FSMContext):
#     feedback_text = message.text
#     user_id = message.from_user.id
#     user_full_name = message.from_user.full_name
#     user_username = message.from_user.username
#     user_role = get_role(user_id)
#     user_waiting_for_action_state = get_role_waiting_for_action_state(user_role)
#     user_keyboard = get_role_keyboard(user_role)
#     # print(f"feedback from {user_role} {user_id} ({user_full_name}): {feedback_text}")
#     # feedback_msg = f"Сообщение от @{user_username}\n" \
#     #                f"{user_full_name}\n" \
#     #                f"роль: {user_role}\n\n{feedback_text}"
#     feedback_msg = text(bold(f"Сообщение от @{user_username} id: {user_id}\n"),
#                         code(f"{user_full_name}\n"),
#                         italic(f"роль: {escape_md(user_role)}\n\n"),  # не добавлять в роль _ (будет конфликт с italic)
#                         md_shielding(str(feedback_text))
#                         )
#     print(feedback_msg)
#     try:
#         await bot.send_message(feedback_tg_id, feedback_msg, parse_mode=ParseMode.MARKDOWN)
#     except (BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError) as e:
#         print("Отправка фидбека не удалась")
#         print(e)
#         await message.answer("К сожалению отправка фидбека не удалась", reply_markup=user_keyboard)
#     else:
#         await message.answer("Сообщение отправлено", reply_markup=user_keyboard)
#     await user_waiting_for_action_state.set()
def define_broadcast_targets_set(broadcast_target: str) -> set:
    targets_set = set()
    if broadcast_target == "all":
        targets_set = get_all_users()
    elif broadcast_target.isdigit():
        targets_set = {int(broadcast_target)}
    elif broadcast_target in role_by_name.keys():
        targets_set = get_users_by_role(role_by_name.get(broadcast_target))
    print(broadcast_target, targets_set)
    return targets_set


@dp.message_handler(state=BroadcastSteps.waiting_for_broadcast_message)
async def text_for_broadcast_gotten(message: types.Message, state: FSMContext):
    broadcast_start_time = datetime.now()

    broadcast_target = (await state.get_data()).get('broadcast_target')
    targets_set = define_broadcast_targets_set(broadcast_target)
    targets_count = len(targets_set)

    bad_targets_count = 0
    text_to_broadcast = abg.md_format(message.md_text)
    print(f"Текстовая рассылка target = {broadcast_target}")
    print(text_to_broadcast)
    # print(message.text)
    # print(message.as_json())
    # print(abg.md_format(message.md_text))
    user_id = message.from_user.id
    user_role = get_role(user_id)
    await get_role_waiting_for_action_state(user_role).set()
    await message.answer(f"Рассылаю {targets_count} пользователям", reply_markup=get_role_keyboard(user_role))

    if not allow_broadcasts:
        broadcast_from_text = f"От пользователя {message.from_user.username}[{message.from_user.id}]\n" \
                              f"{message.from_user.full_name}\n поступил запрос на рассылку текста: \n" \
                              f"{message.text}\n\n" \
                              f"Вы видите это сообщение, потомучто рассылки отключены в настройках бота"
        print(broadcast_from_text)
        await notify_admins(broadcast_from_text)
        return

    progress_percents = 0
    progress_message: types.Message = await message.answer(
        f"Рассылка: {other.progress_bar(progress_percents)} (0/{targets_count})")

    for (index, user_id) in enumerate(targets_set):
        try:

            pass
            time.sleep(0.2)
            await bot.send_message(user_id, text_to_broadcast, parse_mode=ParseMode.MARKDOWN)
            pass

        except BotBlocked:
            print(f"Targetu [ID:{user_id}]: blocked by user")
            bad_targets_count += 1
        except ChatNotFound:
            print(f"Target [ID:{user_id}]: invalid user ID")
            bad_targets_count += 1
        except RetryAfter as e:
            print(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
            bad_targets_count += 1
            await asyncio.sleep(e.timeout)
        except UserDeactivated:
            print(f"Target [ID:{user_id}]: user is deactivated")
            bad_targets_count += 1
        except TelegramAPIError:
            print(f"Target [ID:{user_id}]: failed")
            bad_targets_count += 1
        finally:
            progress_percents = int(round((index + 1) / targets_count, 2) * 100)
            await progress_message.edit_text(
                f"Рассылка: {other.progress_bar(progress_percents)} ({index + 1}/{targets_count})")
    broadcast_length_time = (datetime.now() - broadcast_start_time).seconds
    print(broadcast_length_time, "секунд заняла рассылка. Рассылка окончена")
    await message.reply(
        f"Разослано {targets_count - bad_targets_count} сообщений. {bad_targets_count} не удалось отправить.\n"
        f"Рассылка заняла {broadcast_length_time} секунд")


@dp.message_handler(state=BroadcastSteps.waiting_for_broadcast_message, content_types=types.ContentType.PHOTO)
async def photo_for_broadcast_gotten(message: types.Message, state: FSMContext):
    broadcast_start_time = datetime.now()

    broadcast_target = (await state.get_data()).get('broadcast_target')
    targets_set = define_broadcast_targets_set(broadcast_target)
    targets_count = len(targets_set)

    bad_users_count = 0
    print(f"Текстовая рассылка target = {broadcast_target}")
    photo_to_broadcast = message.photo[-1].file_id
    user_id = message.from_user.id
    user_role = get_role(user_id)
    await get_role_waiting_for_action_state(user_role).set()
    await message.answer(f"Рассылаю {targets_count} пользователям", reply_markup=get_role_keyboard(user_role))

    if not allow_broadcasts:
        broadcast_from_text = f"От пользователя {message.from_user.username}[{message.from_user.id}]\n" \
                              f"{message.from_user.full_name}\n поступил запрос на рассылку изображения\n\n" \
                              f"Вы видите это сообщение, потомучто рассылки отключены в настройках бота"
        print(broadcast_from_text)
        await notify_admins(broadcast_from_text)
        await notify_admins_photo(photo_to_broadcast)
        return

    progress_percents = 0
    progress_message: types.Message = await message.answer(
        f"Рассылка: {other.progress_bar(progress_percents)} (0/{targets_count})")
    for (index, user_id) in enumerate(targets_set):
        try:
            pass
            time.sleep(0.2)
            await bot.send_photo(user_id, photo_to_broadcast)
            pass

        except (BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError):
            print(f"Target [ID:{user_id}]: fault")
            # print(e)
            bad_users_count += 1
        finally:
            progress_percents = int(round((index + 1) / targets_count, 2) * 100)
            await progress_message.edit_text(
                f"Рассылка: {other.progress_bar(progress_percents)} ({index + 1}/{targets_count})")

    broadcast_length_time = (datetime.now() - broadcast_start_time).seconds
    print(broadcast_length_time, "секунд заняла рассылка. Рассылка окончена")
    await message.reply(
        f"Разослано {targets_count - bad_users_count} сообщений. {bad_users_count} не удалось отправить.\n"
        f"Рассылка заняла {broadcast_length_time} секунд")







