from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage import FoodMenuPupilCategory
from bot_storage.configuration import feedback_tg_id
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, UserDeactivated, TelegramAPIError
from aiogram.utils.markdown import bold, code, italic, text, escape_md
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from bot_storage.accounts_base import get_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard
from bot_storage.food_menu import get_food_items_by_category, get_food_item_by_id
from utils.scheduled_tasks import set_message_timeout_and_reset_state


class FoodOrderSteps(StatesGroup):
    waiting_for_order = State()
    waiting_inline_food_choose = State()


async def make_food_order(message: types.Message, pupil_food_category: FoodMenuPupilCategory):
    await FoodOrderSteps.waiting_for_order.set()

    available_items = get_food_items_by_category(pupil_food_category)

    # формирование инлайн клавиатуры
    choose_list_kb = InlineKeyboardMarkup(row_width=1)
    for food_item in available_items:
        button = InlineKeyboardButton(f"{food_item.food_name} - {food_item.price}₽", callback_data=str(food_item.id))
        choose_list_kb.insert(button)

    # отправка
    order_kb_message = await message.answer("Выберите блюдо списка", reply_markup=choose_list_kb)
    set_message_timeout_and_reset_state(message.from_user.id, order_kb_message.chat.id, order_kb_message.message_id)


@dp.callback_query_handler(state=FoodOrderSteps.waiting_for_order)
async def order_choose_inline(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

    food_item_id = int(callback_query.data)
    print("выбор", food_item_id, "с инлайн клавиатуры заказа еды")
    # TODO: добавить заказ в БД

    user_id = callback_query.from_user.id
    user_role = get_role(user_id)
    user_waiting_for_action_state = get_role_waiting_for_action_state(user_role)
    user_keyboard = get_role_keyboard(user_role)

    choosen_food_item = get_food_item_by_id(food_item_id)

    order_msg = text(escape_md(f"Отлично! Вы выбрали:\n\n"),
                     bold(f"{choosen_food_item.food_name}\n"),
                     escape_md(f"{choosen_food_item.price}₽\n\n"),
                     italic(f"{choosen_food_item.description}\n"),
                     )

    await user_waiting_for_action_state.set()
    await callback_query.message.answer(order_msg, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=user_keyboard)
