from typing import Set, Optional, List
from sqlalchemy.orm import sessionmaker
from bot_storage import bot_stats
from bot_storage import Roles, Account, engine
from datetime import datetime

import utils

# TODO rename to accounts_db
# user_id | username | firstname | lastname | role | sch_identifier | auth_key | supervisor_user_id | reg date
# auth_key - ключ авторизации для внутренних сервисов. При генерации нового ключа старый затирается во избежание утечек

DbSession = sessionmaker(bind=engine, expire_on_commit=False)


def gen_uniq_auth_key() -> str:
    generated_auth_key = utils.gen_random_string()

    accounts_db_session = DbSession()
    key_is_unique = accounts_db_session.query(Account).filter(Account.auth_key == generated_auth_key).first() is None
    accounts_db_session.close()

    return generated_auth_key if key_is_unique else gen_uniq_auth_key()


def check_account_existence(user_id: int) -> bool:
    accounts_db_session = DbSession()
    account_exists = accounts_db_session.query(Account).filter(Account.user_id == user_id).first() is not None
    accounts_db_session.close()

    return account_exists


def unlink_account(user_id: int):
    """
    Отсоеденить аккаунт бота от аккаунта telegram
    """
    accounts_db_session = DbSession()
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    user.user_id = None

    # список контролируемых пользователей
    # controlled_users: List[Account] = accounts_db_session.query(Account).filter(user in Account.supervisor_user_ids).all()
    # print("controlled_users type", controlled_users)
    # for controlled_user in controlled_users:
    #     controlled_user.supervisor_user_ids.remove(user)
    # user.username = None
    # user.registration_date = None
    accounts_db_session.commit()
    accounts_db_session.close()


def refresh_user_auth_key(user_id: int):
    """
    Обновить ключ авторизации пользователя
    """
    accounts_db_session = DbSession()
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    user.auth_key = gen_uniq_auth_key()
    accounts_db_session.commit()
    accounts_db_session.close()


def reg_user(user_id: Optional[int], role: Roles, username: Optional[str],
             firstname: Optional[str], lastname: Optional[str], sch_identifier: str = None) -> Optional[Account]:
    accounts_db_session = DbSession()
    # print(f"Регистрация пользователя @{username}[{user_id}] как {role}")
    print(f"Регистрация пользователя {utils.get_account_human_readable(firstname, lastname, username, user_id)}"
          f" как {role}")
    # user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()

    new_user_account = Account(
        user_id=user_id,
        username=username,
        firstname=firstname,
        lastname=lastname,
        role=role,
        sch_identifier=sch_identifier,
        auth_key=gen_uniq_auth_key(),
        registration_date=datetime.now() if user_id else None  # это поле не заполняется пока нет tg_id юзера
    )
    accounts_db_session.add(new_user_account)
    accounts_db_session.commit()
    accounts_db_session.close()

    bot_stats.new_user(role.name)
    return new_user_account


# def add_new_account(user_id: str, username: str, firstname: str, lastname: str,
#                     role: Roles, sch_identifier: str, registration_date: datetime) -> Optional[Account]:
#     accounts_db_session = DbSession()
#     new_user_account = Account(
#         user_id=user_id,
#         username=username,
#         firstname=firstname,
#         lastname=lastname,
#         role=role,
#         sch_identifier=sch_identifier,
#         auth_key=gen_uniq_auth_key(),
#         registration_date=registration_date
#     )
#     accounts_db_session.add(new_user_account)
#     accounts_db_session.commit()
#     accounts_db_session.close()
#
#     bot_stats.new_user(role.name)
#     return new_user_account


def authorize_user(auth_key: str, user_id: int, username: str) -> Optional[Account]:
    """
    Авторизовать пользователя
    @return реузльтат авторизации
    """
    accounts_db_session = DbSession()
    print(f"Авторизация пользователя {user_id} ...")

    user: Account = accounts_db_session.query(Account).filter(Account.auth_key == auth_key.strip()).scalar()
    if (user is None) or (user.user_id is not None and user.user_id != user_id):
        return None

    user.user_id = user_id
    user.username = username
    user.registration_date = datetime.now()
    user_role = user.role

    accounts_db_session.commit()
    accounts_db_session.close()

    bot_stats.new_user(user_role.name)  ## remove later
    return user


def set_user_supervisor(user_id: int, supervisor_user_id: int) -> bool:
    """
    Add supervisor to supervisor_ids of account
    """
    accounts_db_session = DbSession()
    print(f"Установка {supervisor_user_id} как родитель для {user_id}")

    supervisor_user: Account = accounts_db_session.query(Account).filter(Account.user_id == supervisor_user_id).scalar()
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    if user is None:
        return False

    print("supervisor ids", user.supervisor_user_ids)
    user.supervisor_user_ids.append(supervisor_user)

    accounts_db_session.commit()
    accounts_db_session.close()
    return True


def get_role(user_id: int) -> Optional[Roles]:
    accounts_db_session = DbSession()

    # user_id = user_id
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    if user is None:
        return None
    accounts_db_session.close()
    return user.role


def get_sch_identifier(user_id: int) -> str:
    accounts_db_session = DbSession()

    # user_id = str(user_id)
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    user_identifier = user.sch_identifier

    accounts_db_session.close()
    return user_identifier


def get_user_fullname(user_id: int):
    accounts_db_session = DbSession()

    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    user_fullname = user.firstname + " " + user.lastname

    accounts_db_session.close()
    return user_fullname


def get_users_set(role: Roles = None) -> Set[Account]:
    """
    returns ids of users by role, or all available ids if role parameter not specified
    """
    accounts_db_session = DbSession()

    user_id_set: Set[int] = set()
    users = accounts_db_session.query(Account).all() if role is None \
        else accounts_db_session.query(Account).filter(Account.role == role.name).all()

    for user in users:
        if user.user_id is None:
            continue
        user_id_set.add(user.user_id)

    accounts_db_session.close()
    return user_id_set


def get_user_by_auth_key(auth_key: str) -> Optional[Account]:
    accounts_db_session = DbSession()

    user = accounts_db_session.query(Account).filter(Account.auth_key == auth_key).scalar()
    accounts_db_session.close()

    return user


def upload_new_accounts_from_csv(accounts_csv) -> int:
    accounts_list = [csv_row.split(",") for csv_row in accounts_csv.split("\r\n")]
    registered_accounts_amount = 0
    for csv_row in accounts_list:
        if len(csv_row) != 4:
            continue
        firstname = csv_row[0]
        lastname = csv_row[1]
        role = csv_row[2]
        sch_identifier = csv_row[3] if csv_row[3].strip() else None
        reg_user(None, Roles(role), None, firstname, lastname, sch_identifier)
        registered_accounts_amount += 1

    return registered_accounts_amount
