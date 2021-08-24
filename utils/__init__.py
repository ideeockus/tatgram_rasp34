import string
import random


def progress_bar(percents: int, bar_max_width=10) -> str:
    filled_part = percents//bar_max_width
    empty_part = bar_max_width - filled_part
    return "[" + '#'*filled_part + '  '*empty_part + "]"


def gen_random_string(length: int) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))
