from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import Enum as sqlalchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from bot_storage.configuration import db_url

from enum import Enum

Base = declarative_base()  # декларативный базовый класс


class Roles(Enum):
    teacher = "Учитель"
    pupil = "Ученик"
    headman = "Староста"
    parent = "Родитель"
    master = "Админ"
    guest = "Гость"


user_supervisor_relationship = Table(
    "user_supervisor_relationship", Base.metadata,
    Column("supervisor_id", ForeignKey("accounts_db.id"), primary_key=True),
    Column("controlled_user_id", ForeignKey("accounts_db.id"), primary_key=True),
    # UniqueConstraint('supervisor_id', 'controlled_user_id')
)


class Account(Base):
    __tablename__ = "accounts_db"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    role = Column(sqlalchemyEnum(Roles))
    sch_identifier = Column(String)
    auth_key = Column(String, unique=True)
    supervisor_user_ids = relationship(
        "Account", secondary=user_supervisor_relationship,
        primaryjoin=(user_supervisor_relationship.c.controlled_user_id == id),
        secondaryjoin=(user_supervisor_relationship.c.supervisor_id == id)
    )  # list of supervisors of user
    registration_date = Column(DateTime)


class Lessons(Base):
    __tablename__ = "rasp_db"
    id = Column(Integer, primary_key=True)
    class_name = Column(String)
    week_day = Column(String)
    lesson_start_time = Column(String)
    lesson_end_time = Column(String)
    subject_name = Column(String)
    room_number = Column(String)
    teacher_name = Column(String)


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


# postgres_db = db_url
engine = create_engine(db_url, echo=False)
Base.metadata.create_all(engine)
# DbSession = sessionmaker(bind=engine, expire_on_commit=False)
