from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bot_storage import bot_stats
from bot_storage.configuration import postgresql_db_url

Base = declarative_base()


class RoleRecord(Base):
    __tablename__ = "roles_db"
    id = Column(Integer)
    user_id = Column(String, primary_key=True)
    role = Column(String)


postgres_db = postgresql_db_url
engine = create_engine(postgres_db, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
roles_db_session = Session()


def reg_new(user_id, role):
    user_id = str(user_id)
    user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == str(user_id))
    user_roles = []
    for user_record in user_records:
        user_roles.append(user_record.role)
    if len(user_roles) > 0:
        print(f"у пользователя {user_id} уже есть роль")
        return
    role_db_record = RoleRecord(user_id=user_id, role=role)
    roles_db_session.add(role_db_record)
    roles_db_session.commit()

    bot_stats.new_user(role)  # учет статистики


def del_user_role(user_id):
    user_id = str(user_id)
    user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == str(user_id))
    for user_record in user_records:
        roles_db_session.delete(user_record)
    roles_db_session.commit()


def change_role(user_id, new_role):
    print(f"Смена роли пользователя {user_id} на {new_role}")
    user_id = str(user_id)
    del_user_role(user_id)
    user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == user_id)
    for user_record in user_records:
        roles_db_session.delete(user_record)
    role_db_record = RoleRecord(user_id=user_id, role=new_role)
    roles_db_session.add(role_db_record)
    roles_db_session.commit()


def get_role(user_id):
    user_id = str(user_id)
    user_records = roles_db_session.query(RoleRecord).filter(RoleRecord.user_id == str(user_id))
    user_roles = []

    for user_record in user_records:
        # print(f"У пользователя {user_record.user_id} записана роль {user_record.role}")
        user_roles.append(user_record.role)
    if len(user_roles) == 0:
        return None
    user_role = user_roles[0]
    return user_role


def get_all_users():
    user_id_set = set()
    user_records = roles_db_session.query(RoleRecord).all()
    for user_record in user_records:
        user_id_set.add(user_record.user_id)
    return user_id_set


