from aiogram import types
from bot_storage.UserStates import MasterStates
from bot import dp
from bot_storage import bot_stats, accounts_base
from bot_storage.Keyboards import cancel_kb
from actions import update_global_rasp, broadcast_action, upload_account_base, upload_food_menu_action
from actions.pupils_rasp import make_pupil_rasp_request
from actions.teachers_rasp import make_teacher_rasp_request
from bot_storage import UserStates
from bot_storage.Keyboards import guest_kb


# TODO сделать валидацию доступа декоратором
# TODO загрузка базы аккаунтов - предоставляются firstname, lastname, role, sch_identifier. Далее смотреть accounts_db
# TODO add system_funcs: refresh key, unlink account, prereg new user, upload accounts base
from bot_storage.accounts_base import Roles


def validate_master_command(cmd_description: str):
    def decorator(func):
        async def wrapper(message: types.Message):
            print(cmd_description)
            if not await validate_master(message):
                return
            func()
        return wrapper
    return decorator


async def validate_master(message: types.Message) -> bool:
    user_id = message.from_user.id
    user_name = message.from_user.username
    user_full_name = message.from_user.full_name
    if accounts_base.get_role(user_id) == Roles.master:
        print(f"master role validated for user {user_name}[{user_id}] ({user_full_name})")
        return True
    else:
        print(f"master role for user {user_name}[{user_id}] ({user_full_name}) NOT VALIDATED")
        await message.answer("Выберие свою роль", reply_markup=guest_kb)
        await UserStates.GuestStates.waiting_for_action.set()
        return False


@dp.message_handler(lambda m: any(word in m.text for word in ["Статистика", "стат", "Стат", "stat"]),
                    state=MasterStates.waiting_for_action)
async def stats(message: types.Message):
    print("show statistics to master")
    if not await validate_master(message):
        return

    replying_for = message.reply_to_message
    usage_stats_by_class = ""
    if replying_for is None:
        usage_stats_by_class = bot_stats.get_stats(bot_stats.StatsType.ByClass)
    else:
        new_stats_by_class = bot_stats.parse_stat_by_class(bot_stats.get_stats(bot_stats.StatsType.ByClass))
        old_stats_by_class = bot_stats.parse_stat_by_class(replying_for.text)

        for class_name, stat_count in new_stats_by_class.items():
            if class_name not in old_stats_by_class.keys():
                continue
            usage_stats_by_class += f"{bot_stats.by_class_prefix} {class_name} =" \
                                    f" {new_stats_by_class[class_name] - old_stats_by_class[class_name]}\n"

    usage_stats_general = bot_stats.get_stats(bot_stats.StatsType.General)
    await message.answer(usage_stats_general + "\n" + usage_stats_by_class)


@dp.message_handler(lambda m: m.text == "Рассылка", state=MasterStates.waiting_for_action)
async def broadcast(message: types.Message):
    print("broadcast by master")
    if not await validate_master(message):
        return

    await broadcast_action.make_broadcast(message)


@dp.message_handler(lambda m: m.text == "Расписание школьников", state=MasterStates.waiting_for_action)
async def pupils_rasp(message: types.Message):
    print("pupils rasp by master")
    if not await validate_master(message):
        return

    await make_pupil_rasp_request(message)


@dp.message_handler(lambda m: m.text == "Расписание учителей", state=MasterStates.waiting_for_action)
async def teachers_rasp(message: types.Message):
    print("teachers rasp by master")
    if not await validate_master(message):
        return

    await make_teacher_rasp_request(message)


@dp.message_handler(lambda m: m.text == "Загрузить расписание", state=MasterStates.waiting_for_action)
async def upload_rasp(message: types.Message):
    print("master upload new rasp_table")
    if not await validate_master(message):
        return

    await message.answer("Пришлите мне xlsx файл с расписанием", reply_markup=cancel_kb)
    await update_global_rasp.make_global_rasp_update()


@dp.message_handler(lambda m: m.text == "Загрузить базу аккаунтов", state=MasterStates.waiting_for_action)
async def upload_rasp(message: types.Message):
    print("master upload new rasp_table")
    if not await validate_master(message):
        return

    await message.answer("Пришлите мне список аккаунтов в формате csv", reply_markup=cancel_kb)
    await upload_account_base.make_accounts_upload()


@dp.message_handler(lambda m: m.text == "Загрузить меню", state=MasterStates.waiting_for_action)
async def upload_food_menu(message: types.Message):
    print("master upload food menu")
    if not await validate_master(message):
        return

    await message.answer("Пришлите новое меню в формате csv", reply_markup=cancel_kb)
    await upload_food_menu_action.make_food_menu_upload()
