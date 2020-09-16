from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

pupil_role_button = KeyboardButton("Ученик")
teacher_role_button = KeyboardButton("Учитель")
parent_role_button = KeyboardButton("Родитель")
choose_role_kb = ReplyKeyboardMarkup(resize_keyboard=True)
choose_role_kb.row(pupil_role_button, teacher_role_button, parent_role_button)

rasp_button = KeyboardButton("Расписание")
rasp_today_button = KeyboardButton("На сегодня")
rasp_yesterday_button = KeyboardButton("На завтра")
# for_teacher_button = KeyboardButton("Для учителя")
pupil_kb = ReplyKeyboardMarkup(resize_keyboard=True)
pupil_kb.row(rasp_today_button, rasp_yesterday_button)


teacher_rasp_button = KeyboardButton("Расписание учителей")
teacher_photo_button = KeyboardButton("Отправить фото")
teacher_kb = ReplyKeyboardMarkup(resize_keyboard=True)
teacher_kb.row(teacher_rasp_button, teacher_photo_button)




