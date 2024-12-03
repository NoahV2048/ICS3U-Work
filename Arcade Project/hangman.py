# Hangman Game

import random, requests
from common import X, col, pl, cred_msg, gs_msg


# Init

hangman_incorrect = [f'''
  ╭───╮
  │   ┆
  │
  │
  │
  │
══╧══════''', f'''
  ╭───╮
  │   ┆
  │   {col(31)}O{X}
  │
  │
  │
══╧══════''', f'''
  ╭───╮
  │   ┆
  │   {col(31)}O{X}
  │   {col(31)}|{X}
  │
  │
══╧══════''', f'''
  ╭───╮
  │   ┆
  │   {col(31)}O{X}
  │   {col(31)}|\\{X}
  │
  │
══╧══════''', f'''
  ╭───╮
  │   ┆
  │   {col(31)}O{X}
  │  {col(31)}/|\\{X}
  │
  │
══╧══════''', f'''
  ╭───╮
  │   ┆
  │   {col(31)}O{X}
  │  {col(31)}/|\\{X}
  │    {col(31)}\\{X}
  │
══╧══════''', f'''
  ╭───╮
  │   ┆
  │   {col(31)}O{X}
  │  {col(31)}/|\\{X}
  │  {col(31)}/ \\{X}
  │
══╧══════''']

def get_word() -> str: # originally used https://random-word-api.herokuapp.com/home but some words were weird so I used https://random-word-api.vercel.app/
    newword = requests.get(f'https://random-word-api.vercel.app/api?words=1&length={random.randint(3, 9)}&type=uppercase').json()
    return newword[0]

def define(word: str) -> list: # from Merriam-Webster https://dictionaryapi.com/products/api-collegiate-dictionary
    mer_web = requests.get(f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key=0254ad9d-b3b0-4e59-8fc8-1bc436a66edd').json()
    try:
        return mer_web[0]['shortdef'] if mer_web[0]['shortdef'] else ['definition not found'] # some edge cases
    except:
        return ['definition not found']

def get_guess():
    while True:
        inp = input('Guess a letter (or a 3+ letter word): ').strip().upper()
        if not inp.isalpha() or len(inp) == 2:
            print(f'\x1b[31m"{inp}" is not a valid guess.{X} {gs_msg()}')
        else:
            return inp

def letter_response():
    pass

# Main loop
def play(creds, bet):
    print(f'{col(32)}Playing Hangman...{X}')

    # Game init
    word, guesses = get_word(), 6
    letters, incorrect, wrong_words = set(), set(), set()

    print(hangman_incorrect[0])
    print(f'\nGuess the {col(35)}secret word!{X} You have {gs_msg()}')
    print(f'{col(32)}Progress:{X}' + col(34) + ' _' * len(word) + X + '\n')

    # Game loop
    while guesses > 0:
        inp = get_guess()

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

    return creds