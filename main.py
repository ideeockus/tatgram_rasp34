from aiogram import executor, types, Dispatcher
from bot_storage.Keyboards import guest_kb
from aiogram.dispatcher import FSMContext
from bot_storage.UserStates import GuestStates, get_role_waiting_for_action_state
from bot import dp, bot
from bot_storage.accounts_base import get_role
from handlers import common_handlers, guest_handlers, teacher_handler, pupil_handler, master_handler  # handlers
from bot_storage import accounts_base
from bot_storage.configuration import feedback_tg_id, creator_id
from bot_storage.accounts_base import Roles
from utils.scheduled_tasks import set_weakly_stats_clear_task
from actions.notify_actions import quiet_admin_notification
from middlewares.common_middleware import CommonMiddleware
from bot_storage import Keyboards


@dp.message_handler()
async def unregistered_msg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_role = accounts_base.get_role(user_id)
    print(" - unregistered message", user_id, user_role)
    if user_role is None:
        await message.answer("Выберите опцию", reply_markup=guest_kb)
        await GuestStates.waiting_for_action.set()
    else:
        await define_action(message, state)


async def define_action(message: types.Message, state: FSMContext):
    """
    Определить дальнейшее действие по сообщению и роли пользователя
    (Если вдруг бот перезагрузился посреди диалога)
    """
    user_id = str(message.from_user.id)
    user_role = accounts_base.get_role(user_id)
    if user_role == Roles.pupil or user_role == Roles.parent or user_role == Roles.headman:
        await pupil_handler.PupilStates.waiting_for_action.set()
        if message.text in ["На сегодня", "На завтра"]:
            await pupil_handler.rasp_today_yesterday(message, state)
        elif message.text == "По дням":
            await pupil_handler.rasp_by_day(message, state)
        elif message.text == "Обратная связь":
            await pupil_handler.pupil_feedback(message)
        elif message.text == "Для другого класса":
            await pupil_handler.req_rasp_for_other_class(message)
        elif message.text == "Расписание учителей":
            await pupil_handler.teacher_rasp(message)
        else:
            await message.answer("Здравствуйте", reply_markup=Keyboards.pupil_kb)
    elif user_role == Roles.teacher:
        await teacher_handler.TeacherStates.waiting_for_action.set()
        if message.text == "Мое расписание":
            await teacher_handler.rasp(message, state)
        elif message.text == "Расписание учителей":
            await teacher_handler.other_teachers_rasp(message)
        elif message.text == "Отправить фото":
            await teacher_handler.wanna_send_photo(message)
        else:
            await message.answer("Здравствуйте", reply_markup=Keyboards.teacher_kb)
    elif user_role == Roles.master:
        await master_handler.MasterStates.waiting_for_action.set()
        await message.answer("Здравствуйте. Уведомляю что с момента вашего последнего сообщения бот перезагружался",
                             reply_markup=Keyboards.master_kb)
        if message.text == "Статистика":
            await master_handler.stats(message)
        elif message.text == "Рассылка":
            await master_handler.broadcast(message)
        elif message.text == "Расписание школьников":
            await master_handler.pupils_rasp(message)
        elif message.text == "Расписание учителей":
            await master_handler.teachers_rasp(message)
        elif message.text == "Загрузить расписание":
            await master_handler.upload_rasp(message)
        else:
            await message.answer("Команда не распознана")
    else:
        await message.answer("Команда не определена")


@dp.message_handler(state="*")
async def other_msg(message: types.Message, state: FSMContext):
    print(f"other message, state: {await state.get_state()}; state_data: {await state.get_data()}")
    user_state = await state.get_state()

    if user_state == get_role_waiting_for_action_state(get_role(message.from_user.id)).state:
        # for base state
        print("message ignored")
        # await message.reply("Не могу определить что мне нужно делать")
        # await message.reply("Throttle rate 2")
        # await dp.throttle(key="1", rate=2, user_id=message.from_user.id)
    else:
        await message.reply("Сначала завершите предыдущее действие")


@dp.callback_query_handler(state="*")
async def empty_callback_query(callback_query: types.CallbackQuery, state: FSMContext):
    print(f"unrecognized callback query, callback_data: {callback_query.data}; state: {await state.get_state()}")
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.errors_handler()
async def error_handler(update: types.Update, exception: Exception):
    error_info_message = "Возникла какая-то ошибка 🙄, описание недоступно. Возможно пора вызывать магов 🔮\n\n"
    try:
        error_info_message = "🙄🙄🙄\nСообщение для администратора:\n" \
                             "Произошла ошибка при обработке сообщения пользователя " \
                             f"@{update.message.from_user.username} [{update.message.from_user.id}]\n" \
                             f"{update.message.from_user.full_name}\n" \
                             f"Сообщение: {update.message.text}\n\n" \
                             "Подробнее смотрите в логах.\n" + str(exception)
    except Exception as e:
        error_info_message += f"Ну, зато вот ошибка из-за которой описание недоступно:\n {e}\n\n"
        error_info_message += f"И еще вот какая-то штука:\n {str(exception)}"
    if feedback_tg_id == creator_id:
        await bot.send_message(creator_id, error_info_message)
        return
    await bot.send_message(feedback_tg_id, error_info_message)
    await bot.send_message(creator_id, error_info_message)
    # ## psycopg2.errors.AdminShutdown exception handler ?


async def on_aiogram_startup(aiogram_dp: Dispatcher):
    # await quiet_admin_notification("Бот запущен 🤖")
    print("Бот запущен 🤖")
    set_weakly_stats_clear_task(False)


async def on_aiogram_shutdown(aiogram_dp: Dispatcher):
    await quiet_admin_notification("Бот отключается. До связи 😵")
    print("Бот отключается. До связи 😵")

if __name__ == '__main__':
    dp.middleware.setup(CommonMiddleware())
    executor.start_polling(dp, skip_updates=True, on_startup=on_aiogram_startup, on_shutdown=on_aiogram_shutdown)
