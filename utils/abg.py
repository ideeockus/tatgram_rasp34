import re


def md_format(md_text: str) -> str:
    # return re.sub(r"\\[^~*_\\`]", "", md_text)
    return re.sub(r"\\([^`*_\\])", r"\1", md_text)


def md_shielding(md_text: str) -> str:
    return md_text.replace("*", "\\*").replace("`", "\\`").replace("_", "\\_").replace("~", "\\_")

