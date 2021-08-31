from aiogram import executor, types, Dispatcher
from bot_storage.Keyboards import teacher_kb, guest_kb, headman_kb, get_role_keyboard, cancel_kb
from aiogram.dispatcher import FSMContext
from bot_storage.UserStates import GuestStates, MainStates, get_role_waiting_for_action_state
from bot import dp, bot
# from bot_storage.accounts_base import get_role
from handlers import common_handlers, teacher_handler, pupil_handler, master_handler
from bot_storage.Keyboards import ReplyKeyboardRemove, master_kb
from bot_storage import accounts_base
from bot_storage.accounts_base import Roles
from bot_storage.configuration import botmaster_role_phrase, feedback_tg_id, creator_id
from utils.scheduled_tasks import set_weakly_stats_clear_task
from actions.notify_admins import notify_admins, quiet_admin_notification
from middlewares.common_middleware import CommonMiddleware


@dp.message_handler(state=GuestStates.waiting_for_action)
async def guest_action(message: types.Message):
    if message.text == "Ввести ключ аутентификации":
        await GuestStates.waiting_for_auth_key.set()
        await message.answer("Введите ваш ключ", reply_markup=cancel_kb)
    elif message.text == "parent":
        await GuestStates.waiting_for_controlled_key.set()
        await message.answer("Введите ключ", reply_markup=cancel_kb)
    elif message.text == botmaster_role_phrase:
        user_id = message.from_user.id
        username = message.from_user.username
        user_firstname = message.from_user.first_name
        user_lastname = message.from_user.last_name

        user_account = accounts_base.reg_user(user_id, Roles.master, username, user_firstname, user_lastname)

        if user_account is None:
            print(f"Registration master {username}[{user_id}] failed")
            await message.reply(f"Что-то пошло не так. Зарегестрироваться не удалось")
            return

        print(f"Master {username}[{user_id}] registration successful")
        await get_role_waiting_for_action_state(Roles.master).set()
        await message.reply(f"Вы успешно зарегестрированы как {Roles.master}", reply_markup=master_kb)
    else:
        await message.answer("Выберите опцию с помощью кнопок")


@dp.message_handler(state=GuestStates.waiting_for_auth_key)
async def enter_auth_key(message: types.Message):
    estimated_auth_key = message.text
    user_id = message.from_user.id
    username = message.from_user.username

    user_account = accounts_base.authorize_user(estimated_auth_key, user_id, username)

    if user_account is None:
        print(f"User {username}[{user_id}] authorization failed")
        await message.reply(f"Что-то пошло не так. Проверьте ключ или запросите новый у администратора")
        return

    print(f"User {username}[{user_id}] successful authorized")
    user_role = user_account.role
    user_default_kb = get_role_keyboard(user_role)
    await get_role_waiting_for_action_state(user_role).set()
    await message.reply(f"Вы успешно авторизованы как {user_account.firstname}", reply_markup=user_default_kb)


# @dp.message_handler(text=botmaster_role_phrase, state=GuestStates.waiting_for_action)
# async def auth_admin(message: types.Message):
    # estimated_auth_key = message.text
    # user_id = message.from_user.id
    # username = message.from_user.username
    # user_firstname = message.from_user.first_name
    # user_lastname = message.from_user.last_name
    # user_role =
    #
    # user_account = accounts_base.reg_user(user_id, Roles.master, username, user_firstname, user_lastname)
    #
    # if user_account is None:
    #     print(f"Registration user {username}[{user_id}] failed")
    #     await message.reply(f"Что-то пошло не так. Зарегестрироваться не удалось")
    #     return
    #
    # print(f"User {username}[{user_id}] registration successful")
    # user_role = role_by_name.get(user_account.role)
    # user_default_kb = get_role_keyboard(user_role)
    # await get_role_waiting_for_action_state(user_role).set()
    # await message.reply(f"Вы успешно зарегестрированы как {Roles.master}", reply_markup=user_default_kb)


@dp.message_handler(state=GuestStates.waiting_for_controlled_key)
async def reg_supervisor(message: types.Message):
    estimated_controlled_key = message.text
    user_id = message.from_user.id
    username = message.from_user.username
    user_firstname = message.from_user.first_name
    user_lastname = message.from_user.last_name

    controlled_user = accounts_base.get_user_by_auth_key(estimated_controlled_key)
    if controlled_user is None:
        await message.answer("Что-то пошло не так. Проверьте корректность ключа")
        return

    if controlled_user.user_id == user_id:
        await message.answer("К сожалению, так не получится")
        return

    if controlled_user.user_id is None:
        await message.answer("Этот пользователь еще не вошел в систему. \n\n Отклонено")
        return

    user_account = accounts_base.reg_user(user_id, Roles.parent, username, user_firstname, user_lastname)

    if user_account is None:
        print(f"Registration user {username}[{user_id}] failed")
        await message.reply(f"Что-то пошло не так. Зарегестрироваться не удалось")
        return

    print(f"User {username}[{user_id}] registration successful")

    accounts_base.set_user_supervisor(controlled_user.user_id, user_account.user_id)

    user_role = user_account.role
    user_default_kb = get_role_keyboard(user_role)
    await get_role_waiting_for_action_state(user_role).set()
    await message.reply(f"Вы успешно зарегестрированы как {user_role}", reply_markup=user_default_kb)

    # roles_list = {'Ученик': "pupil", 'Учитель': "teacher", 'Родитель': "parent",
    #               botmaster_role_phrase: "master", "Староста": "headman"}
    # role = roles_list[message.text]
    # user_id = message.from_user.id
    # if roles_base.get_role(user_id) is None:
    #     username = message.from_user.username
    #     user_fullname = message.from_user.full_name
    #     roles_base.reg_new(user_id, role, username=username, user_fullname=user_fullname)
    # else:
    #     roles_base.change_role(user_id, role)
    #     roles_base.set_teacher_name(user_id, None)
    #     roles_base.set_class_name(user_id, None)
    #
    # if role == "pupil" or role == "parent" or role == "headman":
    #     await message.reply("Введите свой класс", reply_markup=ReplyKeyboardRemove())
    #     await pupil_handler.PupilStates.waiting_for_registration.set()
    # elif role == "teacher":
    #     await teacher_handler.TeacherStates.waiting_for_identifier.set()
    #     await message.reply("Введите ваше имя")
    # elif role == "master":
    #     await master_handler.MasterStates.waiting_for_action.set()
    #     await message.answer("Master role activated", reply_markup=master_kb)
