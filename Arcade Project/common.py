# Shared Functions
# Some common functionality between different minigames
# Noah Verdon
# Last edited: Dec. 4, 2024

import time as t


# Color Shortcuts

X = '\x1b[0m' 

def col(color: int) -> str:
    return f'\x1b[1;{color}m'


# Utility Shortcuts

def pl(variable: int, es: bool) -> str:
    '''Plurality function.'''
    return "es" * (variable != 1) if es else "s" * (variable != 1)

def cred_msg(creds: int) -> str: # credit message function
    return f'{col(36)}{creds:,}{X} credit{pl(creds, False)}.'

def gs_msg(guesses: int) -> str: # guess message function
    return f'{col(33)}{guesses}{X} incorrect guess{pl(guesses, True)} remaining.'

def border(msg: str, color: int) -> None:
    print(col(33) + '╔' + '═' * len(msg) + '╗')
    print(f'║{col(color)}{msg}{col(33)}║')
    print(col(33) + '╚' + '═' * len(msg) + '╝' + X + '\n')
    t.sleep(0.5)

def yn_validate(msg: str):
    '''Validate yes or no inputs.'''
    yn = None

    while yn not in ('y', 'n'):
        yn = input(msg).strip().lower()
    return ('n', 'y').index(yn)