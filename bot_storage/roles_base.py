from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bot_storage import bot_stats
from bot_storage.configuration import postgresql_db_url

Base = declarative_base()


class RoleRecord(Base):
    __tablename__ = "roles_db"
    # id = Column(Integer)
    user_id = Column(String, primary_key=True)
    role = Column(String)
    identifier = Column(String)  # идентификатор
    class_name = Column(String)  # имя класса
    teacher_name = Column(String)  # имя учителя
    username = Column(String)
    user_fullname = Column(String)


postgres_db = postgresql_db_url
engine = create_engine(postgres_db, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
# roles_db_session = Session()


def reg_new(user_id, role, username="", user_fullname=""):
    roles_db_session = Session()

    user_id = str(user_id)
    user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == str(user_id)).scalar()
    # user_roles = []
    # for user_record in user_records:
    #     user_roles.append(user_record.role)
    if user_record is not None:
        print(f"у пользователя {user_id} уже есть роль")
        return
    role_db_record = RoleRecord(user_id=user_id, role=role, username=username, user_fullname=user_fullname)
    roles_db_session.add(role_db_record)
    roles_db_session.commit()

    bot_stats.new_user(role)  # учет статистики


# def reg_class(user_id, class_name):
#     print("__user_base:", f"регистрация {user_id} в классе {class_name}")
#     user_id = str(user_id)
#     user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
#     if user_record is None:
#         print(f"Пользователь {user_id} не может быть зарегестрирова в классе, т.к. его нет в базе")
#         return
#     user_record.identifier = class_name
#     roles_db_session.commit()


def set_identifier(user_id, identifier):
    roles_db_session = Session()

    print(f"{user_id} теперь зарегестрирован как {identifier}")
    user_id = str(user_id)
    user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
    if user_record is None:
        print(f"Пользователь {user_id} не может быть зарегестрирован, т.к. его нет в базе")
        return
    user_record.identifier = identifier
    roles_db_session.commit()


def set_class_name(user_id, class_name):
    roles_db_session = Session()

    print(f"{user_id} зарегестрирован в классе {class_name}")
    user_id = str(user_id)
    user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
    if user_record is None:
        print(f"Пользователь {user_id} не может быть зарегестрирован, т.к. его нет в базе")
        return
    user_record.class_name = class_name
    roles_db_session.commit()


def set_teacher_name(user_id, teacher_name):
    roles_db_session = Session()

    print(f"{user_id} зарегестрирован как {teacher_name}")
    user_id = str(user_id)
    user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
    if user_record is None:
        print(f"Пользователь {user_id} не может быть зарегестрирован, т.к. его нет в базе")
        return
    user_record.teacher_name = teacher_name
    roles_db_session.commit()


def del_user_role(user_id):
    roles_db_session = Session()

    user_id = str(user_id)
    user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id)
    for user_record in user_records:
        roles_db_session.delete(user_record)
    roles_db_session.commit()


def change_role(user_id, new_role):
    roles_db_session = Session()

    print(f"Смена роли пользователя {user_id} на {new_role}")
    user_id = str(user_id)
    # del_user_role(user_id)
    user_record = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
    if user_record is None:
        print("__user_base:", f"Пользователя {user_id} нет в базе")
    bot_stats.edit_stat(get_role(user_id), -1)
    user_record.role = new_role
    # for user_record in user_records:
    #     roles_db_session.delete(user_record)
    # role_db_record = RoleRecord(user_id=user_id, role=new_role)
    # roles_db_session.add(role_db_record)
    roles_db_session.commit()

    bot_stats.edit_stat(new_role, 1)


def get_role(user_id):
    roles_db_session = Session()

    user_id = str(user_id)
    user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
    if user_records is None:
        return None
    user_role = user_records.role
    # user_roles = []
    #
    # for user_record in user_records:
    #     # print(f"У пользователя {user_record.user_id} записана роль {user_record.role}")
    #     user_roles.append(user_record.role)
    # if len(user_roles) == 0:
    #     return None
    # user_role = user_roles[0]
    return user_role


def get_identifier(user_id):
    roles_db_session = Session()

    user_id = str(user_id)
    user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
    user_identifier = user_records.identifier
    return user_identifier


def get_class_name(user_id):
    roles_db_session = Session()

    user_id = str(user_id)
    user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
    class_name = user_records.class_name
    return class_name


def get_teacher_name(user_id):
    roles_db_session = Session()

    user_id = str(user_id)
    user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id).scalar()
    teacher_name = user_records.teacher_name
    return teacher_name


def get_all_users():
    roles_db_session = Session()

    user_id_set = set()
    user_records = roles_db_session.query(RoleRecord).all()
    for user_record in user_records:
        user_id_set.add(user_record.user_id)
    return user_id_set


