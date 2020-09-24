from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage import bot_stats
from bot_storage.roles_base import get_all_users
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError
import asyncio
from bot_storage import rasp_base
from bot_storage.Keyboards import rasp_by_days_kb, secret_role_cancel_kb, secret_role_kb
from bot_storage.Keyboards import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ParseMode


class MasterStates(StatesGroup):
    waiting_for_action = State()  # ожидание действий
    waiting_for_text_to_broadcast = State()
    waiting_for_class_name = State()
    waiting_for_teacher_name = State()

@dp.message_handler(lambda m: m.text == "Статистика", state=MasterStates.waiting_for_action)
async def stats(message: types.Message, state: FSMContext):
    usage_stats = bot_stats.get_stats()
    await message.answer(usage_stats)


@dp.message_handler(lambda m: m.text == "Рассылка", state=MasterStates.waiting_for_action)
async def broadcast(message: types.Message, state: FSMContext):
    await message.answer("Введите текст или картинку для рассылки", reply_markup=secret_role_cancel_kb)
    await MasterStates.waiting_for_text_to_broadcast.set()


@dp.message_handler(lambda m: m.text == "Отмена", state=MasterStates.waiting_for_text_to_broadcast)
async def broadcast(message: types.Message, state: FSMContext):
    await message.answer("Хорошо", reply_markup=secret_role_kb)
    await MasterStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text == "Расписание школьников", state=MasterStates.waiting_for_action)
async def pupils_rasp(message: types.Message):
    await message.answer("Для какого класса?")
    await MasterStates.waiting_for_class_name.set()


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=MasterStates.waiting_for_action)
async def teachers_rasp(message: types.Message):
    await message.answer("Введите имя учителя")
    await MasterStates.waiting_for_teacher_name.set()


@dp.message_handler(state=MasterStates.waiting_for_class_name)
async def pupil_rasp_2(message: types.Message, state: FSMContext):
    # classes_set = rasp_base.get_all_classes()
    class_name = message.text.lower()
    if rasp_base.check_for_class(class_name):
        await state.update_data(rasp_for_class=class_name)
        await message.answer("Выберите день", reply_markup=rasp_by_days_kb)
        await MasterStates.waiting_for_action.set()
    else:
        await message.reply("Такого класса нет в БД")


@dp.message_handler(state=MasterStates.waiting_for_teacher_name)
async def teachers_rasp_2(message: types.Message, state: FSMContext):
    teacher_name = message.text.lower()
    teachers_set = rasp_base.get_all_teachers()
    if teacher_name in teachers_set:
        await message.answer("День недели", reply_markup=rasp_by_days_kb)
        await state.update_data(rasp_for_teacher=teacher_name.title())
    else:
        teachers_choose_list = []
        teachers_choose_list_kb = InlineKeyboardMarkup(row_width=2)
        for teacher_full_name in teachers_set:
            if teacher_full_name.find(teacher_name) >= 0:
                teachers_choose_list.append(teacher_full_name)
                teacher_full_name_button = InlineKeyboardButton(teacher_full_name.title(), callback_data=teacher_full_name)
                teachers_choose_list_kb.insert(teacher_full_name_button)
        if len(teachers_choose_list) == 1:
            await message.answer("День недели", reply_markup=rasp_by_days_kb)
            await state.update_data(rasp_for_teacher=teachers_choose_list[0].title())
        elif len(teachers_choose_list) < 1:
            await message.reply("Такого учителя нет в БД")
        elif len(teachers_choose_list) > 1:
            await message.answer("Выберите учителя из списка", reply_markup=teachers_choose_list_kb)
            return
    await MasterStates.waiting_for_action.set()


@dp.callback_query_handler(state=MasterStates.waiting_for_teacher_name)
async def teacher_full_name_inline(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    callback_data = callback_query.data
    teacher_name = callback_data
    await bot.send_message(callback_query.from_user.id, "День недели", reply_markup=rasp_by_days_kb)
    await state.update_data(rasp_for_teacher=teacher_name.title())
    await MasterStates.waiting_for_action.set()
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.message_handler(state=MasterStates.waiting_for_text_to_broadcast)
async def text_for_broadcast_gotten(message: types.Message):
    print("Текстовая рассылка")
    users_id_set = get_all_users()
    users_count = len(users_id_set)
    bad_users_count = 0
    text_to_broadcast = message.md_text
    print(text_to_broadcast)
    await message.answer(f"Рассылаю {users_count} пользователям", reply_markup=secret_role_kb)
    for user_id in users_id_set:
        try:
            await bot.send_message(user_id, text_to_broadcast, parse_mode=ParseMode.MARKDOWN)
            # await bot.send_photo(user_id, photo_to_broadcast)
        except BotBlocked:
            print(f"Target [ID:{user_id}]: blocked by user")
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
    await message.reply(f"Разослано {users_count-bad_users_count} сообщений. {bad_users_count} не удалось отправить")
    await MasterStates.waiting_for_action.set()


@dp.message_handler(state=MasterStates.waiting_for_text_to_broadcast, content_types=types.ContentType.PHOTO)
async def text_for_broadcast_gotten(message: types.Message):
    print("Рассылка фото")
    users_id_set = get_all_users()
    users_count = len(users_id_set)
    bad_users_count = 0
    # text_to_broadcast = message.md_text
    photo_to_broadcast = message.photo[-1].file_id
    # print(text_to_broadcast)
    await message.answer(f"Рассылаю {users_count} пользователям", reply_markup=secret_role_kb)
    for user_id in users_id_set:
        try:
            # await bot.send_message(user_id, text_to_broadcast, parse_mode=ParseMode.MARKDOWN)
            await bot.send_photo(user_id, photo_to_broadcast)
        except (BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError):
            print(f"Target [ID:{user_id}]: fault")
            bad_users_count += 1
    await message.reply(f"Разослано {users_count-bad_users_count} сообщений. {bad_users_count} не удалось отправить")
    await MasterStates.waiting_for_action.set()


@dp.callback_query_handler(state=MasterStates.waiting_for_action)
async def rasp_by_day_inline_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    callback_data_text = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
    callback_data = callback_query.data
    user_data = await state.get_data()
    # print(user_data)
    class_name = None
    teacher_name = None

    try:
        class_name = user_data['rasp_for_class']
    except KeyError:
        pass
    try:
        teacher_name = user_data['rasp_for_teacher']
    except KeyError:
        pass
    # print(class_name, teacher_name)

    if teacher_name is not None:
        teacher_lessons = rasp_base.get_teacher_lessons_for_week_day(teacher_name, callback_data_text[callback_data])
        await bot.send_message(callback_query.from_user.id, teacher_lessons, parse_mode=ParseMode.MARKDOWN)
        await state.update_data(rasp_for_teacher=None)
        await state.update_data(rasp_for_class=None)
    if class_name is not None:
        pupils_lessons = rasp_base.get_lessons_for_week_day(class_name, callback_data_text[callback_data])
        await bot.send_message(callback_query.from_user.id, pupils_lessons, parse_mode=ParseMode.MARKDOWN)
        await state.update_data(rasp_for_teacher=None)
        await state.update_data(rasp_for_class=None)
    # else:
    #     await bot.send_message(callback_query.from_user.id, f"Какая-то ошибка произошла\n{teacher_name}\n{class_name}")
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


