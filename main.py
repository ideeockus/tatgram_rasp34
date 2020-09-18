from aiogram import Bot, Dispatcher, executor, types, utils
from Keyboards import pupil_kb, teacher_kb, choose_role_kb
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp
import pupil_handler
import teacher_handler

# Configure logging
# logging.basicConfig(filename='tatgram_rasp34.log', level=logging.DEBUG)


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


@dp.message_handler(lambda m: m.text.lower() in ["учитель", "ученик", "родитель"], state=MainStates.wait_for_role)
async def choose_role(message: types.Message, state: FSMContext):
    cur_state = await state.get_state()
    print(cur_state)

    role = message.text.lower()
    await state.update_data(chosen_role=role)

    if role == "ученик":
        await message.reply("Введите свой класс")
        await pupil_handler.PupilStates.waiting_for_registration.set()
    elif role == "учитель":
        await teacher_handler.TeacherStates.waiting_for_action.set()
        await message.reply("Принято.", reply_markup=teacher_kb)


@dp.message_handler(state="*")
async def other_msg(message: types.Message, state: FSMContext):
    print("Unknown message")

    user_data = await state.get_data()
    if 'chosen_role' not in user_data.keys():
        await message.answer("Ой, я кажется забыл кто вы")
        await message.answer("Пожалуйста, выберите свою роль", reply_markup=choose_role_kb)
        await MainStates.wait_for_role.set()
        return

    cur_state = await state.get_state()
    print(cur_state)
    print(await state.get_data())
    await message.reply("Не могу определить что мне нужно делать")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)