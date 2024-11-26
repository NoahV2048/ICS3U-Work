# Some common functionality between different minigames

X = '\x1b[0m' # color shortcuts
def col(i: int) -> str:
    return f'\x1b[1;{i}m'