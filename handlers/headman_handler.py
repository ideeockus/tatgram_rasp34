from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot_storage.rasp_base import get_lessons_for_today, get_lessons_for_yesterday, check_for_class, get_lessons_by_day
from bot_storage.rasp_base import get_all_teachers, get_teacher_lessons_for_week_day
from bot import dp, bot
from bot_storage.Keyboards import headman_kb, rasp_by_days_kb, InlineKeyboardButton, InlineKeyboardMarkup
from bot_storage import roles_base
from aiogram.types import ParseMode

from actions import feedback


class HeadmanStates(StatesGroup):
    waiting_for_class_name = State()  # ожидание номера классаpupil_kb
    waiting_for_action = State()  # ожидание действий
    waiting_for_identifier = State()  # ждет название класса
    waiting_for_registration = State()
    waiting_for_other_class_name = State()  # для другого класса
    waiting_for_teacher_name = State()

    waiting_for_day_for_teacher_rasp = State()
    waiting_for_day_for_pupil_rasp = State()


@dp.message_handler(state=HeadmanStates.waiting_for_registration, content_types=types.ContentType.TEXT)
async def reg_class(message: types.Message, state: FSMContext):
    class_name = message.text.replace(" ", "")
    user_id = message.from_user.id
    roles_base.reg_class(user_id, class_name)
    if check_for_class(class_name):
        # print("Регистрация в классе", class_name)
        await state.update_data(class_name=class_name)
        await message.answer(f"Окей, ты зарегистрирован как староста {class_name}", reply_markup=headman_kb)
        await message.answer("Теперь ты можешь узнать расписание")
        await HeadmanStates.waiting_for_action.set()
    else:
        await message.answer("Не могу найти такого класса, введите еще раз")


@dp.message_handler(lambda m: m.text in ["На сегодня", "На завтра"], state=HeadmanStates.waiting_for_action)
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
            await HeadmanStates.waiting_for_action.set()
        if message.text.lower() == "на завтра":
            lessons = get_lessons_for_yesterday(class_name)
            await message.answer(lessons, parse_mode=ParseMode.MARKDOWN)
            await HeadmanStates.waiting_for_action.set()
        return

    print("класс не указан", user_data)
    await message.answer("Укажите свой класс, пожалуйста")
    await HeadmanStates.waiting_for_registration.set()


@dp.message_handler(lambda m: m.text == "По дням", state=HeadmanStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def rasp_by_day(message: types.Message, state: FSMContext):
    # print("Запрос по дням, отправляю inline клавиатуру")
    await message.answer("Выберите день", reply_markup=rasp_by_days_kb)
    await HeadmanStates.waiting_for_day_for_pupil_rasp.set()


@dp.callback_query_handler(lambda cq: cq.data in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
                           state=HeadmanStates.waiting_for_day_for_pupil_rasp)
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
        await HeadmanStates.waiting_for_action.set()
    else:
        await HeadmanStates.waiting_for_class_name.set()
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Напомните номер класса, пожалуйста")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, lessons, parse_mode=ParseMode.MARKDOWN)
    await state.update_data(other_class_name=None)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.message_handler(lambda m: m.text == "Для другого класса", state=HeadmanStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def req_rasp_for_other_class(message: types.Message, state: FSMContext):
    # print("запрос расписания для другого класса")
    await message.answer("Для какого класса вы хотите узнать расписание?")
    await HeadmanStates.waiting_for_other_class_name.set()


@dp.message_handler(state=HeadmanStates.waiting_for_other_class_name, content_types=types.ContentType.TEXT)
async def rasp_for_other_class(message: types.Message, state: FSMContext):
    # print("Запрос для другого класса: ")
    other_class_name = message.text.replace(" ", "")
    if not check_for_class(other_class_name):
        await message.reply("Не могу найти такого класса")
        await HeadmanStates.waiting_for_action.set()
        return
    await state.update_data(other_class_name=other_class_name)
    await message.answer("Расписание для " + other_class_name + "\nВыберите день недели",
                         reply_markup=rasp_by_days_kb)
    await HeadmanStates.waiting_for_day_for_pupil_rasp.set()


@dp.message_handler(lambda m: m.text == "Обратная связь", state=HeadmanStates.waiting_for_action)
async def pupil_feedback(message: types.Message):
    await message.reply("Что вы хотите сообщить?", reply_markup=feedback.cancel_feedback_kb)
    await feedback.make_feedback(HeadmanStates.waiting_for_action, end_keyboard=headman_kb)


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=HeadmanStates.waiting_for_action)
async def teacher_rasp(message: types.Message, state: FSMContext):
    print("Запрос расписания учителей старостой")
    # user_data = await state.get_data()
    # if 'teacher_name' in user_data:
    #     last_teacher_kb = InlineKeyboardMarkup(row_width=2)
    #     last_teacher_button = InlineKeyboardButton(user_data['teacher_name'].title(), callback_data=user_data['teacher_name'])
    #     new_teacher_button = InlineKeyboardButton("Для другого учителя", callback_data="other_teacher")
    #     last_teacher_kb.add(last_teacher_button, new_teacher_button)
    #     await message.answer("Для кого хотите узнать расписание?", reply_markup=last_teacher_kb)
    #     await HeadmanStates.waiting_for_teacher_name.set()
    #     return
    await message.reply("Введите имя, пожалуйста")
    await HeadmanStates.waiting_for_teacher_name.set()


@dp.message_handler(state=HeadmanStates.waiting_for_teacher_name, content_types=types.ContentType.TEXT)
async def get_teacher_name(message: types.Message, state: FSMContext):
    teacher_name = message.text.lower()
    print("запрошено раписание учителя", teacher_name)
    teachers_set = get_all_teachers()
    # print(teachers_set)
    if teacher_name in teachers_set:
        await message.answer("Хорошо, выберите день недели", reply_markup=rasp_by_days_kb)
        await state.update_data(rasp_for_teacher=teacher_name.title())
        await HeadmanStates.waiting_for_day_for_teacher_rasp.set()
    else:
        teachers_choose_list = []
        teachers_choose_list_kb = InlineKeyboardMarkup(row_width=2)
        for teacher_full_name in teachers_set:
            if teacher_full_name.find(teacher_name) >= 0:
                teachers_choose_list.append(teacher_full_name)
                teacher_full_name_button = InlineKeyboardButton(teacher_full_name.title(), callback_data=teacher_full_name)
                teachers_choose_list_kb.insert(teacher_full_name_button)
        if len(teachers_choose_list) < 1:
            await message.reply("Я не нашел такого учителя")
            await HeadmanStates.waiting_for_action.set()
        elif len(teachers_choose_list) >= 1:
            await message.answer("Выберите учителя из списка", reply_markup=teachers_choose_list_kb)
            # await HeadmanStates.waiting_for_action.set()

@dp.callback_query_handler(lambda cq: cq.data not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
                           state=HeadmanStates.waiting_for_teacher_name)
async def teacher_full_name_inline(callback_query: types.CallbackQuery, state: FSMContext):
    callback_data = callback_query.data
    teacher_name = callback_data

    await state.update_data(teacher_name=teacher_name)

    print("выбор", teacher_name, "с инлайн клавиатуры")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Хорошо, выберите день недели", reply_markup=rasp_by_days_kb)
    await state.update_data(rasp_for_teacher=teacher_name.title())
    await HeadmanStates.waiting_for_day_for_teacher_rasp.set()
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda cq: cq.data in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
                           state=HeadmanStates.waiting_for_day_for_teacher_rasp,)
async def rasp_by_day_inline_handler(callback_query: types.CallbackQuery, state: FSMContext):
    # print("пришел callback на расписание по дням")
    callback_data_text = {'monday': 0, 'tuesday': 1, 'wednesday': 2,
                          'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
    callback_data = callback_query.data
    user_data = await state.get_data()
    teacher_name = user_data['rasp_for_teacher']
    print("запрос расписания для", teacher_name, "на", callback_data)
    lessons = "Нет уроков"
    if teacher_name is not None:
        # print(callback_data)
        lessons = get_teacher_lessons_for_week_day(teacher_name, callback_data_text[callback_data])
        await HeadmanStates.waiting_for_action.set()
    else:
        await HeadmanStates.waiting_for_teacher_name.set()
        await bot.send_message(chat_id=callback_query.message.chat.id, text="для кого вы хотите узнать распиание?")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, lessons, parse_mode=ParseMode.MARKDOWN)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.message_handler(state=HeadmanStates.waiting_for_day_for_pupil_rasp)
async def waiting_for_day_for_pupil_rasp_unrecognized_message(message: types.Message, state: FSMContext):
    await message.answer("Выберите день")
    # await HeadmanStates.waiting_for_action.set()


@dp.message_handler(state=HeadmanStates.waiting_for_day_for_teacher_rasp)
async def waiting_for_day_for_teacher_rasp_unrecognized_message(message: types.Message, state: FSMContext):
    await message.answer("Выберите день")



