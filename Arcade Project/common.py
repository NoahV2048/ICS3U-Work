# Some common functionality between different minigames


# Color Shortcuts

X = '\x1b[0m' 

def col(i: int) -> str:
    return f'\x1b[1;{i}m'


# Utility Shortcuts

def pl(var, es) -> str: # plurality function
    return "es" * (var != 1) if es else "s" * (var != 1)

def cred_msg() -> str: # credit message function
    return f'{col(36)}{creds}{X} credit{pl(creds, 0)}.'

def gs_msg() -> str: # guess message function
    return f'{col(33)}{guesses}{X} incorrect guess{pl(guesses, 1)} remaining.'