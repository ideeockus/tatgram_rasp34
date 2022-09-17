from typing import Optional, List

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from bot_storage import FoodOrder, engine

DbSession = sessionmaker(bind=engine, expire_on_commit=False)


def add_food_order(food_item_id: int, user_id: int) -> Optional[FoodOrder]:
    food_orders_db_session = DbSession()
    print(f"Выбор еды: {user_id} выбрал пункт {food_item_id}")

    new_food_order = FoodOrder(
        food_item_id=food_item_id,
        user_id=user_id
    )

    food_orders_db_session.add(new_food_order)
    food_orders_db_session.commit()
    food_orders_db_session.close()

    return new_food_order


def get_food_orders_info() -> List:
    food_orders_db_session = DbSession()

    wtf = food_orders_db_session.query(
        FoodOrder.food_item_id, func.count(FoodOrder.user_id)
    ).group_by(FoodOrder.food_item_id).all()

    # [(2, 1), (4, 1)]

    return wtf


def clear_food_orders() -> bool:
    food_orders_db_session = DbSession()
    print(f"Очистка заказов")

    for order in food_orders_db_session.query(FoodOrder).all():
        food_orders_db_session.delete(order)

    food_orders_db_session.commit()
    return True
