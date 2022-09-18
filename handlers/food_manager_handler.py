from aiogram import types

from actions import view_food_orders, take_food_orders
from bot import dp
from bot_storage.Keyboards import cancel_kb
from bot_storage.UserStates import FoodManagerStates


@dp.message_handler(lambda m: m.text == "Посмотреть заказы", state=FoodManagerStates.waiting_for_action)
async def view_orders(message: types.Message):
    await view_food_orders.make_view_food_orders(message)


@dp.message_handler(lambda m: m.text == "Собрать заказы", state=FoodManagerStates.waiting_for_action)
async def take_orders(message: types.Message):
    await take_food_orders.make_take_food_orders(message)
    # await make_food_order.make_food_order(message, pupil_food_category)
