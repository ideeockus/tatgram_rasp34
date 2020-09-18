from openpyxl import load_workbook
from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
# from aiogram.utils.emoji import emojize


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
engine = create_engine('postgres:///rasp_db', echo=False)
Session = sessionmaker(bind=engine)
rasp_session = Session()


def get_lessons(class_name):
    rasp_lessons = rasp_session.query(Lessons).filter(Lessons.class_name == class_name)
    lessons_string = ""
    print(rasp_lessons)
    for lsn in rasp_lessons:
        print("LSN:", lsn)
        print(lsn.week_day)
        print(lsn.subject_name)
        print(lsn.room_number)
        lessons_string = lessons_string + " " + str(lsn.week_day) + " " + str(lsn.subject_name) + " " + str(lsn.room_number) + "\n"
        print("0.0")
    return lessons_string


def get_lessons_for_week_day(class_name: str, week_day: int):
    week_days_list = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    day_lessons = rasp_session.query(Lessons).filter(Lessons.class_name == class_name.upper(),
                                                     Lessons.week_day == week_days_list[week_day])  # выборка по бд

    day_lessons_text = ""
    for lsn in day_lessons:
        lesson_start = lsn.lesson_start_time[:-3]
        lesson_end = lsn.lesson_end_time[:-3]
        subject_name = lsn.subject_name
        room_number = lsn.room_number
        room_number = room_number if room_number is not None else ""
        day_lessons_text += f"[{lesson_start} - {lesson_end}] {subject_name} {room_number}\n"
    if day_lessons_text == "":
        print("__rasp_base:", "Уроков для класса", class_name, "на", week_days_list[week_day], "не найдено")
        return "Выходной"
    day_lessons_text_result = f"Расписание для класса {str(class_name)}:\n"
    day_lessons_text_result += "📅" + week_days_list[week_day] + "\n"
    day_lessons_text_result += day_lessons_text
    return day_lessons_text_result


def get_lessons_for_today(class_name: str):
    # week_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    current_week_day = datetime.now().weekday()
    # rasp_lessons = rasp_session.query(Lessons).filter(Lessons.class_name == class_name,
    # Lessons.week_day == week_days[current_week_day])
    return get_lessons_for_week_day(class_name, current_week_day)


def get_lessons_for_yesterday(class_name: str):
    next_week_day = (datetime.now() + timedelta(days=1)).weekday()
    # rasp_lessons = rasp_session.query(Lessons).filter(Lessons.class_name == class_name,
    # Lessons.week_day == week_days[current_week_day])
    return get_lessons_for_week_day(class_name, next_week_day)


def get_all_classes():
    classes_set = set()
    classes = rasp_session.query(Lessons.class_name)  # выборка по бд
    for class_name in classes:
        classes_set.add(class_name.class_name)
    return classes_set


def check_for_class(class_name) -> bool:  # проверить наличие класса в бд
    classes_map = map(str.lower, get_all_classes())  # к нижнему регстру
    classes_set = set(classes_map)
    return class_name.lower() in classes_set  # True or False


def get_lessons_by_day(day: str, class_name: str):
    day = day.lower()
    print("поиск в базе расписания для", class_name, "на", day)
    if day == "сегодня":
        return get_lessons_for_today(class_name)
    if day == "завтра":
        return get_lessons_for_yesterday(class_name)

    week_days_list = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    if day.capitalize() in week_days_list:
        week_day_num = week_days_list.index(day.capitalize())
        return get_lessons_for_week_day(class_name, week_day_num)
    else:
        print("__rasp_base:", "такого дня нет в базе")


