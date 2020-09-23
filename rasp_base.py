from openpyxl import load_workbook
from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from configuration import postgresql_db_url
# from aiogram.utils.emoji import emojize
# from configuration import postgresql_db_password


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
    teacher_name = Column(String)


# engine = create_engine('sqlite:///rasp.db', echo=True)
# postgres_db = "postgres://auovkhqgqesnwt:" + postgresql_db_password + "@ec2-54-246-85-151.eu-west-1.compute.amazonaws.com:5432/dce3m16p78rm71"
postgres_db = postgresql_db_url
# engine = create_engine('sqlite:///databases/rasp.db', echo=True)
engine = create_engine(postgres_db, echo=False)
engine = create_engine('sqlite:///databases/rasp.db', echo=False)
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
        teacher_name = lsn.teacher_name
        teacher_name = f"\n{teacher_name}" if teacher_name is not None else ""
        day_lessons_text += f"[{lesson_start} - {lesson_end}] {subject_name} кабинет {room_number}{teacher_name}\n\n"
    if day_lessons_text == "":
        print("__rasp_base:", "Уроков для класса", class_name, "на", week_days_list[week_day], "не найдено")
        return "Выходной"  # EDIT THIS LINE LATER
    day_lessons_text_result = f"Расписание для класса {str(class_name)}:\n"
    day_lessons_text_result += "📅" + week_days_list[week_day] + "\n"
    day_lessons_text_result += day_lessons_text
    return day_lessons_text_result


def get_lessons_for_today(class_name: str):
    current_week_day = datetime.now().weekday()
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


def get_all_teachers():
    teachers_set = set()
    teachers = rasp_session.query(Lessons.teacher_name)  # выборка по бд
    for teacher_name in teachers:
        teacher_name = teacher_name.teacher_name
        # print("teacher_name: ", teacher_name)
        if teacher_name is None or teacher_name == "":
            continue
        if teacher_name.find("/") > 0:
            splitted_teacher_cell = teacher_name.split(" / ")
            for teacher_name_splitted in splitted_teacher_cell:
                teachers_set.add(teacher_name_splitted.strip().lower())
        else:
            teachers_set.add(teacher_name.lower())
    # print(teachers_set)
    return teachers_set


def get_teacher_lessons_for_week_day(teacher: str, week_day: int):
    week_days_list = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    day_lessons = rasp_session.query(Lessons).filter(Lessons.teacher_name.ilike(f"%{teacher}%"),
                                                     Lessons.week_day == week_days_list[week_day])  # выборка по бд
    # day_lessons_text = ""
    day_lessons_dict = {}
    for lsn in day_lessons:
        lesson_start = lsn.lesson_start_time[:-3]
        lesson_end = lsn.lesson_end_time[:-3]
        subject_name = lsn.subject_name
        teacher_name = lsn.teacher_name
        class_name = lsn.class_name
        room_number = lsn.room_number
        room_number = f"в кабинете {room_number}" if room_number is not None else ""
        # day_lessons_text += f"[{lesson_start} - {lesson_end}] {subject_name} у {class_name} {room_number}\n"
        day_lessons_dict[lesson_start] = f"[{lesson_start} - {lesson_end}] {subject_name} у {class_name} {room_number}\n"
    if len(day_lessons_dict) == 0:
        print("__rasp_base:", "Уроков для учителя", teacher, "на", week_days_list[week_day], "не найдено")
        day_lessons_dict['dayoff'] = "Выходной"
    day_lessons_text_result = f"Расписание для учителя {str(teacher)}:\n"
    day_lessons_text_result += "📅" + week_days_list[week_day] + "\n"

    start_times = list(day_lessons_dict.keys())
    start_times.sort()
    for start_time in start_times:
        day_lessons_text_result += day_lessons_dict[start_time]
    return day_lessons_text_result





