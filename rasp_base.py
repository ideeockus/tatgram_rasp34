from openpyxl import load_workbook
from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime


"""
A - 0 empty column
B - 1 class_name
C - 2 week_day
D -3 lesson_start_time
E -4 lesson_end_time
F - 5 subject_name
G - 6 room_number
"""


Base = declarative_base()  # декларативный базовый класс


class Lessons(Base):
    __tablename__ = "rasp_db"
    id = Column(Integer, primary_key=True)
    class_name = Column(String)
    week_day = Column(String)
    lesson_start_time = Column(String)
    lesson_end_time = Column(String)
    subject_name = Column(String)
    room_number = Column(String)


# engine = create_engine('sqlite:///rasp.db', echo=True)
engine = create_engine('postgres:///rasp_db', echo=True)
Session = sessionmaker(bind=engine)
rasp_session = Session()

