from aiogram import types
from bot_storage.food_menu import get_food_item_by_id
from bot_storage.food_menu.orders import get_food_orders_info


# class ViewFoodOrdersSteps(StatesGroup):
#     waiting_for_csv = State()


async def make_view_food_orders(message: types.Message):
    orders = get_food_orders_info()
    print(f"orders: {orders}")

    orders_list = [f"{get_food_item_by_id(o.food_item_id).food_name} - {o.count}" for o in orders]

    if orders_list:
        msg = "Заказы:\n" + \
              "\n".join(orders_list)
    else:
        await message.answer("Заказов нет!")
        return

    await message.answer(msg)
