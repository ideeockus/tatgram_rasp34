from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bot_storage.configuration import postgresql_db_url
from enum import Enum
import json

Base = declarative_base()


class Stat(Base):
    __tablename__ = "bot_stats_db"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Integer)


class StatFields(Enum):
    TOTAL_USERS = "total_users"
    PUPILS = "pupils"
    TEACHERS = "teachers"
    PARENTS = "parents"

    GET_CLASS_RASP = "get"


postgres_db = postgresql_db_url
engine = create_engine(postgres_db, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
# stats_db_session = Session()


def get_stats():
    stat_by_name = {
        'total_users': "Всего пользователей",
        'teacher': "Учителей",
        'headman': "Старост",
        'pupil': "Учеников",
        'parent': "Родителей",
        'master': "Администраторов",
        'get_rasp_total': "Всего запросов расписания",
        'get_class_rasp': "Запросов расписания по классам",
        'get_teacher_rasp': "Запросов расписания по учителям",
    }
    stats_db_session = Session()
    stats = stats_db_session.query(Stat).all()
    stats_text = ""
    for stat in stats:
        stats_text += (stat_by_name.get(str(stat.name)) or str(stat.name)) + " = " + str(stat.value) + "\n"
    stats_db_session.close()
    return stats_text


def inc_req_stat_by_class(classname: str):
    stats_db_session = Session()
    requests_by_class_stat = stats_db_session.query(Stat).filter(Stat.name == f"Запросов для {classname}").scalar()
    if requests_by_class_stat is None:
        stats_db_session.add(Stat(name=f"Запросов для {classname}", value=1))
        requests_by_class_stat = stats_db_session.query(Stat).filter(Stat.name == f"Запросов для {classname}").scalar()
    else:
        requests_by_class_stat.value += 1
    stats_db_session.commit()
    stats_db_session.close()


def new_user(role: str):
    stats_db_session = Session()
    total_users = stats_db_session.query(Stat).filter(Stat.name == "total_users").scalar()
    if total_users is None:
        stats_db_session.add(Stat(name="total_users", value=0))
        total_users = stats_db_session.query(Stat).filter(Stat.name == "total_users").scalar()
    total_users.value += 1

    roles = stats_db_session.query(Stat).filter(Stat.name == role).scalar()
    if roles is None:
        stats_db_session.add(Stat(name=role, value=0))
        roles = stats_db_session.query(Stat).filter(Stat.name == role).scalar()
    roles.value += 1

    stats_db_session.commit()
    stats_db_session.close()


def edit_stat(stat_name: str, value_delta: int):
    stats_db_session = Session()
    # print("__bot_stats:", f"изменение параметра статистики {stat_name} на {value_delta}")
    editable_stat = stats_db_session.query(Stat).filter(Stat.name == stat_name).scalar()
    if editable_stat is None:
        stats_db_session.add(Stat(name=stat_name, value=0))
        editable_stat = stats_db_session.query(Stat).filter(Stat.name == stat_name).scalar()
    editable_stat.value += value_delta
    stats_db_session.commit()
    stats_db_session.close()


def clear_rasp_reqs_stat():
    stats_db_session = Session()
    clearing_stat_list = stats_db_session.query(Stat).filter(Stat.name in ["get_rasp_total",
                                                                           "get_class_rasp", "get_teacher_rasp"]).all()
    for clearing_stat in clearing_stat_list:
        clearing_stat.value = 0
    stats_db_session.commit()
    stats_db_session.close()



