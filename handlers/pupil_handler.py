from aiogram import types
from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup
from bot_storage.UserStates import PupilStates
from bot_storage.rasp_base import get_lessons_for_today, get_lessons_for_yesterday
from bot_storage.rasp_base import get_all_classes
from bot import dp
from bot_storage.Keyboards import pupil_kb, headman_kb
from bot_storage import roles_base
from aiogram.types import ParseMode
from actions import pupils_rasp, teachers_rasp, feedback
from utils.abg import abg_lost_role


# class PupilStates(StatesGroup):
#     waiting_for_class_name = State()  # ожидание номера класса
#     waiting_for_action = State()  # ожидание действий
#     waiting_for_identifier = State()  # ждет название класса
#     waiting_for_registration = State()
#     waiting_for_other_class_name = State()  # для другого класса


def get_current_kb(user_id):
    current_role = roles_base.get_role(user_id)
    current_kb = pupil_kb
    if current_role == "pupil":
        current_kb = pupil_kb
    if current_role == "headman":
        current_kb = headman_kb
    return current_kb


@dp.message_handler(state=PupilStates.waiting_for_registration, content_types=types.ContentType.TEXT)
async def reg_class(message: types.Message):
    class_name = message.text.replace(" ", "")
    user_id = message.from_user.id
    classes_set = set(map(str.lower, get_all_classes()))
    if class_name in classes_set:
        roles_base.set_class_name(user_id, class_name)
        # user_kb = headman_kb if roles_base.get_role(user_id) == "headman" else get_current_kb(user_id)
        await message.answer("Окей, ты зарегистрирован", reply_markup=get_current_kb(user_id))
        await message.answer("Теперь ты можешь узнать расписание")
        await PupilStates.waiting_for_action.set()
    else:
        await message.answer("Не могу найти такого класса, введите еще раз")


@dp.message_handler(lambda m: m.text in ["На сегодня", "На завтра"], state=PupilStates.waiting_for_action)
async def rasp_today_yesterday(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    role = roles_base.get_role(user_id)
    class_name = roles_base.get_class_name(user_id)
    print(role, "запросил расписание", message.text)

    if class_name is not None:
        if message.text.lower() == "на сегодня":
            lessons = get_lessons_for_today(class_name)
            await message.answer(lessons, parse_mode=ParseMode.MARKDOWN)
            await PupilStates.waiting_for_action.set()
        if message.text.lower() == "на завтра":
            lessons = get_lessons_for_yesterday(class_name)
            await message.answer(lessons, parse_mode=ParseMode.MARKDOWN)
            await PupilStates.waiting_for_action.set()
    else:
        # await abg_lost_role(message, state)

        print(f"класс пользователя [{message.from_user.id}] не указан")
        await message.answer("Укажите свой класс, пожалуйста")
        await PupilStates.waiting_for_registration.set()


@dp.message_handler(lambda m: m.text == "По дням", state=PupilStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def rasp_by_day(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    class_name = roles_base.get_class_name(user_id)
    if class_name is None:
        # await abg_lost_role(message, state)

        print(f"класс пользователя [{message.from_user.id}] не указан")
        await message.answer("Укажите свой класс, пожалуйста")
        await PupilStates.waiting_for_registration.set()
        # await message.answer("Упс, я не помню в каком вы классе")
        # await message.answer("Введите свой класс")
        # await PupilStates.waiting_for_registration.set()
        return
    await state.update_data(class_name=class_name)
    await pupils_rasp.make_pupil_rasp_request(message, class_name)


@dp.message_handler(lambda m: m.text == "Для другого класса", state=PupilStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def req_rasp_for_other_class(message: types.Message):
    user_id = message.from_user.id
    await pupils_rasp.make_pupil_rasp_request(message)


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=PupilStates.waiting_for_action)
async def teacher_rasp(message: types.Message):
    user_id = message.from_user.id
    print("Запрос расписания учителей учеником")
    await teachers_rasp.make_teacher_rasp_request(message)


@dp.message_handler(lambda m: m.text == "Обратная связь", state=PupilStates.waiting_for_action)
async def pupil_feedback(message: types.Message):
    user_id = message.from_user.id
    await message.reply("Что вы хотите сообщить?", reply_markup=feedback.cancel_kb)
    await feedback.make_feedback()





