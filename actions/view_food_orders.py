from itertools import groupby
from typing import cast

from aiogram import types
from bot_storage.food_menu import get_food_item_by_id
from bot_storage.food_menu.orders import get_food_orders_info, FoodItemAmount


# class ViewFoodOrdersSteps(StatesGroup):
#     waiting_for_csv = State()


async def make_view_food_orders(message: types.Message):
    orders = get_food_orders_info()
    if not orders:
        await message.answer("Заказов нет!")
        return

    orders_by_class = groupby(orders, key=lambda order: cast(FoodItemAmount, order).class_identifier)  # its iterator
    msg = "Список заказов по классам 🍽\n\n"

    for cl, orders in orders_by_class:
        class_orders_list = [f"{get_food_item_by_id(o.food_item_id).food_name} - {o.count} шт" for o in orders]
        msg += f"Заказы по {cl}:\n" + "\n".join(class_orders_list) + "\n\n"

    await message.answer(msg)
