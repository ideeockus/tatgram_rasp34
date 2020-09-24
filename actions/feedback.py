from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage.configuration import feedback_tg_id
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError
from bot_storage.roles_base import get_role
from aiogram.utils.markdown import bold, code, italic, text
from aiogram.types import ParseMode


class FeedbackSteps(StatesGroup):
    waiting_for_feedback_text = State()
    end_state = State()


async def make_feedback(end_state: State):
    FeedbackSteps.end_state = end_state
    await FeedbackSteps.waiting_for_feedback_text.set()


@dp.message_handler(state=FeedbackSteps.waiting_for_feedback_text, content_types=types.ContentType.TEXT)
async def feedback_text_gotten(message: types.Message, state: FSMContext):
    feedback_text = message.text
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    user_role = get_role(user_id)
    print(f"feedback from {user_role} {user_id} ({user_full_name}): {feedback_text}")
    # feedback_msg = f"Сообщение от @{user_username}\n" \
    #                f"{user_full_name}\n" \
    #                f"роль: {user_role}\n\n{feedback_text}"
    feedback_msg = text(bold(f"Сообщение от @{user_username}\n"),
                        italic(f"{user_full_name}\n"),
                        italic(f"роль: {user_role}\n\n"),
                        str(feedback_text))
    try:
        await bot.send_message(feedback_tg_id, feedback_msg, parse_mode=ParseMode.MARKDOWN)
    except (BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError):
        print("Отправка фидбека не удалась")
        await message.answer("К сожалению отправка фидбека не удалась")
    else:
        await message.answer("Сообщение отправлено")
    await FeedbackSteps.end_state.set()





