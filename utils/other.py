def progress_bar(percents: int, bar_max_width=10) -> str:
    filled_part = percents//bar_max_width
    empty_part = bar_max_width - filled_part
    return "[" + '#'*filled_part + '  '*empty_part + "]"
