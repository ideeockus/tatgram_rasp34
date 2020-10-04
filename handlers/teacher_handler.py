from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
from bot import dp, bot
import yadisk
from bot_storage.configuration import yadisk_token
from bot_storage.Keyboards import teacher_photo_sending_kb, teacher_kb, InlineKeyboardButton, InlineKeyboardMarkup
import io
from bot_storage.rasp_base import get_all_teachers
from actions import feedback
from actions import teachers_rasp
from bot_storage import roles_base


class TeacherStates(StatesGroup):
    rasp_today = State()  # расписание на сегодня
    rasp_yesterday = State()  # расписание на завтра
    waiting_for_action = State()  # ожидание действий
    waiting_for_identifier = State()  # ждет имя
    waiting_for_photo = State()
    waiting_for_teacher_name = State()  # ждет имя учителя


@dp.message_handler(state=TeacherStates.waiting_for_identifier, content_types=types.ContentType.TEXT)
async def reg_teacher(message: types.Message, state: FSMContext):
    teacher_name = message.text.lower()
    user_id = message.from_user.id
    teachers_set = set(map(str.lower, get_all_teachers()))
    if teacher_name.lower() in teachers_set:
        roles_base.set_identifier(user_id, teacher_name.title())
        await message.answer("Отлично", reply_markup=teacher_kb)
        await message.answer("Теперь вы можете узнать расписание")
        await TeacherStates.waiting_for_action.set()
    else:
        teachers_choose_list = []
        teachers_choose_list_kb = InlineKeyboardMarkup(row_width=2)
        for teacher_full_name in teachers_set:
            if teacher_full_name.find(teacher_name) >= 0:
                teachers_choose_list.append(teacher_full_name)
                teacher_full_name_button = InlineKeyboardButton(teacher_full_name.title(),
                                                                callback_data=teacher_full_name)
                teachers_choose_list_kb.insert(teacher_full_name_button)
        if len(teachers_choose_list) < 1:
            await message.reply("Не могу найти такого учителя в базе, введите еще раз")
        elif len(teachers_choose_list) >= 1:
            await message.answer("Выберите учителя из списка", reply_markup=teachers_choose_list_kb)
            return


@dp.callback_query_handler(state=TeacherStates.waiting_for_identifier)
async def reg_teacher_full_name_inline(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await TeacherStates.waiting_for_action.set()
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    teacher_name = callback_query.data
    user_id = callback_query.from_user.id
    teachers_set = set(map(str.lower, get_all_teachers()))
    if teacher_name.lower() in teachers_set:
        roles_base.set_identifier(user_id, teacher_name.title())
        await bot.send_message(user_id, "Отлично", reply_markup=teacher_kb)
        await bot.send_message(user_id, "Теперь вы можете узнать расписание")
        await TeacherStates.waiting_for_action.set()


@dp.message_handler(lambda m: m.text == "Мое расписание", state=TeacherStates.waiting_for_action)
async def rasp(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    teacher_name = roles_base.get_identifier(user_id)
    if teacher_name is None:
        await message.answer("Упс, я забыл кто вы")
        await message.answer("Введите свое имя")
        await TeacherStates.waiting_for_identifier.set()
    await state.update_data(teacher_name=teacher_name.title())
    await teachers_rasp.make_teacher_rasp_request(message, TeacherStates.waiting_for_action, teacher_name)


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=TeacherStates.waiting_for_action)
async def other_teachers_rasp(message: types.Message):
    print("Запрос расписания учителей")
    await teachers_rasp.make_teacher_rasp_request(message, TeacherStates.waiting_for_action)


@dp.message_handler(lambda m: m.text == "Отправить фото", state=TeacherStates.waiting_for_action, content_types=types.ContentType.TEXT)
async def wanna_send_photo(message: types.Message):
    print("пользователь хочет прислать фото")
    await message.answer("Пожалуйста, отправьте фотографию", reply_markup=teacher_photo_sending_kb)
    await TeacherStates.waiting_for_photo.set()


@dp.message_handler(lambda m: m.text == "Назад (отправка фото окончена)", state=TeacherStates.waiting_for_photo)
async def photo_sending_end(message: types.Message, state: FSMContext):
    print("отправка фото закончена")
    await message.answer("Отлично", reply_markup=teacher_kb)
    await TeacherStates.waiting_for_action.set()


@dp.message_handler(state=TeacherStates.waiting_for_photo, content_types=types.ContentType.TEXT)
async def wait_for_photo_got_text(message: types.Message):
    await message.reply("Понятно, но я все еще жду фото")


@dp.message_handler(state=TeacherStates.waiting_for_photo, content_types=types.ContentType.PHOTO)
async def photo_getting(message: types.Message, state: FSMContext):
    print("Принимаю фото")
    photo_id = message.photo[-1].file_id

    photo = await bot.get_file(photo_id)
    photo_path = photo.file_path
    photo_name = str(datetime.now()) + ".jpg"
    loaded_file: io.BytesIO = await bot.download_file(photo_path)
    yandex_disk = yadisk.YaDisk(token=yadisk_token)
    yandex_disk.upload(loaded_file, "app:/" + "photo" + photo_name)
    await message.reply("Готово")


@dp.message_handler(state=TeacherStates.waiting_for_photo, content_types=types.ContentType.DOCUMENT)
async def document_getting(message: types.Message, state: FSMContext):
    print("Принимаю документ")
    file_id = message.document.file_id
    file_name = message.document.file_name

    file = await bot.get_file(file_id)
    file_path = file.file_path
    loaded_file: io.BytesIO = await bot.download_file(file_path)
    yandex_disk = yadisk.YaDisk(token=yadisk_token)
    yandex_disk.upload(loaded_file, "app:/"+file_name)
    await message.reply("Готово, документ оправлен")


@dp.message_handler(lambda m: m.text == "Обратная связь", state=TeacherStates.waiting_for_action)
async def rasp_yesterday(message: types.Message, state: FSMContext):
    await message.reply("Что вы хотите сообщить?", reply_markup=feedback.cancel_kb)
    await feedback.make_feedback(TeacherStates.waiting_for_action, end_keyboard=teacher_kb)




