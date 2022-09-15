from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage.configuration import feedback_tg_id
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError
from aiogram.utils.markdown import bold, code, italic, text, escape_md
from aiogram.types import ParseMode
from bot_storage.accounts_base import get_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard


class FeedbackSteps(StatesGroup):
    waiting_for_feedback_text = State()


async def make_feedback():
    await FeedbackSteps.waiting_for_feedback_text.set()


@dp.message_handler(state=FeedbackSteps.waiting_for_feedback_text, content_types=types.ContentType.TEXT)
async def feedback_text_gotten(message: types.Message, state: FSMContext):
    print("Feedback action")
    feedback_text = message.text
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    user_role = get_role(user_id)
    user_waiting_for_action_state = get_role_waiting_for_action_state(user_role)
    user_keyboard = get_role_keyboard(user_role)
    feedback_msg = text(bold(f"Сообщение от @{user_username} id: {user_id}\n"),
                        code(f"{user_full_name}\n"),
                        italic(f"роль: {user_role.value}\n\n"),  # не добавлять в роль _ (будет конфликт с italic)
                        # md_shielding(str(feedback_text))
                        # escape_md(str(feedback_text))
                        escape_md(feedback_text)
                        )
    print(feedback_msg)
    try:
        await bot.send_message(feedback_tg_id, feedback_msg, parse_mode=ParseMode.MARKDOWN_V2)
    except (BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError) as e:
        print("Отправка фидбека не удалась")
        print(e)
        await message.answer("К сожалению отправка фидбека не удалась", reply_markup=user_keyboard)
    else:
        await message.answer("Сообщение отправлено", reply_markup=user_keyboard)
    await user_waiting_for_action_state.set()
