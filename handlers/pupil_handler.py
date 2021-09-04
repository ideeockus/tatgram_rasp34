from aiogram import types
from aiogram.dispatcher import FSMContext
from bot_storage.UserStates import PupilStates
from bot_storage.rasp_base import get_lessons_for_today, get_lessons_for_yesterday
from bot import dp
from bot_storage.accounts_base import get_role, get_sch_identifier
from aiogram.types import ParseMode
from actions import pupils_rasp, teachers_rasp, feedback, notify_actions
from bot_storage.Keyboards import cancel_kb

# TODO разделить функционал на common_pupil_handler, headman_handler, parent_handler
# parent: уведомление о входе / выходе, настройка свободного выхода


@dp.message_handler(text=["На сегодня", "На завтра"], state=PupilStates.waiting_for_action)
async def rasp_today_yesterday(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    role = get_role(user_id)
    class_name = get_sch_identifier(user_id)
    print(role, "запросил расписание", message.text)

    if class_name is not None:
        if message.text.lower() == "на сегодня":
            lessons = get_lessons_for_today(class_name)
            print(lessons)
            await message.answer(lessons, parse_mode=ParseMode.MARKDOWN_V2)
            await PupilStates.waiting_for_action.set()
        if message.text.lower() == "на завтра":
            lessons = get_lessons_for_yesterday(class_name)
            await message.answer(lessons, parse_mode=ParseMode.MARKDOWN_V2)
            await PupilStates.waiting_for_action.set()
    else:
        print(f"класс пользователя [{message.from_user.id}] не указан")
        await message.answer("Нужно авториоваться. Пожалуйста, введите /start")
        await notify_actions.notify_admins(f"Класс пользователя {user_id} не указан")
        # await message.answer("Укажите свой класс, пожалуйста")
        # await PupilStates.waiting_for_registration.set()


@dp.message_handler(text="По дням", state=PupilStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def rasp_by_day(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    class_name = get_sch_identifier(user_id)
    if class_name is None:
        print(f"класс пользователя [{message.from_user.id}] не указан")
        await message.answer("Нужно авториоваться. Пожалуйста, введите /start")
        await notify_actions.notify_admins(f"Класс пользователя {user_id} не указан")
        # await message.answer("Укажите свой класс, пожалуйста")
        # await PupilStates.waiting_for_registration.set()
        return
    await state.update_data(class_name=class_name)
    await pupils_rasp.make_pupil_rasp_request(message, class_name)


@dp.message_handler(lambda m: m.text == "Для другого класса", state=PupilStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def req_rasp_for_other_class(message: types.Message):
    # user_id = message.from_user.id
    await pupils_rasp.make_pupil_rasp_request(message)


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=PupilStates.waiting_for_action)
async def teacher_rasp(message: types.Message):
    # user_id = message.from_user.id
    print("Запрос расписания учителей учеником")
    await teachers_rasp.make_teacher_rasp_request(message)


@dp.message_handler(lambda m: m.text == "Обратная связь", state=PupilStates.waiting_for_action)
async def pupil_feedback(message: types.Message):
    # user_id = message.from_user.id
    await message.reply("Что вы хотите сообщить?", reply_markup=cancel_kb)
    await feedback.make_feedback()





