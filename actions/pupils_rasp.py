from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from aiogram.types import ParseMode
from bot_storage.Keyboards import rasp_by_days_kb, cancel_kb
from bot_storage.rasp_base import get_all_classes, get_lessons_for_week_day, get_week_rasp_by_role
from bot_storage.UserStates import PupilStates
from utils.abg import md_shielding, md_format
from bot_storage.roles_base import get_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard
from utils.scheduled_tasks import set_message_timeout_and_reset_state


class PupilsRaspReqStates(StatesGroup):
    # waiting_for_action = State()
    waiting_for_inline_week_day_chose = State()
    waiting_for_class_name = State()


# action_vars = {'keyboard': cancel_kb}


# def md_shielding(md_text: str) -> str:
#     return md_text.replace("*", "\\*").replace("`", "\\`").replace("_", "\\_")


async def make_pupil_rasp_request(message: types.Message, class_name=None):
    # TODO: приделать сюда FSMContext и убрать дубликацию кода
    print(f"action make_pupil_rasp_request, class_name = {class_name}")
    # action_vars['keyboard'] = role_keyboard
    # PupilsRaspReqStates.waiting_for_action = PupilStates.waiting_for_action
    # PupilsRaspReqStates.waiting_for_action = waiting_for_action_state
    if class_name is None:
        await message.answer("Для какого класса вы хотите узнать расписание?", reply_markup=cancel_kb)
        await PupilsRaspReqStates.waiting_for_class_name.set()
    else:
        await message.answer(f"Запрос расписания для класса {class_name}",
                             reply_markup=get_role_keyboard(get_role(message.from_user.id)))
        kb_msg = await message.answer("Выберите день недели", reply_markup=rasp_by_days_kb)
        set_message_timeout_and_reset_state(message.from_user.id, kb_msg.chat.id, kb_msg.message_id)
        await PupilsRaspReqStates.waiting_for_inline_week_day_chose.set()


# @dp.message_handler(lambda m: m.text == "Отмена", state=PupilsRaspReqStates, content_types=types.ContentType.TEXT)
# async def cancel_rasp_update(message: types.Message):
#     user_id = message.from_user.id
#     user_role = get_role(user_id)
#     await get_role_waiting_for_action_state(user_role).set()
#     await message.reply("Отменено", reply_markup=get_role_keyboard(user_role))
    # await PupilsRaspReqStates.waiting_for_action.set()
    # await message.reply("Отменено", reply_markup=action_vars['keyboard'])


@dp.message_handler(state=PupilsRaspReqStates.waiting_for_class_name, content_types=types.ContentType.TEXT)
async def get_class_name(message: types.Message, state: FSMContext):
    class_name = message.text.replace(" ", "").lower()
    print("запрошено раписание класса", class_name)
    classes_set = set(map(str.lower, get_all_classes()))
    if class_name in classes_set:
        await state.update_data(class_name=class_name)
        await message.answer(f"Запрос расписания для класса {class_name}",
                             reply_markup=get_role_keyboard(get_role(message.from_user.id)))
        kb_msg = await message.answer("Выберите день недели", reply_markup=rasp_by_days_kb)
        set_message_timeout_and_reset_state(message.from_user.id, kb_msg.chat.id, kb_msg.message_id)

        await PupilsRaspReqStates.waiting_for_inline_week_day_chose.set()
    else:
        await message.answer("Не могу найти такого класса, введите еще раз")


@dp.callback_query_handler(lambda cq: cq.data in ["monday", "tuesday", "wednesday",
                                                  "thursday", "friday", "saturday", "week"],
                           state=PupilsRaspReqStates.waiting_for_inline_week_day_chose)
async def rasp_by_day_inline_handler(callback_query: types.CallbackQuery, state: FSMContext):
    print(f"callback_data: {callback_query.data}")
    print(f"state_data: {await state.get_data()}")
    user_id = callback_query.from_user.id
    user_role = get_role(user_id)
    user_waiting_for_action_state = get_role_waiting_for_action_state(user_role)
    print(f"next state is {user_waiting_for_action_state}")
    print(f"current state is {await state.get_state()}")
    callback_data_text = {'monday': 0, 'tuesday': 1, 'wednesday': 2,
                          'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    week_day = callback_query.data
    user_data = await state.get_data()
    class_name = user_data['class_name']
    print("запрос расписания для", class_name, "на", week_day)
    if class_name is not None:
        lessons = None
        if week_day == "week":  # если на всю неделю
            lessons = get_week_rasp_by_role("pupil", class_name)
        else:
            lessons = get_lessons_for_week_day(class_name, callback_data_text[week_day])
        # lessons = md_format(lessons)
        # print(lessons)
        await bot.send_message(user_id, lessons,
                               parse_mode=ParseMode.MARKDOWN, reply_markup=get_role_keyboard(user_role))
        await user_waiting_for_action_state.set()
    else:
        await PupilsRaspReqStates.waiting_for_class_name.set()
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Для кого вы хотите узнать распиание?")

