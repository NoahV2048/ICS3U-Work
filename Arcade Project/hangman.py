# Hangman Game
# Simple word guessing game
# Noah Verdon
# Last edited: Dec. 6, 2024

import random, requests, time as t
from common import X, col, gs_msg, border


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

def get_word() -> str:
    '''From https://random-word-api.vercel.app/'''
    newword = requests.get(f'https://random-word-api.vercel.app/api?words=1&length={random.randint(3, 9)}&type=uppercase').json()
    return newword[0]

def define(word: str) -> list:
    '''From Merriam-Webster: https://dictionaryapi.com/products/api-collegiate-dictionary'''
    mer_web = requests.get(f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key=0254ad9d-b3b0-4e59-8fc8-1bc436a66edd').json()
    try:
        return mer_web[0]['shortdef'] if mer_web[0]['shortdef'] else ['definition not found'] # some edge cases
    except:
        return ['definition not found']

def get_guess(guesses: int) -> str:
    '''Gets a letter or a 3+ letter word as input.'''
    while True:
        inp = input('Guess a letter (or a 3+ letter word): ').strip().upper()
        if not inp.isalpha() or len(inp) == 2:
            print(f'\x1b[31m"{inp}" is not a valid guess.{X} {gs_msg(guesses)}')
        else:
            return inp

def input_response(inp: str, word: str, guesses: int, letters: set, incorrect: set, wrong_words: set) -> tuple[set, set, set]:

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
    
    print(f' {gs_msg(guesses)}')

    return letters, incorrect, wrong_words
    

def display_progress(word: str, letters: set, incorrect: set) -> None:
    print(f'{col(32)}Progress: {X}', end='')
    for char in word:
        print(col(32) + char + X, end=' ') if char in letters else print(col(34) + '_' + X, end=' ') # word progress
    print(f'    {col(31)}Incorrect: {X}' * (incorrect != set()) + ' '.join([i for i in incorrect]) + '\n')


# Main Game

def play(bet: int) -> int:
    '''Plays Hangman.'''
    border('HANGMAN', 32)

    # Game init
    word, guesses = get_word(), 6
    letters, incorrect, wrong_words = set(), set(), set()

    print(f'Guess the {col(35)}secret word!{X} You have {gs_msg(guesses)}')
    t.sleep(0.5)
    print(hangman_incorrect[0])
    print(f'\n{col(32)}Progress:{X}' + col(34) + ' _' * len(word) + X + '\n')

    # Game loop
    while guesses > 0:
        inp = get_guess(guesses)

        if inp in letters or inp in incorrect or inp in wrong_words:
            print(f'\x1b[31mYou have already guessed {inp}.{X} {gs_msg(guesses)}')
        else:
            if len(inp) == 1: # guesses updated before hanging
                guesses -= 1 if inp not in word else 0
            else:
                guesses -= 1 if inp != word else 0
            print(hangman_incorrect[6 - guesses]) # print hanging

            letters, incorrect, wrong_words = input_response(inp, word, guesses, letters, incorrect, wrong_words)
            display_progress(word, letters, incorrect)

            if letters == set(word): # winning
                break

    # Credit management
    if guesses > 0:
        print('Congrats, you guessed the word!\n')
        result = bet
    else:
        print(f'Sorry, you lost the game! The word was {col(33)}{word}.{X}\n')
        result = -bet

    # Definition
    def_list = define(word)

    print(f'{col(32)}Definition(s){X} of {col(33)}"{word.lower()}"{X}:')
    for i, definition in enumerate(def_list, start=1):
        print(f'{i}. {definition.capitalize()}.')
    print()

    return result