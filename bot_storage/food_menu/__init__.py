from typing import Optional, List

from sqlalchemy.orm import sessionmaker

from bot_storage import FoodMenuPupilCategory, FoodMenuItem, engine

DbSession = sessionmaker(bind=engine, expire_on_commit=False)


def add_food_item(category: FoodMenuPupilCategory, name: str,
                  price: float, description: str) -> Optional[FoodMenuItem]:
    food_menu_db_session = DbSession()
    print(f"Занесение в список меню: {category} - {name} - {price} - {description}")

    new_food_item = FoodMenuItem(
        category=category,
        food_name=name,
        price=price,
        description=description
    )

    food_menu_db_session.add(new_food_item)
    food_menu_db_session.commit()
    food_menu_db_session.close()

    return new_food_item


def get_food_items_by_category(category: FoodMenuPupilCategory) -> List[FoodMenuItem]:
    food_menu_db_session = DbSession()
    print(f"Получение списка блюд для {category}")

    items = food_menu_db_session.query(FoodMenuItem).filter(FoodMenuItem.category == category).all()

    return items


def get_food_item_by_id(food_item_id: int) -> Optional[FoodMenuItem]:
    food_menu_db_session = DbSession()

    item = food_menu_db_session.query(FoodMenuItem).filter(FoodMenuItem.id == food_item_id).scalar()

    return item


def clear_menu() -> bool:
    food_menu_db_session = DbSession()
    print(f"Очистка меню")

    for lsn in food_menu_db_session.query(FoodMenuItem).all():
        food_menu_db_session.delete(lsn)

    food_menu_db_session.commit()
    return True


def upload_food_menu_from_csv(accounts_csv) -> int:
    food_menu_item_list = [csv_row.split(",") for csv_row in accounts_csv.split("\r\n")]
    items_amount = 0

    clear_menu()  # # очитска предыдущей таблицы

    for csv_row in food_menu_item_list:
        if len(csv_row) != 4:
            continue
        category = FoodMenuPupilCategory(csv_row[0])
        food_name = csv_row[1]
        price = float(csv_row[2])
        description = csv_row[3]
        add_food_item(category, food_name, price, description)
        items_amount += 1

    return items_amount
