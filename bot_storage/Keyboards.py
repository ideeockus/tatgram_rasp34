from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta


# global keys
from bot_storage.accounts_base import Roles

feedback_button = KeyboardButton("Обратная связь")

# deprecated
# # Клавиатура для выбора роли
# pupil_role_button = KeyboardButton("Ученик")
# teacher_role_button = KeyboardButton("Учитель")
# parent_role_button = KeyboardButton("Родитель")
# choose_role_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
# choose_role_kb.row(pupil_role_button, teacher_role_button, parent_role_button)


enter_auth_key_btn = KeyboardButton("Ввести ключ аутентификации")
become_supervisor_btn = KeyboardButton("Я родитель")
guest_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
guest_kb.row(enter_auth_key_btn, become_supervisor_btn)


# Клавиатура учеников
rasp_today_button = KeyboardButton("На сегодня")
rasp_yesterday_button = KeyboardButton("На завтра")
rasp_by_day_button = KeyboardButton("По дням")
other_class_rasp_button = KeyboardButton("Для другого класса")
pupil_kb = ReplyKeyboardMarkup(resize_keyboard=False)  # тут сделал False т.к. вроде так лучше
pupil_kb.row(rasp_today_button, rasp_yesterday_button)
pupil_kb.add(rasp_by_day_button)
pupil_kb.add(other_class_rasp_button)
pupil_kb.add(feedback_button)


# Инлайн клавиатура выбора расписания
week_start_timedelta = timedelta(days=datetime.now().weekday())
week_start_date = datetime.now() - week_start_timedelta
week_days_text = []
dd = [(week_start_date+timedelta(days=i)).date() for i in range(8)]
for d in list(map(lambda d: str(d).split("-")[1:], dd)):
    d.reverse()
    week_days_text.append(".".join(d))
rasp_by_days_kb = InlineKeyboardMarkup(row_width=2)
mon_button = InlineKeyboardButton("Понедельник "+week_days_text[0], callback_data="monday")
tue_button = InlineKeyboardButton("Вторник "+week_days_text[1], callback_data="tuesday")
wed_button = InlineKeyboardButton("Среда "+week_days_text[2], callback_data="wednesday")
thu_button = InlineKeyboardButton("Четверг "+week_days_text[3], callback_data="thursday")
fri_button = InlineKeyboardButton("Пятница "+week_days_text[4], callback_data="friday")
sat_button = InlineKeyboardButton("Суббота "+week_days_text[5], callback_data="saturday")
week_button = InlineKeyboardButton(f"Неделя {week_days_text[0]} - {week_days_text[7]}", callback_data="week")

rasp_by_days_kb.add(mon_button, tue_button, wed_button, thu_button, fri_button, sat_button)
rasp_by_days_kb.row(week_button)


# Клавиатура учителей
teacher_rasp_button = KeyboardButton("Мое расписание")
all_teachers_rasp_button = KeyboardButton("Расписание учителей")
teacher_photo_button = KeyboardButton("Отправить фото")
pupils_rasp_button = KeyboardButton("Расписание школьников")
teacher_kb = ReplyKeyboardMarkup(resize_keyboard=True)
teacher_kb.add(teacher_rasp_button)
teacher_kb.row(all_teachers_rasp_button, teacher_photo_button)
teacher_kb.add(pupils_rasp_button)
teacher_kb.add(feedback_button)

teacher_photo_end_button = KeyboardButton("Назад (отправка фото окончена)")
teacher_photo_sending_kb = ReplyKeyboardMarkup(resize_keyboard=True)
teacher_photo_sending_kb.row(teacher_photo_end_button)


# Клавиатура дял старост
headman_kb = ReplyKeyboardMarkup(resize_keyboard=True)
headman_kb.row(rasp_today_button, rasp_yesterday_button)
headman_kb.add(rasp_by_day_button)
headman_kb.add(other_class_rasp_button, all_teachers_rasp_button)
headman_kb.add(feedback_button)

# Клавиатура для выбора цели рассылки
broadcast_choose_target_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
teacher_target_btn = KeyboardButton("Учителям")
pupil_target_btn = KeyboardButton("Ученикам")
parent_target_btn = KeyboardButton("Родителям")
headman_target_btn = KeyboardButton("Старостам")
all_target_btn = KeyboardButton("Общая рассылка")
cancel_btn = KeyboardButton("Отмена")
broadcast_choose_target_kb.row(all_target_btn)
broadcast_choose_target_kb.add(teacher_target_btn, pupil_target_btn, parent_target_btn, headman_target_btn)
broadcast_choose_target_kb.row(cancel_btn)

# Клавиатура админа
master_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
stats_button = KeyboardButton("Статистика")
broadcast_button = KeyboardButton("Рассылка")
pupils_rasp_button = KeyboardButton("Расписание школьников")
teachers_rasp_button = KeyboardButton("Расписание учителей")
update_rasp_button = KeyboardButton("Загрузить расписание")
upload_accounts_button = KeyboardButton("Загрузить базу аккаунтов")
master_kb.add(stats_button)
master_kb.add(broadcast_button)
master_kb.add(pupils_rasp_button, teachers_rasp_button)
master_kb.add(update_rasp_button, upload_accounts_button)


# Клавиатура отмены действия
cancel_button = KeyboardButton("Отмена")
cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.add(cancel_button)


def get_role_keyboard(role: Roles):
    role_keyboard = None
    if role == Roles.pupil:
        role_keyboard = pupil_kb
    elif role == Roles.headman:
        role_keyboard = headman_kb
    elif role == Roles.parent:
        role_keyboard = pupil_kb
    elif role == Roles.teacher:
        role_keyboard = teacher_kb
    elif role == Roles.master:
        role_keyboard = master_kb
    else:
        role_keyboard = guest_kb
    return role_keyboard





