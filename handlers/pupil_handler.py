from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot_storage.rasp_base import get_lessons_for_today, get_lessons_for_yesterday, check_for_class, get_lessons_by_day
from bot_storage.rasp_base import get_all_classes
from bot import dp, bot
from bot_storage.Keyboards import pupil_kb, rasp_by_days_kb, InlineKeyboardButton, InlineKeyboardMarkup
from bot_storage import roles_base
from aiogram.types import ParseMode

from actions import feedback


class PupilStates(StatesGroup):
    waiting_for_class_name = State()  # ожидание номера класса
    waiting_for_action = State()  # ожидание действий
    waiting_for_identifier = State()  # ждет название класса
    waiting_for_registration = State()
    waiting_for_other_class_name = State()  # для другого класса


@dp.message_handler(state=PupilStates.waiting_for_registration, content_types=types.ContentType.TEXT)
async def reg_class(message: types.Message, state: FSMContext):
    class_name = message.text.replace(" ", "")
    user_id = message.from_user.id
    if check_for_class(class_name):
        roles_base.reg_class(user_id, class_name)
        # print("Регистрация в классе", class_name)
        await state.update_data(class_name=class_name)
        await message.answer("Окей, ты зарегистрирован", reply_markup=pupil_kb)
        await message.answer("Теперь ты можешь узнать расписание")
        await PupilStates.waiting_for_action.set()
    else:
        await message.answer("Не могу найти такого класса, введите еще раз")
        # classes_set = get_all_classes()
        # classes_choose_list = []
        # classes_choose_list_kb = InlineKeyboardMarkup(row_width=2)
        # for class_name in classes_set:
        #     if class_name.find(class_name) >= 0:
        #         classes_choose_list.append(class_name)
        #         class_name_button = InlineKeyboardButton(class_name.upper(), callback_data=class_name)
        #         classes_choose_list_kb.insert(class_name_button)
        # if len(classes_choose_list) < 1:
        #     await message.reply("Не могу найти такого класса, введите еще раз")
        # elif len(classes_choose_list) > 1:
        #     await message.answer("Выберите из списка", reply_markup=classes_choose_list_kb)
        # elif len(classes_choose_list) == 1:
        #     roles_base.set_identifier(user_id, class_name.title())
        #     await state.update_data(class_name=class_name)
        #     await bot.send_message(user_id, "Отлично", reply_markup=pupil_kb)
        #     await bot.send_message(user_id, "Теперь вы можете узнать расписание")
        #     await PupilStates.waiting_for_action.set()


# @dp.callback_query_handler(state=PupilStates.waiting_for_registration)
# async def reg_teacher_full_name_inline(callback_query: types.CallbackQuery, state: FSMContext):
#     await bot.answer_callback_query(callback_query.id)
#     await PupilStates.waiting_for_action.set()
#     await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
#
#     class_name = callback_query.data.replace(" ", "")
#     user_id = callback_query.from_user.id
#     classes_set = set(map(str.lower, get_all_classes()))
#     if class_name.lower() in classes_set:
#         roles_base.set_identifier(user_id, class_name.title())
#         await state.update_data(class_name=class_name)
#         await bot.send_message(user_id, "Отлично", reply_markup=pupil_kb)
#         await bot.send_message(user_id, "Теперь вы можете узнать расписание")
#         await PupilStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text in ["На сегодня", "На завтра"], state=PupilStates.waiting_for_action)
async def rasp_today_yesterday(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    # role = user_data['chosen_role']
    role = roles_base.get_role(message.from_user.id)
    class_name = user_data['class_name']
    print(role, "запросил расписание", message.text)

    if class_name is not None:
        if message.text.lower() == "на сегодня":
            lessons = get_lessons_for_today(class_name)
            await message.answer(lessons, parse_mode=ParseMode.MARKDOWN)
            await PupilStates.waiting_for_action.set()
        if message.text.lower() == "на завтра":
            lessons = get_lessons_for_yesterday(class_name)
            # print("прямо перед отправкой", lessons)
            await message.answer(lessons, parse_mode=ParseMode.MARKDOWN)
            await PupilStates.waiting_for_action.set()
        return

    print("класс не указан", user_data)
    await message.answer("Укажите свой класс, пожалуйста")
    await PupilStates.waiting_for_registration.set()


@dp.message_handler(lambda m: m.text == "По дням", state=PupilStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def rasp_by_day(message: types.Message, state: FSMContext):
    # print("Запрос по дням, отправляю inline клавиатуру")
    await message.answer("Выберите день", reply_markup=rasp_by_days_kb)


@dp.callback_query_handler(lambda cq: cq.data in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
                           state=PupilStates.waiting_for_action,)
async def rasp_by_day_inline_handler(callback_query: types.CallbackQuery, state: FSMContext):
    # print("пришел callback на расписание по дням")
    callback_data_text = {'monday': "понедельник", 'tuesday': "вторник", 'wednesday': "Среда",
                          'thursday': "четверг", 'friday': "пятница", 'saturday': "суббота", 'sunday': "воскресенье"}
    callback_data = callback_query.data
    user_data = await state.get_data()
    class_name = user_data['class_name']
    if 'other_class_name' in user_data:
        if user_data['other_class_name'] is not None:
            class_name = user_data['other_class_name']

    print(class_name, "запрос расписания на", callback_data)
    lessons = "Нет уроков"
    if class_name is not None:
        print(callback_data)
        lessons = get_lessons_by_day(callback_data_text[callback_data], class_name)
        # print(lessons)
        await PupilStates.waiting_for_action.set()
    else:
        await PupilStates.waiting_for_class_name.set()
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Напомните номер класса, пожалуйста")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, lessons, parse_mode=ParseMode.MARKDOWN)
    await state.update_data(other_class_name=None)
    # await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
    #                                     message_id=callback_query.message.message_id,
    #                                     reply_markup=ReplyKeyboardRemove)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.message_handler(lambda m: m.text == "Для другого класса", state=PupilStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def req_rasp_for_other_class(message: types.Message, state: FSMContext):
    # print("запрос расписания для другого класса")
    await message.answer("Для какого класса вы хотите узнать расписание?")
    await PupilStates.waiting_for_other_class_name.set()


@dp.message_handler(state=PupilStates.waiting_for_other_class_name, content_types=types.ContentType.TEXT)
async def rasp_for_other_class(message: types.Message, state: FSMContext):
    # print("Запрос для другого класса: ")
    other_class_name = message.text.replace(" ", "")
    if not check_for_class(other_class_name):
        await message.reply("Не могу найти такого класса")
        await PupilStates.waiting_for_action.set()
        return
    await state.update_data(other_class_name=other_class_name)
    await message.answer("Расписание для " + other_class_name + "\nВыберите день недели",
                         reply_markup=rasp_by_days_kb)
    await PupilStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=PupilStates.waiting_for_action)
async def rasp_yesterday(message: types.Message):
    print("Запрос расписания учителей учеником")


@dp.message_handler(lambda m: m.text == "Обратная связь", state=PupilStates.waiting_for_action)
async def pupil_feedback(message: types.Message):
    await message.reply("Что вы хотите сообщить?", reply_markup=feedback.cancel_feedback_kb)
    await feedback.make_feedback(PupilStates.waiting_for_action, end_keyboard=pupil_kb)





