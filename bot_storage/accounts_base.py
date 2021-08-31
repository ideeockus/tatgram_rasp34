from typing import Set, Optional
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


def check_account_existence(user_id: str) -> bool:
    accounts_db_session = DbSession()
    account_exists = accounts_db_session.query(Account).filter(Account.user_id == user_id).first() is not None
    accounts_db_session.close()

    return account_exists


def unlink_account(user_id: str):
    """
    Отсоеденить аккаунт бота от аккаунта telegram
    """
    accounts_db_session = DbSession()
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    user.user_id = None
    # user.username = None
    # user.registration_date = None
    accounts_db_session.commit()
    accounts_db_session.close()


def refresh_user_auth_key(user_id: str):
    """
    Обновить ключ авторизации пользователя
    """
    accounts_db_session = DbSession()
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    user.auth_key = gen_uniq_auth_key()
    accounts_db_session.commit()
    accounts_db_session.close()


def reg_user(user_id: str, role: Roles, username: str,
             firstname: str, lastname: str, sch_identifier: str = None) -> Optional[Account]:
    accounts_db_session = DbSession()
    print(f"Регистрация пользователя {username}[{user_id}] как {role}")
    # user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()

    new_user_account = Account(
        user_id=user_id,
        username=username,
        firstname=firstname,
        lastname=lastname,
        role=role.name,
        sch_identifier=sch_identifier,
        auth_key=gen_uniq_auth_key(),
        registration_date=datetime.now()
    )
    accounts_db_session.add(new_user_account)
    accounts_db_session.commit()
    accounts_db_session.close()

    bot_stats.new_user(role.name)
    return new_user_account


def authorize_user(auth_key: str, user_id: str, username: str) -> Optional[Account]:
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


def set_user_supervisor(user_id: str, supervisor_user_id: str) -> bool:
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



# def reg_supervisor(controlled_auth_key: str, user_id: str, role: Roles, username: str,
#                    firstname: str, lastname: str) -> Optional[Account]:
#     """
#     Reg supervisor
#     """
#     accounts_db_session = DbSession()
#     print(f"Регистрация пользователя {username}[{user_id}] как {role}")
#
#     # user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
#     # if user is not None:
#     #     print(f"Пользователь {username}[{user_id}] уже зарегестрирован как {user.role}. Аккаунт будет удален")
#     #     accounts_db_session.delete(user)
#     #
#     # new_user_account = Account(
#     #     user_id=user_id,
#     #     username=username,
#     #     firstname=firstname,
#     #     lastname=lastname,
#     #     role=role.name,
#     #     registration_date=datetime.now()
#     # )
#     # accounts_db_session.add(new_user_account)
#
#     controlled_user = accounts_db_session.query(Account).filter(Account.auth_key == controlled_auth_key).scalar()
#     if controlled_user is None:
#
#     accounts_db_session.commit()
#     accounts_db_session.close()
#
#     bot_stats.new_user(role.name)
#     return new_user_account


# def reg_class(user_id, class_name):
#     print("__user_base:", f"регистрация {user_id} в классе {class_name}")
#     user_id = str(user_id)
#     user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
#     if user_record is None:
#         print(f"Пользователь {user_id} не может быть зарегестрирова в классе, т.к. его нет в базе")
#         return
#     user_record.identifier = class_name
#     roles_db_session.commit()


# вроде это теперь не нужно
# def set_identifier(user_id, identifier):
#     roles_db_session = DbSession()
#
#     print(f"{user_id} теперь зарегестрирован как {identifier}")
#     user_id = str(user_id)
#     user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
#     if user_record is None:
#         print(f"Пользователь {user_id} не может быть зарегестрирован, т.к. его нет в базе")
#         return
#     user_record.identifier = identifier
#     roles_db_session.commit()
#     roles_db_session.close()


# def set_class_name(user_id, class_name):
#     roles_db_session = DbSession()
#
#     print(f"{user_id} зарегестрирован в классе {class_name}")
#     user_id = str(user_id)
#     user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
#     if user_record is None:
#         print(f"Пользователь {user_id} не может быть зарегестрирован, т.к. его нет в базе")
#         return
#     user_record.class_name = class_name
#     roles_db_session.commit()
#     roles_db_session.close()


# def set_teacher_name(user_id, teacher_name):
#     roles_db_session = DbSession()
#
#     print(f"{user_id} зарегестрирован как {teacher_name}")
#     user_id = str(user_id)
#     user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
#     if user_record is None:
#         print(f"Пользователь {user_id} не может быть зарегестрирован, т.к. его нет в базе")
#         return
#     user_record.teacher_name = teacher_name
#     roles_db_session.commit()
#     roles_db_session.close()


# def del_user_role(user_id):
#     roles_db_session = DbSession()
#
#     user_id = str(user_id)
#     user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id)
#     for user_record in user_records:
#         roles_db_session.delete(user_record)
#     roles_db_session.commit()
#     roles_db_session.close()


# def change_role(user_id, new_role):
#     roles_db_session = DbSession()
#
#     print(f"Смена роли пользователя {user_id} на {new_role}")
#     user_id = str(user_id)
#     # del_user_role(user_id)
#     user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
#     if user_record is None:
#         print("__user_base:", f"Пользователя {user_id} нет в базе")
#     bot_stats.edit_stat(get_role(user_id), -1)
#     user_record.role = new_role
#     # for user_record in user_records:
#     #     roles_db_session.delete(user_record)
#     # role_db_record = RoleRecord(user_id=user_id, role=new_role)
#     # roles_db_session.add(role_db_record)
#     roles_db_session.commit()
#     roles_db_session.close()
#
#     bot_stats.edit_stat(new_role, 1)


def get_role(user_id: str) -> Optional[Roles]:
    accounts_db_session = DbSession()

    # user_id = user_id
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    if user is None:
        return None
    # user_role = user_records.role
    accounts_db_session.close()
    # user_roles = []
    #
    # for user_record in user_records:
    #     # print(f"У пользователя {user_record.user_id} записана роль {user_record.role}")
    #     user_roles.append(user_record.role)
    # if len(user_roles) == 0:
    #     return None
    # user_role = user_roles[0]
    return user.role


def get_sch_identifier(user_id: str) -> str:
    accounts_db_session = DbSession()

    # user_id = str(user_id)
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    print(type(user))
    user_identifier = user.sch_identifier

    accounts_db_session.close()
    return user_identifier


# def get_class_name(user_id):
#     roles_db_session = DbSession()
#
#     user_id = str(user_id)
#     user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
#     class_name = user_records.class_name
#
#     roles_db_session.close()
#     return class_name
#
#
# def get_teacher_name(user_id):
#     roles_db_session = DbSession()
#
#     user_id = str(user_id)
#     user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
#     teacher_name = user_records.teacher_name
#
#     roles_db_session.close()
#     return teacher_name

def get_user_fullname(user_id: str):
    accounts_db_session = DbSession()

    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    user_fullname = user.firstname + " " + user.lastname

    accounts_db_session.close()
    return user_fullname


# refactored
# def get_all_users_ids():
#     accounts_db_session = DbSession()
#
#     user_id_set = set()
#     users: List[Account] = accounts_db_session.query(Account).all()
#     for user in users:
#         user_id_set.add(user.user_id)
#
#     accounts_db_session.close()
#     return user_id_set
#
#
# def get_users_by_role(role: Roles):
#     accounts_db_session = DbSession()
#
#     user_id_set = set()
#     users = accounts_db_session.query(Account).filter(Account.role == role.name).all()
#     for user_record in users:
#         user_id_set.add(user_record.user_id)
#
#     accounts_db_session.close()
#     return user_id_set


def get_users_set(role: Roles = None) -> Set[Account]:
    """
    returns ids of users by role, or all available ids if role parameter not specified
    """
    accounts_db_session = DbSession()

    user_id_set = set()
    users = accounts_db_session.query(Account).all() if role is None \
        else accounts_db_session.query(Account).filter(Account.role == role.name).all()

    for user in users:
        user_id_set.add(user.user_id)

    accounts_db_session.close()
    return user_id_set

def get_user_by_auth_key(auth_key: str) -> Optional[Account]:
    accounts_db_session = DbSession()

    user = accounts_db_session.query(Account).filter(Account.auth_key == auth_key).scalar()
    accounts_db_session.close()

    return user
