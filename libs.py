from enum import Enum


class Roles(Enum):
    teacher = "Учитель"
    pupil = "Ученик"
    headman = "Староста"
    parent = "Родитель"
    master = "Админ"
    guest = "Гость"


role_by_name = {
    'teacher': Roles.teacher,
    'pupil': Roles.pupil,
    'headman': Roles.headman,
    'parent': Roles.parent,
    'master': Roles.master
}
