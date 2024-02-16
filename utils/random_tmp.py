from random import choices
from string import ascii_lowercase

def get_random_tmp_path(suffix: str = ".dot") -> str:
    name = get_random_id(8)
    return "/tmp/" + name + suffix

def get_random_id(length = 10) -> str:
    return ''.join(choices(ascii_lowercase, k=length))