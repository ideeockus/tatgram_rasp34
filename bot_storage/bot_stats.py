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
    # total_users = Column(Integer)
    # pupils = Column(Integer)
    # teachers = Column(Integer)
    # parents = Column(Integer)


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

    # if role == "pupil":
    #     pupils = stats_db_session.query(Stat).filter(Stat.name == StatFields.PUPILS.value).scalar()
    #     if pupils is None:
    #         stats_db_session.add(Stat(name=StatFields.PUPILS.value, value=0))
    #         pupils = stats_db_session.query(Stat).filter(Stat.name == StatFields.PUPILS.value).scalar()
    #     pupils += 1
    # if role == "teacher":
    #     teachers = stats_db_session.query(Stat).filter(Stat.name == StatFields.TEACHERS.value).scalar()
    #     if teachers is None:
    #         stats_db_session.add(Stat(name=StatFields.TEACHERS.value, value=0))
    #         teachers = stats_db_session.query(Stat).filter(Stat.name == StatFields.TEACHERS.value).scalar()
    #     teachers += 1
    # if role == "parent":
    #     parents = stats_db_session.query(Stat).filter(Stat.name == StatFields.PARENTS.value).scalar()
    #     if parents is None:
    #         stats_db_session.add(Stat(name=StatFields.PARENTS.value, value=0))
    #         parents = stats_db_session.query(Stat).filter(Stat.name == StatFields.PARENTS.value).scalar()
    #     parents += 1

    # roles = stats_db_session.query(Stat).filter(Stat.name == role).scalar()
    # if roles is None:
    #     stats_db_session.add(Stat(name=role, value=0))
    #     parents = stats_db_session.query(Stat).filter(Stat.name == role).scalar()
    # roles += 1

    stats_db_session.commit()





