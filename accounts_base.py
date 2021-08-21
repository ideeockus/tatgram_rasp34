from typing import List, Set, Optional

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bot_storage import bot_stats
from bot_storage.configuration import postgresql_db_url

from datetime import datetime

from libs import Roles, role_by_name

Base = declarative_base()


# TODO rename to accounts_db
# user_id | username | firstname | lastname | role | sch_identifier | auth_key | supervisor_user_id | reg date
# auth_key - ключ авторизации для внутренних сервисов. При генерации нового ключа старый затирается во избежание утечек


class Account(Base):
    __tablename__ = "accounts_db"
    # id = Column(Integer)
    user_id = Column(String, primary_key=True)
    username = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    role = Column(String)
    sch_identifier = Column(String)  # для школьников тут будет название класса
    auth_key = Column(String)
    supervisor_user_id = Column(String)
    # class_name = Column(String)  # имя класса
    # teacher_name = Column(String)  # имя учителя
    # user_fullname = Column(String)
    registration_date = Column(DateTime)


postgres_db = postgresql_db_url
engine = create_engine(postgres_db, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# roles_db_session = Session()


# def reg_new(user_id, role, username="", user_fullname=""):
#     roles_db_session = Session()
#     print(f"Пользователь {user_id} будет загерестрирован как {role}")
#
#     user_id = str(user_id)
#     user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == str(user_id)).scalar()
#     # user_roles = []
#     # for user_record in user_records:
#     #     user_roles.append(user_record.role)
#     if (user_record.role if user_record is not None else None) is not None:
#         print(f"у пользователя {user_id} уже есть роль", user_record.role)
#         return
#     role_db_record = RoleRecord(user_id=user_id, role=role, username=username,
#                                 user_fullname=user_fullname, registration_date=datetime.now())
#     roles_db_session.add(role_db_record)
#     roles_db_session.commit()
#     roles_db_session.close()
#
#     bot_stats.new_user(role)  # учет статистики

def authorize_user(auth_key: str, user_id: str, username: str = None) -> bool:
    """
    Авторизовать пользователя
    @return реузльтат авторизации
    """
    accounts_db_session = Session()
    print(f"Авторизация пользователя {user_id} ...")

    user: Account = accounts_db_session.query(Account).filter(Account.auth_key == auth_key).scalar()
    print(type(user))
    if user.user_id is not None and user.user_id != user_id:
        return False

    # user_roles = []
    # for user_record in user_records:
    #     user_roles.append(user_record.role)
    # if (user_record.role if user_record is not None else None) is not None:
    #     print(f"у пользователя {user_id} уже есть роль", user_record.role)
    #     return
    # account_db_record = Account(
    #     user_id = user_id,
    #     username = username,
    #     registration_date=datetime.now()
    # )

    # accounts_db_session.query().filter(
    #     Account.auth_key == auth_key
    # ).update({
    #     Account.user_id: user_id,
    #     Account.username: username,
    #     Account.registration_date: datetime.now()
    # })
    user.user_id = user_id
    user.username = username
    user.registration_date = datetime.now()

    # role = r
    # user_id=user_id, role=role, username=username,
    # user_fullname=user_fullname, registration_date=datetime.now())
    # accounts_db_session.add(role_db_record)

    accounts_db_session.commit()
    accounts_db_session.close()

    bot_stats.new_user(user.role)  ## remove later
    return True


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
#     roles_db_session = Session()
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
#     roles_db_session = Session()
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
#     roles_db_session = Session()
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
#     roles_db_session = Session()
#
#     user_id = str(user_id)
#     user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id)
#     for user_record in user_records:
#         roles_db_session.delete(user_record)
#     roles_db_session.commit()
#     roles_db_session.close()


# def change_role(user_id, new_role):
#     roles_db_session = Session()
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
    accounts_db_session = Session()

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
    return role_by_name.get(user.role)


def get_sch_identifier(user_id) -> str:
    accounts_db_session = Session()

    # user_id = str(user_id)
    user: Account = accounts_db_session.query(Account).filter(Account.user_id == user_id).scalar()
    print(type(user))
    user_identifier = user.sch_identifier

    accounts_db_session.close()
    return user_identifier


# def get_class_name(user_id):
#     roles_db_session = Session()
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
#     roles_db_session = Session()
#
#     user_id = str(user_id)
#     user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
#     teacher_name = user_records.teacher_name
#
#     roles_db_session.close()
#     return teacher_name


# refactored
# def get_all_users_ids():
#     accounts_db_session = Session()
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
#     accounts_db_session = Session()
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
    accounts_db_session = Session()

    user_id_set = set()
    users = accounts_db_session.query(Account).all() if role is None \
        else accounts_db_session.query(Account).filter(Account.role == role.name).all()

    for user in users:
        user_id_set.add(user.user_id)

    accounts_db_session.close()
    return user_id_set
