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


class StatsType(Enum):
    General = "general"
    ByClass = "byclass"


# by_class_bd_values = {
#     # перевод значений из бд в human-readable формат
#     "for_class_": "Запросов для "
# }

# human_readable_format = {
#     'for_class': "Запросов для класса "
# }

by_class_prefix = "Запросов для класса"
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


def get_stats(stats_type: StatsType):
    stats_db_session = Session()
    stats = stats_db_session.query(Stat).all()
    stats_text = ""
    for stat in stats:
        if stats_type == StatsType.General and (stat.name in stat_by_name.keys()):
            stats_text += stat_by_name.get(str(stat.name)) + " = " + str(stat.value) + "\n"
        if stats_type == StatsType.ByClass and (stat.name not in stat_by_name.keys()) and by_class_prefix in stat.name:
            stats_text += str(stat.name) + " = " + str(stat.value) + "\n"
        # stats_text += (stat_by_name.get(str(stat.name)) or str(stat.name)) + " = " + str(stat.value) + "\n"
    stats_db_session.close()
    return stats_text


def inc_req_stat_by_class(classname: str):
    stats_db_session = Session()
    requests_by_class_stat = stats_db_session.query(Stat).filter(Stat.name == f"{by_class_prefix} {classname}").scalar()
    if requests_by_class_stat is None:
        stats_db_session.add(Stat(name=f"{by_class_prefix} {classname}", value=1))
        # requests_by_class_stat = \
        #     stats_db_session.query(Stat).filter(Stat.name == f"{by_class_prefix} {classname}").scalar()
    else:
        requests_by_class_stat.value += 1
    stats_db_session.commit()
    stats_db_session.close()


def clean_stats(stats_type: StatsType):
    stats_db_session = Session()
    stats = stats_db_session.query(Stat).all()
    for stat in stats:
        if stats_type == StatsType.General and (stat.name in stat_by_name.keys()):
            stats_db_session.delete(stat)
        if stats_type == StatsType.ByClass and (stat.name not in stat_by_name.keys()) and by_class_prefix in stat.name:
            stats_db_session.delete(stat)
    stats_db_session.commit()
    stats_db_session.close()


def parse_stat_by_class(stat_by_class_text: str) -> dict:
    by_class_res_dict = {}
    for s in stat_by_class_text.split("\n"):
        if by_class_prefix not in s:
            continue
        class_name_with_prefix, stat_count = s.split("=")
        class_name = class_name_with_prefix[len(by_class_prefix):]  # тут еще пробел учитывается
        by_class_res_dict[class_name.strip()] = int(stat_count)
    return by_class_res_dict


# def inc_req_stat_by_class(classname: str):
#     stats_db_session = Session()
#     stat_name = f"REQ{classname}"
#     requests_by_class_stat = stats_db_session.query(Stat).filter(Stat.name == stat_name).scalar()
#     if requests_by_class_stat is None:
#         stats_db_session.add(Stat(name=stat_name, value=1))
#         requests_by_class_stat = stats_db_session.query(Stat).filter(Stat.name == stat_name).scalar()
#     else:
#         requests_by_class_stat.value += 1
#     stats_db_session.commit()
#     stats_db_session.close()


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


# def clear_rasp_reqs_stat():
#     stats_db_session = Session()
#     clearing_stat_list = stats_db_session.query(Stat).filter(Stat.name in ["get_rasp_total",
#                                                                            "get_class_rasp", "get_teacher_rasp"]).all()
#     for clearing_stat in clearing_stat_list:
#         clearing_stat.value = 0
#     stats_db_session.commit()
#     stats_db_session.close()



