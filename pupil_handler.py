from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from rasp_base import get_lessons, get_lessons_for_today, get_lessons_for_yesterday, get_all_classes
from bot import dp
from Keyboards import pupil_kb

# logging.basicConfig(filename='tatgram_rasp34.log', level=logging.DEBUG)


class PupilStates(StatesGroup):
    rasp_today = State()  # расписание на сегодня
    rasp_yesterday = State()  # расписание на завтра
    waiting_for_action = State()  # ожидание действий
    waiting_for_identifier = State()  # ждет название класса
    waiting_for_registration = State()


@dp.message_handler(state=PupilStates.waiting_for_registration, content_types=types.ContentType.TEXT)
async def rasp_today(message: types.Message, state: FSMContext):
    classes_set = get_all_classes()
    print(classes_set)
    class_name = message.text
    if class_name in classes_set:
        await state.update_data(class_name=message.text)
        await message.answer("Окей, ты зарегистрирован", reply_markup=pupil_kb)
        await PupilStates.waiting_for_action.set()
    else:
        await message.answer("Не могу найти такого класса")


@dp.message_handler(lambda m: m.text in ["На сегодня", "На завтра"], state=PupilStates.waiting_for_action)
async def rasp_today(message: types.Message, state: FSMContext):
    # print("УФХЦЧШЦХЗ")
    user_data = await state.get_data()
    # print(message.text)
    # print(user_data)
    #
    # cur_state = await state.get_state()
    # print(cur_state)
    role = user_data['chosen_role']
    print("Мне написал", role)

    await message.answer("Укажите свой класс, пожалуйста")
    # await RaspBotStates.wait_for_class_name_rasp_today.set()
    if message.text == "На сегодня":
        await PupilStates.rasp_today.set()
    if message.text == "На завтра":
        await PupilStates.rasp_yesterday.set()


@dp.message_handler(state=PupilStates.rasp_today, content_types=types.ContentType.TEXT)  # на сегодня
async def rasp_today(message: types.Message, state: FSMContext):
    # cur_state = await state.get_state()
    # print(cur_state)

    rasp_lessons = get_lessons_for_today(message.text)
    await message.answer(rasp_lessons)
    await PupilStates.waiting_for_action.set()


@dp.message_handler(state=PupilStates.rasp_yesterday, content_types=types.ContentType.TEXT)  # на завтра
async def rasp_today(message: types.Message, state: FSMContext):
    # cur_state = await state.get_state()
    # print(cur_state)

    rasp_lessons = get_lessons_for_yesterday(message.text)
    await message.answer(rasp_lessons)
    await PupilStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=PupilStates.waiting_for_action)
async def rasp_yesterday(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    role = user_data['chosen_role']
    print("Мне написал", role)

    await message.reply("В базе данных пока нет информации об учителях")


@dp.message_handler(lambda m: m.text == "Отправить фото", state=PupilStates.waiting_for_action)
async def rasp_yesterday(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    role = user_data['chosen_role']
    print("Мне написал", role)

    await message.reply("В разработке")