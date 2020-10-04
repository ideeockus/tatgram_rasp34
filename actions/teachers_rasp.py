from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage.configuration import feedback_tg_id
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError
from bot_storage.roles_base import get_role
from aiogram.utils.markdown import bold, code, italic, text, escape_md
from aiogram.types import ParseMode
from bot_storage.Keyboards import teacher_kb, rasp_by_days_kb, cancel_kb
from bot_storage.Keyboards import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot_storage.rasp_base import get_all_teachers, get_teacher_lessons_for_week_day

# cancel_feedback_kb = ReplyKeyboardMarkup(resize_keyboard=True)
# cancel_feedback_button = KeyboardButton("Отмена")
# cancel_feedback_kb.add(cancel_feedback_button)


class TeacherRaspReqStates(StatesGroup):
    waiting_for_action = State()
    waiting_for_teacher_name = State()
    end_state = State()


# class FeedbackKeyboards:
#     end_keyboard = cancel_feedback_kb


def md_shielding(md_text: str) -> str:
    return md_text.replace("*", "\\*").replace("`", "\\`").replace("_", "\\_")


# async def make_teacher_rasp_req(end_state: State, end_keyboard: types.ReplyKeyboardMarkup):
#     await TeacherRaspReqStates.waiting_for_action.set()
#     FeedbackKeyboards.end_keyboard = end_keyboard


async def make_teacher_rasp_request(message: types.Message, teacher_name=None):
    await TeacherRaspReqStates.waiting_for_action.set()
    if teacher_name is None:
        await message.answer("Для кого вы хотите узнать расписание?")
        await TeacherRaspReqStates.waiting_for_teacher_name.set()
    else:
        await message.answer("Выберите день недели", reply_markup=rasp_by_days_kb)


@dp.message_handler(state=TeacherRaspReqStates.waiting_for_teacher_name, content_types=types.ContentType.TEXT)
async def get_teacher_name(message: types.Message, state: FSMContext):
    teacher_name = message.text.lower()
    print("запрошено раписание учителя", teacher_name)
    # teachers_set = get_all_teachers()
    teacher_name = message.text.lower()
    teachers_set = set(map(str.lower, get_all_teachers()))
    if teacher_name in teachers_set:
        user_data = await state.get_data()
        user_data.update(teacher_name=teacher_name.title())
        await message.answer("Хорошо, выберите день недели", reply_markup=rasp_by_days_kb)
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
        elif len(teachers_choose_list) >= 1:
            await message.answer("Выберите учителя из списка", reply_markup=teachers_choose_list_kb)
            return
    await TeacherRaspReqStates.waiting_for_action.set()


@dp.callback_query_handler(lambda cq: cq.data not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
                           state=TeacherRaspReqStates.waiting_for_teacher_name)
async def teacher_full_name_inline(callback_query: types.CallbackQuery, state: FSMContext):
    teacher_name = callback_query.data
    # await state.update_data(teacher_name=teacher_name)
    print("выбор", teacher_name, "с инлайн клавиатуры")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Хорошо, выберите день недели", reply_markup=rasp_by_days_kb)
    await state.update_data(teacher_name=teacher_name.title())
    await TeacherRaspReqStates.waiting_for_action.set()
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda cq: cq.data in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
                           state=TeacherRaspReqStates.waiting_for_action)
async def rasp_by_day_inline_handler(callback_query: types.CallbackQuery, state: FSMContext):
    # print("пришел callback на расписание по дням")
    callback_data_text = {'monday': 0, 'tuesday': 1, 'wednesday': 2,
                          'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
    callback_data = callback_query.data
    user_data = await state.get_data()
    teacher_name = user_data['teacher_name']
    print("запрос расписания для", teacher_name, "на", callback_data)
    lessons = "Нет уроков"
    if teacher_name is not None:
        # print(callback_data)
        lessons = get_teacher_lessons_for_week_day(teacher_name, callback_data_text[callback_data])
        await TeacherRaspReqStates.waiting_for_action.set()
    else:
        await TeacherRaspReqStates.waiting_for_teacher_name.set()
        await bot.send_message(chat_id=callback_query.message.chat.id, text="для кого вы хотите узнать распиание?")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, lessons, parse_mode=ParseMode.MARKDOWN)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)







