# Level 4+ – Bonus Challenges
# Added pizzazz: random words from an API and definitions from Merriam Webster API
# Noah Verdon
# Last edited: Nov. 18, 2024

import random, requests

# Init
X = '\x1b[0m' # color shortcuts
def col(i: int) -> str:
    return f'\x1b[1;{i}m'

def pl(var, es) -> str: # plurality function
    return "es" * (var != 1) if es else "s" * (var != 1)

def cred_msg() -> str: # credit message function
    return f'{col(36)}{creds}{X} credit{pl(creds, 0)}.'

def gs_msg() -> str: # guess message function
    return f'{col(33)}{guesses}{X} incorrect guess{pl(guesses, 1)} remaining.'

def get_word() -> str: # originally used https://random-word-api.herokuapp.com/home but some words were weird so I used https://random-word-api.vercel.app/
    newword = requests.get(f'https://random-word-api.vercel.app/api?words=1&length={random.randint(3, 9)}&type=uppercase').json()
    return newword[0]

def define(word: str) -> list: # from Merriam-Webster https://dictionaryapi.com/products/api-collegiate-dictionary
    mer_web = requests.get(f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key=0254ad9d-b3b0-4e59-8fc8-1bc436a66edd').json()
    try:
        return mer_web[0]['shortdef'] if mer_web[0]['shortdef'] else ['definition not found'] # some edge cases
    except:
        return ['definition not found']

creds = 500

# ASCII art modified from https://gist.github.com/chrishorton/8510732aa9a80a03c829b09f12e20d9c
hangman_incorrect = [f'''
  +---+
  |   |
  |
  |
  |
  |
=========''', f'''
  +---+
  |   |
  |   {col(31)}O{X}
  |
  |
  |
=========''', f'''
  +---+
  |   |
  |   {col(31)}O{X}
  |   {col(31)}|{X}
  |
  |
=========''', f'''
  +---+
  |   |
  |   {col(31)}O{X}
  |   {col(31)}|\\{X}
  |
  |
=========''', f'''
  +---+
  |   |
  |   {col(31)}O{X}
  |  {col(31)}/|\\{X}
  |
  |
=========''', f'''
  +---+
  |   |
  |   {col(31)}O{X}
  |  {col(31)}/|\\{X}
  |    {col(31)}\\{X}
  |
=========''', f'''
  +---+
  |   |
  |   {col(31)}O{X}
  |  {col(31)}/|\\{X}
  |  {col(31)}/ \\{X}
  |
=========''']

# Main loop
while True:
    # Game init
    word, guesses = get_word(), 6
    letters, incorrect, wrong_words = set(), set(), set()
    inp, bet = '', 0 # unnecessary but colab red underlines are pretty annoying

    while True: # removed flag variables to reduce redundancy
        print(f'You have {cred_msg()} ', end='')
        bet = input('How many would you like to bet? ').strip()
        if bet.isdecimal():
            bet = int(bet)
            if bet == 0:
                print(f'\x1b[31mYou have to bet something!{X}')
            elif not 1 <= bet <= creds:
                print(f'\x1b[31mInsufficient funds.{X}')
            else:
                break
        else:
            print(f'\x1b[31mInvalid bet.{X}')

    print(hangman_incorrect[0])
    print(f'\nGuess the {col(35)}secret word!{X} You have {gs_msg()}')
    print(f'{col(32)}Progress:{X}' + col(34) + ' _' * len(word) + X + '\n')

    # Game loop
    while guesses > 0:
        while True: # removed flag variables to reduce redundancy
            inp = input('Guess a letter (or a 3+ letter word): ').strip().upper()
            if not inp.isalpha() or len(inp) == 2:
                print(f'\x1b[31m"{inp}" is not a valid guess.{X} {gs_msg()}')
            else:
                break

        # Letter response
        if inp in letters or inp in incorrect or inp in wrong_words:
            print(f'\x1b[31mYou have already guessed {inp}.{X} {gs_msg()}')
        else:
            if len(inp) == 1: # guesses updated before hanging
                guesses -= 1 if inp not in word else 0
            else:
                guesses -= 1 if inp != word else 0
            print(hangman_incorrect[6 - guesses]) # print hanging

            if len(inp) == 1: # letter logic
                if inp in word:
                    letters.add(inp)
                    print(f'\n{col(32)}Yes,{X} {col(33)}{inp}{X} was in the word.', end='')
                else:
                    incorrect.add(inp)
                    print(f'\n{col(31)}No,{X} {col(33)}{inp}{X} was not in the word.', end='')
            else: # word logic
                if inp == word:
                    letters = set(word)
                    print(f'\n{col(32)}Yes,{X} {col(33)}{inp}{X} was the word.', end='')
                else:
                    wrong_words.add(inp)
                    print(f'\n{col(31)}No,{X} {col(33)}{inp}{X} was not the word.', end='')

            print(f' {gs_msg()}')
            print(f'{col(32)}Progress: {X}', end='')
            for char in word:
                print(col(32) + char + X, end=' ') if char in letters else print(col(34) + '_' + X, end=' ') # word progress
            print(f'    {col(31)}Incorrect: {X}' * (incorrect != set()) + ' '.join([i for i in incorrect]) + '\n')

            if letters == set(word): # winning
                break

    # Credit management
    if guesses > 0:
        print('Congrats, you guessed the word!')
        creds += bet
        print(f'You won {col(32)}{bet} credit{pl(bet, 0)}.{X} You now have {cred_msg()}\n')
    else:
        print(f'Sorry, you lost the game! The word was {col(33)}{word}.{X}')
        creds -= bet
        print(f'You lost {col(31)}{bet} credit{pl(bet, 0)}.{X} You now have {cred_msg()}\n')

    # Definition
    def_list = define(word)
    print(f'Definition(s) of {col(33)}"{word.lower()}"{X}:')
    for i, deff in enumerate(def_list, start=1):
        print(f'    {i}. {deff}')
    print()

    # Replay
    if creds == 0:
        print(col(31) + 'You ran out of credits. Game over!' + X)
        break
    else:
        replay = ''
        while replay not in ('y', 'n'):
            print(f'Would you like to play again ({col(32)}Y{X}/{col(31)}N{X})? ', end='')
            replay = input().strip().lower()
        print()
        if replay == 'n':
            break

# End
print(f'{col(32)}Thanks for playing!{X} Your final balance is {cred_msg()}')