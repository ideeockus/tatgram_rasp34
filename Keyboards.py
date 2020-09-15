from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

rasp_button = KeyboardButton("Расписание")
for_teacher_button = KeyboardButton("Для учителя")
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row(rasp_button, for_teacher_button)


teacher_rasp_button = KeyboardButton("Расписание учителей")
teacher_photo_button = KeyboardButton("Отправить фото")
teacher_kb = ReplyKeyboardMarkup(resize_keyboard=True)
teacher_kb.row(teacher_rasp_button, teacher_photo_button)




