from aiogram import types
from bot_storage.Keyboards import get_role_keyboard, cancel_kb
from aiogram.dispatcher import FSMContext
from bot_storage.UserStates import GuestStates, get_role_waiting_for_action_state
from bot import dp, bot
from bot_storage.Keyboards import master_kb
from bot_storage import accounts_base
from bot_storage.accounts_base import Roles
from bot_storage.configuration import botmaster_role_phrase


@dp.message_handler(state=GuestStates.waiting_for_action)
async def guest_action(message: types.Message):
    if message.text == "Ввести ключ аутентификации":
        await GuestStates.waiting_for_auth_key.set()
        await message.answer("Введите ваш ключ", reply_markup=cancel_kb)
    elif message.text == "Я родитель":
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
        await message.answer(f"Ваш ключ: {user_account.auth_key}")
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

    if controlled_user.user_id is None:
        await message.answer("Этот пользователь еще не зарегистрировался в системе")
        return

    if controlled_user.user_id == user_id:
        await message.answer("Вы ввели свой ключ. К сожалению, так не получится")
        return

    # reg new user account
    user_account = accounts_base.reg_user(user_id, Roles.parent, username, user_firstname,
                                          user_lastname, controlled_user.sch_identifier)

    if user_account is None:
        print(f"Registration user {username}[{user_id}] failed")
        await message.reply(f"Что-то пошло не так. Зарегестрироваться не удалось")
        return

    print(f"User {username}[{user_id}] registration successful")

    # тут может быть ошибка если сам пользователь не зарегистрировался
    accounts_base.set_user_supervisor(controlled_user.user_id, user_account.user_id)
    # accounts_base.set_user_supervisor_by_auth_key(estimated_controlled_key, user_account.user_id)

    user_role = user_account.role
    user_default_kb = get_role_keyboard(user_role)
    await get_role_waiting_for_action_state(user_role).set()
    await message.reply(f"Вы успешно зарегестрированы как родитель пользователя "
                        f"{controlled_user.firstname or str()} "
                        f"{controlled_user.lastname or str()}",
                        reply_markup=user_default_kb)
    await message.answer(f"Ваш ключ: {user_account.auth_key}")

    await bot.send_message(controlled_user.user_id, f"Уведомление:\n"
                                                    f"Пользователь {user_firstname or str()}"
                                                    f"{user_lastname or str()}"
                                                    f" @{user_account.username} [{user_account.user_id}] "
                                                    f"зарегистрировался как ваш родитель")
