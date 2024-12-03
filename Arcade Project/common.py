# Some common functionality between different minigames


# Color Shortcuts

X = '\x1b[0m' 

def col(i: int) -> str:
    return f'\x1b[1;{i}m'


# Utility Shortcuts

def pl(var, es) -> str: # plurality function
    return "es" * (var != 1) if es else "s" * (var != 1)

def cred_msg(creds) -> str: # credit message function
    return f'{col(36)}{creds:,}{X} credit{pl(creds, 0)}.'

def gs_msg(guesses) -> str: # guess message function
    return f'{col(33)}{guesses}{X} incorrect guess{pl(guesses, 1)} remaining.'

def border(msg, c) -> None:
    print(col(33) + '╔' + '═' * len(msg) + '╗')
    print(f'║{col(c)}{msg}{col(33)}║')
    print(col(33) + '╚' + '═' * len(msg) + '╝' + X + '\n')