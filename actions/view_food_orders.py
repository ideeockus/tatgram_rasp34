from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp, bot
from bot_storage.accounts_base import get_role
from bot_storage.UserStates import get_role_waiting_for_action_state
from bot_storage.Keyboards import get_role_keyboard
from bot_storage.food_menu import upload_food_menu_from_csv
from bot_storage.food_menu.orders import get_food_orders_info
from utils import send_direct_message

import io
import threading


class ViewFoodOrdersSteps(StatesGroup):
    waiting_for_csv = State()


async def make_view_food_orders(message: types.Message):
    # await ViewFoodOrdersSteps.waiting_for_csv.set()
    #
    # user_id = message.from_user.id
    # user_role = get_role(user_id)
    # user_keyboard = get_role_keyboard(user_role)
    #
    # await get_role_waiting_for_action_state(user_role).set()
    # await message.answer(f"Готово", reply_markup=user_keyboard)
    orders = get_food_orders_info()
    print(f"orders: {orders}")
    await message.answer(str(orders))