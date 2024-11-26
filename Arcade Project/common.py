# Some common functionality between different minigames


# Color shortcuts

X = '\x1b[0m' 

def col(i: int) -> str:
    return f'\x1b[1;{i}m'