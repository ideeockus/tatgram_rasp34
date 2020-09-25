from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bot_storage.configuration import postgresql_db_url
from enum import Enum

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


postgres_db = postgresql_db_url
engine = create_engine(postgres_db, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
stats_db_session = Session()


def get_stats():
    stats = stats_db_session.query(Stat).all()
    stats_text = ""
    for stat in stats:
        stats_text += str(stat.name) + " = " + str(stat.value) + "\n"
    return stats_text


def new_user(role: str):
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


def edit_stat(stat_name: str, value_delta: int):
    # print("__bot_stats:", f"изменение параметра статистики {stat_name} на {value_delta}")
    editable_stat = stats_db_session.query(Stat).filter(Stat.name == stat_name).scalar()
    if editable_stat is None:
        stats_db_session.add(Stat(name=stat_name, value=0))
        editable_stat = stats_db_session.query(Stat).filter(Stat.name == stat_name).scalar()
    editable_stat.value += value_delta
    stats_db_session.commit()





