from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy import func, update
from sqlalchemy.orm import sessionmaker

from bot_storage import FoodOrder, engine, Account

DbSession = sessionmaker(bind=engine, expire_on_commit=False)


def add_food_order(food_item_id: int, user_id: int) -> Optional[FoodOrder]:
    food_orders_db_session = DbSession()
    print(f"Выбор еды: {user_id} выбрал пункт {food_item_id}")

    new_food_order = FoodOrder(
        food_item_id=food_item_id,
        user_id=user_id
    )

    order_exist = food_orders_db_session.query(FoodOrder.user_id).filter(
        FoodOrder.user_id == user_id).first() is not None

    if not order_exist:
        food_orders_db_session.add(new_food_order)
    else:
        stmt = update(FoodOrder).where(FoodOrder.user_id == user_id).values(
            food_item_id=food_item_id).execution_options(synchronize_session="fetch")
        result = food_orders_db_session.execute(stmt)

    food_orders_db_session.commit()
    food_orders_db_session.close()

    return new_food_order


@dataclass
class FoodItemAmount:
    food_item_id: int
    class_identifier: str
    count: int


def get_food_orders_info() -> List[FoodItemAmount]:
    food_orders_db_session = DbSession()

    food_items_amount_list = food_orders_db_session.query(
        FoodOrder.food_item_id, Account.sch_identifier, func.count(FoodOrder.user_id)
    ).join(Account).group_by(Account.sch_identifier, FoodOrder.food_item_id).all()

    food_items_amount_list = [FoodItemAmount(food_item_id=a[0],
                                             class_identifier=a[1],
                                             count=a[2]) for a in food_items_amount_list]
    return food_items_amount_list


def clear_food_orders() -> bool:
    food_orders_db_session = DbSession()
    print(f"Очистка заказов")

    for order in food_orders_db_session.query(FoodOrder).all():
        food_orders_db_session.delete(order)

    food_orders_db_session.commit()
    return True
