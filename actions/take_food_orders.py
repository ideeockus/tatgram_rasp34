from aiogram import types

from actions import view_food_orders
from bot_storage.food_menu.orders import clear_food_orders


async def make_take_food_orders(message: types.Message):
    """Получить данные о заказаз и очистить список заказов"""
    await view_food_orders.make_view_food_orders(message)

    clear_food_orders()
    await message.answer("Список заказов очищен!")
