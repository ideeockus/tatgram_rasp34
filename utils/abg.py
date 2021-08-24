import re
from aiogram.dispatcher import FSMContext
from aiogram import types
from actions.notify_admins import notify_admins
from bot_storage.roles_base import get_role, get_class_name, get_teacher_name


def md_format(md_text: str) -> str:
    # return re.sub(r"\\[^~*_\\`]", "", md_text)
    return re.sub(r"\\([^`*_\\])", r"\1", md_text)


def md_shielding(md_text: str) -> str:
    return md_text.replace("*", "\\*").replace("`", "\\`").replace("_", "\\_").replace("~", "\\_")


async def abg_lost_role(message: types.Message, state: FSMContext):
    # await unregistered_msg(message, state)
    state_data = await state.get_data()
    # await state.finish()

    user_id = message.from_user.id
    user_name = message.from_user.username
    message_text = message.text

    potentially_teacher_name = get_teacher_name(user_id)
    potentially_class_name = get_class_name(user_id)
    db_role = get_role(user_id)

    abg_info_text = f"От пользователя {user_name}[{user_id}] поступило сообщение, " \
                    f"но данных для идентификации недостаточно.\n" \
                    f"В базе данных имеется следующие данные:\n" \
                    f"role: {db_role}\n" \
                    f"teacher_name: {potentially_teacher_name}\n" \
                    f"class_name: {potentially_class_name}\n\n" \
                    f"Пользователю будет предложено зарегестрироваться заново"
    print(abg_info_text)
    print(f"Его сообщение: {message_text}")
    print(f"Его параметры: {state_data}")
    await notify_admins(abg_info_text)

    # reregistration user
    # await message.answer("Упс, я забыл кто вы")
    # await message.answer("Пожалуйста, выберите свою роль", reply_markup=choose_role_kb)
    # await MainStates.wait_for_role.set()

