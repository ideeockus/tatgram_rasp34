from aiogram import executor, types
from bot_storage.Keyboards import teacher_kb, choose_role_kb, headman_kb
from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup
from bot_storage.UserStates import MainStates
from bot import dp, bot
from handlers import common_handlers, teacher_handler, pupil_handler, master_handler
# from handlers import teacher_handler, pupil_handler, master_handler  # (it imports after start function)
from bot_storage.Keyboards import ReplyKeyboardRemove, secret_role_kb
from bot_storage import roles_base
from bot_storage.configuration import botmaster_role_phrase, feedback_tg_id, creator_id
from bot_storage.roles_base import get_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard
from periodic_operations import do_periodic_operation

# from datetime import datetime, timedelta, time
from bot_storage.bot_stats import clear_rasp_reqs_stat
import datetime

# class MainStates(StatesGroup):
#     wait_for_role = State()


# @dp.message_handler(commands=['start'], state="*")
# async def start(message: types.Message, state: FSMContext):
#     """
#     This handler will be called when user sends `/start` command
#     """
#     print("start", message.from_user)
#     await state.finish()
#     await message.answer("Здравствуйте. \n Выберите свою роль", reply_markup=choose_role_kb)
#     await MainStates.wait_for_role.set()

#
# from handlers import common_handlers, teacher_handler, pupil_handler, master_handler


@dp.message_handler(lambda m: m.text in ["Учитель", "Ученик", "Родитель", "Староста", botmaster_role_phrase],
                    state=MainStates.wait_for_role)
async def choose_role(message: types.Message, state: FSMContext):
    cur_state = await state.get_state()
    print(cur_state)

    roles_list = {'Ученик': "pupil", 'Учитель': "teacher", 'Родитель': "parent",
                  botmaster_role_phrase: "master", "Староста": "headman"}
    role = roles_list[message.text]
    user_id = message.from_user.id
    if roles_base.get_role(user_id) is None:
        username = message.from_user.username
        user_fullname = message.from_user.full_name
        roles_base.reg_new(user_id, role, username=username, user_fullname=user_fullname)
    else:
        roles_base.change_role(user_id, role)
        roles_base.set_teacher_name(user_id, None)
        roles_base.set_class_name(user_id, None)

    if role == "pupil" or role == "parent" or role == "headman":
        await message.reply("Введите свой класс", reply_markup=ReplyKeyboardRemove())
        await pupil_handler.PupilStates.waiting_for_registration.set()
    elif role == "teacher":
        await teacher_handler.TeacherStates.waiting_for_identifier.set()
        await message.reply("Введите ваше имя")
    elif role == "master":
        await master_handler.MasterStates.waiting_for_action.set()
        await message.answer("Master role activated", reply_markup=secret_role_kb)


@dp.message_handler(state=MainStates.wait_for_role)
async def choose_role(message: types.Message):
    await message.answer("Выберите роль с помощью кнопок")


# @dp.message_handler()
# async def unreg_msg(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     user_role = roles_base.get_role(user_id)
#     print("Unregistered message", user_id, user_role)
#     if user_role is None:
#         await message.answer("Ой, я кажется забыл кто вы")
#         await message.answer("Пожалуйста, выберите свою роль", reply_markup=choose_role_kb)
#         await MainStates.wait_for_role.set()
#     else:
#         if user_role == "pupil" or user_role == "parent" or user_role == "headman":
#             await pupil_handler.PupilStates.waiting_for_action.set()
#             if message.text in ["На сегодня", "На завтра"]:
#                 await pupil_handler.rasp_today_yesterday(message)
#             elif message.text == "По дням":
#                 await pupil_handler.rasp_by_day(message, state)
#             elif message.text == "Обратная связь":
#                 await pupil_handler.pupil_feedback(message)
#             elif message.text == "Для другого класса":
#                 await pupil_handler.req_rasp_for_other_class(message)
#             elif message.text == "Расписание учителей":
#                 await pupil_handler.teacher_rasp(message)
#             else:
#                 await message.answer("Здравствуйте", reply_markup=pupil_handler.pupil_kb)
#         elif user_role == "teacher":
#             await teacher_handler.TeacherStates.waiting_for_action.set()
#             if message.text == "Мое расписание":
#                 await teacher_handler.rasp(message, state)
#             elif message.text == "Расписание учителей":
#                 await teacher_handler.other_teachers_rasp(message)
#             elif message.text == "Отправить фото":
#                 await teacher_handler.wanna_send_photo(message)
#             else:
#                 await message.answer("Здравствуйте", reply_markup=teacher_handler.teacher_kb)
#         elif user_role == "master":
#             await master_handler.MasterStates.waiting_for_action.set()
#             await message.answer("Master role activated", reply_markup=secret_role_kb)


@dp.message_handler()
async def unregistered_msg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_role = roles_base.get_role(user_id)
    print("Unregistered message", user_id, user_role)
    if user_role is None:
        await message.answer("Ой, я кажется забыл кто вы")
        await message.answer("Пожалуйста, выберите свою роль", reply_markup=choose_role_kb)
        await MainStates.wait_for_role.set()
    else:
        await define_action(message, state)


async def define_action(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_role = roles_base.get_role(user_id)
    if user_role == "pupil" or user_role == "parent" or user_role == "headman":
        await pupil_handler.PupilStates.waiting_for_action.set()
        if message.text in ["На сегодня", "На завтра"]:
            await pupil_handler.rasp_today_yesterday(message, state)
        elif message.text == "По дням":
            await pupil_handler.rasp_by_day(message, state)
        elif message.text == "Обратная связь":
            await pupil_handler.pupil_feedback(message)
        elif message.text == "Для другого класса":
            await pupil_handler.req_rasp_for_other_class(message)
        elif message.text == "Расписание учителей":
            await pupil_handler.teacher_rasp(message)
        else:
            await message.answer("Здравствуйте", reply_markup=pupil_handler.pupil_kb)
    elif user_role == "teacher":
        await teacher_handler.TeacherStates.waiting_for_action.set()
        if message.text == "Мое расписание":
            await teacher_handler.rasp(message, state)
        elif message.text == "Расписание учителей":
            await teacher_handler.other_teachers_rasp(message)
        elif message.text == "Отправить фото":
            await teacher_handler.wanna_send_photo(message)
        else:
            await message.answer("Здравствуйте", reply_markup=teacher_handler.teacher_kb)
    elif user_role == "master":
        await master_handler.MasterStates.waiting_for_action.set()
        await message.answer("Здравствуйте. Уведомляю что с момента вашего последнего сообщения бот перезагружался",
                             reply_markup=secret_role_kb)
        if message.text == "Статистика":
            await master_handler.stats(message)
        elif message.text == "Рассылка":
            await master_handler.broadcast(message)
        elif message.text == "Расписание школьников":
            await master_handler.pupils_rasp(message)
        elif message.text == "Расписание учителей":
            await master_handler.teachers_rasp(message)
        elif message.text == "Загрузить расписание":
            await master_handler.upload_rasp(message)
        else:
            await message.answer("Команда не распознана")


# @dp.message_handler(lambda m: m.text == "Отмена", state="*", content_types=types.ContentType.TEXT)
# async def cancel_rasp_update(message: types.Message):
    # # current_kb = pupil_handler.pupil_kb
    # # current_state = pupil_handler.PupilStates.waiting_for_action
    # user_id = message.from_user.id
    # user_role = roles_base.get_role(user_id)
    # if user_role is None:
    #     await message.answer("Ой, я кажется забыл кто вы")
    #     await message.answer("Пожалуйста, выберите свою роль", reply_markup=choose_role_kb)
    #     await MainStates.wait_for_role.set()
    #
    # if user_role == "pupil" or user_role == "parent":
    #     current_kb = pupil_handler.pupil_kb
    #     current_state = pupil_handler.PupilStates.waiting_for_action
    # if user_role == "headman":
    #     current_kb = headman_kb
    #     current_state = pupil_handler.PupilStates.waiting_for_action
    # if user_role == "teacher":
    #     current_kb = teacher_kb
    #     current_state = teacher_handler.TeacherStates.waiting_for_action
    # if user_role == "master":
    #     current_kb = secret_role_kb
    #     current_state = master_handler.MasterStates.waiting_for_action
    #
    # await current_state.set()
    # await message.reply("Отменено", reply_markup=current_kb)
# @dp.message_handler(lambda m: m.text == "Отмена", state="*", content_types=types.ContentType.TEXT)
# async def cancel_rasp_update(message: types.Message):
#     user_id = message.from_user.id
#     user_role = get_role(user_id)
#     await get_role_waiting_for_action_state(user_role).set()
#     await message.reply("Отменено", reply_markup=get_role_keyboard(user_role))


@dp.message_handler(state="*")
async def other_msg(message: types.Message, state: FSMContext):
    print(f"other message, state: {await state.get_state()}; state_data: {await state.get_data()}")
    await message.reply("Не могу определить что мне нужно делать")


@dp.callback_query_handler(state="*")
async def empty_callback_query(callback_query: types.CallbackQuery, state: FSMContext):
    print(f"unrecognized callback query, callback_data: {callback_query.data}; state: {await state.get_state()}")
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.errors_handler()
async def error_handler(update: types.Update, exception: Exception):
    error_info_message = "Возникла какая-то ошибка 🙄, описание недоступно. Возможно пора вызывать магов 🔮\n\n"
    try:
        error_info_message = "🙄🙄🙄\nСообщение для администратора:\n" \
                             "Произошла ошибка при обработке сообщения пользователя " \
                             f"@{update.message.from_user.username} [{update.message.from_user.id}]\n" \
                             f"{update.message.from_user.full_name}\n" \
                             f"Сообщение: {update.message.text}\n\n" \
                             "Подробнее смотрите в логах.\n" + str(exception)
    except Exception as e:
        error_info_message += f"Ну, зато вот ошибка из-за которой описание недоступно:\n {e}\n\n"
        error_info_message += f"И еще вот какая-то штука:\n {str(exception)}"
    if feedback_tg_id == creator_id:
        await bot.send_message(creator_id, error_info_message)
        return
    await bot.send_message(feedback_tg_id, error_info_message)
    await bot.send_message(creator_id, error_info_message)
    # ## psycopg2.errors.AdminShutdown exception handler ?

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    # код не запустится и вообще решение не очень
    today_midnight = datetime.datetime.combine(datetime.datetime.now().date(),
                                               datetime.time(hour=23, minute=59, second=59))

    # do_periodic_operation(today_midnight,
    #                       datetime.datetime.now()+datetime.timedelta(days=365), 24*60*60, clear_rasp_reqs_stat())
