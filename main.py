from aiogram import executor, types
from bot_storage.Keyboards import teacher_kb, choose_role_kb, headman_kb
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from handlers import teacher_handler, pupil_handler, master_handler, headman_handler
from bot_storage.Keyboards import ReplyKeyboardRemove, secret_role_kb
from bot_storage import roles_base
from bot_storage.configuration import botmaster_role_phrase


class MainStates(StatesGroup):
    wait_for_role = State()


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    print("start", message.from_user)
    await state.finish()
    """
    This handler will be called when user sends `/start` command
    """
    await message.answer("Здравствуйте. \n Выберите свою роль", reply_markup=choose_role_kb)
    await MainStates.wait_for_role.set()


@dp.message_handler(lambda m: m.text in ["Учитель", "Ученик", "Родитель", "Староста", botmaster_role_phrase], state=MainStates.wait_for_role)
async def choose_role(message: types.Message, state: FSMContext):
    cur_state = await state.get_state()
    print(cur_state)

    roles_list = {'Ученик': "pupil", 'Учитель': "teacher", 'Родитель': "parent",
                  botmaster_role_phrase: "master", "Староста": "headman"}
    role = roles_list[message.text]
    # await state.update_data(chosen_role=role)
    user_id = message.from_user.id
    if roles_base.get_role(user_id) is None:
        username = message.from_user.username
        user_fullname = message.from_user.full_name
        roles_base.reg_new(user_id, role, username=username, user_fullname=user_fullname)
    else:
        roles_base.change_role(user_id, role)

    if role == "pupil" or role == "parent":
        await message.reply("Введите свой класс", reply_markup=ReplyKeyboardRemove())
        await pupil_handler.PupilStates.waiting_for_registration.set()
    elif role == "teacher":
        await teacher_handler.TeacherStates.waiting_for_action.set()
        await message.reply("Принято.", reply_markup=teacher_kb)
    elif role == "master":
        await master_handler.MasterStates.waiting_for_action.set()
        await message.answer("Master role activated", reply_markup=secret_role_kb)
    elif role == "headman":
        await headman_handler.HeadmanStates.waiting_for_registration.set()
        await message.answer("Введите свой класс", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=MainStates.wait_for_role)
async def choose_role(message: types.Message, state: FSMContext):
    await message.answer("Выберите роль с помощью кнопок")


@dp.message_handler()
async def unreg_msg(message: types.Message, state: FSMContext):
    print("Unregistered message")
    user_id = message.from_user.id
    user_role = roles_base.get_role(user_id)
    print(message.from_user.id, user_role)
    if user_role is None:
        await message.answer("Ой, я кажется забыл кто вы")
        await message.answer("Пожалуйста, выберите свою роль", reply_markup=choose_role_kb)
        await MainStates.wait_for_role.set()
    else:
        if user_role == "pupil" or user_role == "parent":
            user_class_name = roles_base.get_identifier(user_id)
            await state.update_data(class_name=user_class_name)
            # await message.answer(f"")
            await pupil_handler.PupilStates.waiting_for_action.set()
            if message.text in ["На сегодня", "На завтра"]:
                await pupil_handler.rasp_today_yesterday(message, state)
            elif message.text == "По дням":
                await pupil_handler.rasp_by_day(message, state)
            elif message.text == "Обратная связь":
                await pupil_handler.pupil_feedback(message)
            elif message.text == "Для другого класса":
                await pupil_handler.req_rasp_for_other_class(message, state)
            else:
                await message.answer("Здравствуйте", reply_markup=pupil_handler.pupil_kb)
            # await message.answer("Погодите, я кажется забыл в каком вы классе")
            # await message.reply("Введите свой класс", reply_markup=ReplyKeyboardRemove())
            # await pupil_handler.PupilStates.waiting_for_registration.set()
        elif user_role == "teacher":
            user_teacher_name = roles_base.get_identifier(user_id)
            await state.update_data(teacher_name=user_teacher_name.title())
            # await state.update_data(rasp_for_teacher=user_teacher_name.title())
            await teacher_handler.TeacherStates.waiting_for_action.set()
            # await message.reply("", reply_markup=teacher_kb)
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
            await message.answer("Master role activated", reply_markup=secret_role_kb)

        elif user_role == "headman":
            user_class_name = roles_base.get_identifier(user_id)
            await state.update_data(class_name=user_class_name)
            await headman_handler.HeadmanStates.waiting_for_action.set()
            if message.text in ["На сегодня", "На завтра"]:
                await headman_handler.rasp_today_yesterday(message, state)
            elif message.text == "По дням":
                await headman_handler.rasp_by_day(message, state)
            elif message.text == "Обратная связь":
                await headman_handler.pupil_feedback(message)
            elif message.text == "Для другого класса":
                await headman_handler.req_rasp_for_other_class(message, state)
            elif message.text == "Расписание учителей":
                await headman_handler.teacher_rasp(message, state)
            else:
                await message.answer("Здравствуйте", reply_markup=pupil_handler.pupil_kb)


@dp.message_handler(state="*")
async def other_msg(message: types.Message):
    print("other message")
    await message.reply("Не могу определить что мне нужно делать")


@dp.callback_query_handler(state="*")
async def rasp_by_day_inline_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)