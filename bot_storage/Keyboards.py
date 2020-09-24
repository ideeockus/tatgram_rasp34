from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta


pupil_role_button = KeyboardButton("Ученик")
teacher_role_button = KeyboardButton("Учитель")
parent_role_button = KeyboardButton("Родитель")
choose_role_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
choose_role_kb.row(pupil_role_button, teacher_role_button, parent_role_button)

feedback_button = KeyboardButton("Обратная связь")

# rasp_button = KeyboardButton("Расписание")
rasp_today_button = KeyboardButton("На сегодня")
rasp_yesterday_button = KeyboardButton("На завтра")
rasp_by_day_button = KeyboardButton("По дням")
other_class_rasp_button = KeyboardButton("Для другого класса")
# for_teacher_button = KeyboardButton("Для учителя")
pupil_kb = ReplyKeyboardMarkup(resize_keyboard=True)
pupil_kb.row(rasp_today_button, rasp_yesterday_button)
pupil_kb.add(rasp_by_day_button)
pupil_kb.add(other_class_rasp_button)
pupil_kb.add(feedback_button)

week_start_timedelta = timedelta(days=datetime.now().weekday())
week_start_date = datetime.now() - week_start_timedelta
week_days_text = []
dd = [(week_start_date+timedelta(days=i)).date() for i in range(7)]
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
rasp_by_days_kb.add(mon_button, tue_button, wed_button, thu_button, fri_button, sat_button)


teacher_rasp_button = KeyboardButton("Расписание учителей")
teacher_photo_button = KeyboardButton("Отправить фото")
teacher_kb = ReplyKeyboardMarkup(resize_keyboard=True)
teacher_kb.row(teacher_rasp_button, teacher_photo_button)
teacher_kb.add(feedback_button)


teacher_photo_end_button = KeyboardButton("Назад (отправка фото окончена)")
teacher_photo_sending_kb = ReplyKeyboardMarkup(resize_keyboard=True)
teacher_photo_sending_kb.row(teacher_photo_end_button)


secret_role_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

stats_button = KeyboardButton("Статистика")
broadcast_button = KeyboardButton("Рассылка")
pupils_rasp_button = KeyboardButton("Расписание школьников")
teachers_rasp_button = KeyboardButton("Расписание учителей")

secret_role_kb.add(stats_button)
secret_role_kb.add(broadcast_button)
secret_role_kb.add(pupils_rasp_button, teacher_rasp_button)
# secret_role_kb.add(teachers_rasp_button)

secret_role_cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_button = KeyboardButton("Отмена")
secret_role_cancel_kb.add(cancel_button)








