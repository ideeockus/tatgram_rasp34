from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from aiogram.types import ParseMode
from bot_storage.Keyboards import rasp_by_days_kb, cancel_kb
from bot_storage.rasp_base import get_all_classes, get_lessons_for_week_day


class PupilsRaspReqStates(StatesGroup):
    waiting_for_action = State()
    waiting_for_inline_week_day_chose = State()
    waiting_for_class_name = State()


def md_shielding(md_text: str) -> str:
    return md_text.replace("*", "\\*").replace("`", "\\`").replace("_", "\\_")


async def make_pupil_rasp_request(message: types.Message, waiting_for_action_state, class_name=None):
    print(f"action make_pupil_rasp_request, class_name = {class_name}")
    PupilsRaspReqStates.waiting_for_action = waiting_for_action_state
    if class_name is None:
        await message.answer("Для какого класса вы хотите узнать расписание?")
        await PupilsRaspReqStates.waiting_for_class_name.set()
    else:
        await message.answer("Выберите день недели", reply_markup=rasp_by_days_kb)
        await PupilsRaspReqStates.waiting_for_inline_week_day_chose.set()


@dp.message_handler(state=PupilsRaspReqStates.waiting_for_class_name, content_types=types.ContentType.TEXT)
async def get_class_name(message: types.Message, state: FSMContext):
    class_name = message.text.lower()
    print("запрошено раписание класса", class_name)
    classes_set = set(map(str.lower, get_all_classes()))
    if class_name in classes_set:
        await state.update_data(class_name=class_name)
        await message.answer("Хорошо, выберите день недели", reply_markup=rasp_by_days_kb)
        await PupilsRaspReqStates.waiting_for_inline_week_day_chose.set()
    else:
        await message.answer("Не могу найти такого класса, введите еще раз")


@dp.callback_query_handler(lambda cq: cq.data in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
                           state=PupilsRaspReqStates.waiting_for_inline_week_day_chose)
async def rasp_by_day_inline_handler(callback_query: types.CallbackQuery, state: FSMContext):
    print(f"callback_data: {callback_query.data}")
    print(f"state_data: {await state.get_data()}")
    print(f"PupilsRaspReqStates.waiting_for_action is {PupilsRaspReqStates.waiting_for_action}")
    print(f"Current state is {await state.get_state()}")
    callback_data_text = {'monday': 0, 'tuesday': 1, 'wednesday': 2,
                          'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    week_day = callback_query.data
    user_data = await state.get_data()
    class_name = user_data['class_name']
    print("запрос расписания для", class_name, "на", week_day)
    if class_name is not None:
        lessons = get_lessons_for_week_day(class_name, callback_data_text[week_day])
        await bot.send_message(callback_query.from_user.id, lessons, parse_mode=ParseMode.MARKDOWN)
        await PupilsRaspReqStates.waiting_for_action.set()
    else:
        await PupilsRaspReqStates.waiting_for_class_name.set()
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Для кого вы хотите узнать распиание?")







