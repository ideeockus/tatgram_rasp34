from aiogram.dispatcher.filters.state import State, StatesGroup


class MainStates(StatesGroup):
    wait_for_role = State()


class PupilStates(StatesGroup):
    waiting_for_class_name = State()  # ожидание номера класса
    waiting_for_action = State()  # ожидание действий
    waiting_for_identifier = State()  # ждет название класса
    waiting_for_registration = State()
    waiting_for_other_class_name = State()  # для другого класса


class TeacherStates(StatesGroup):
    rasp_today = State()  # расписание на сегодня
    rasp_yesterday = State()  # расписание на завтра
    waiting_for_action = State()  # ожидание действий
    waiting_for_identifier = State()  # ждет имя
    waiting_for_photo = State()
    waiting_for_teacher_name = State()  # ждет имя учителя


class MasterStates(StatesGroup):
    waiting_for_action = State()  # ожидание действий
    waiting_for_text_to_broadcast = State()
    waiting_for_class_name = State()
    waiting_for_teacher_name = State()
    waiting_for_rasp_file = State()


