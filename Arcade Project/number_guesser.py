# Number Guesser
# Simple binary search game
# Noah Verdon
# Last edited: Dec. 4, 2024

import random as r, math as m
from common import X, col, gs_msg, border, yn_validate


# Init

bar = [f'{col(32)}■'] * 3 + [f'{col(33)}■'] * 3 + [f'{col(31)}■'] * 3 # difficulty bar

def mod_log(low: int, upp: int) -> str:
    '''Returns a logarithm before modulo operation.'''
    return m.floor(m.log2(upp - low + 1) * 10)

def get_guess(low: int, upp: int, guesses: int) -> int:
    '''Guess validation loop.'''
    while True:
        guess = input('Enter a number: ')
        if not guess.isdecimal():
            print(f'Invalid guess (not an integer >= 0). You have {gs_msg(guesses)}')
        elif not low <= (guess := int(guess)) <= upp:
            print(f'Invalid guess (not in range). You have {gs_msg(guesses)}')
        else:
            break
    return guess

def handle_guess(guess: int, guesses: int, rand: int, bet: int) -> tuple[bool, int]:
    '''Returns if the game has concluded and the alteration to credits if applicable.'''
    finished, result = False, 0

    if guess < rand:
        print(f'Too {col(31)}low!{X} You have {gs_msg(guesses)}')
    elif guess > rand:
        print(f'Too {col(32)}high!{X} You have {gs_msg(guesses)}')

    else: # winning logic
        multiplier = bet * (guesses + 1)
        print(f'\nYou guessed the number, {col(95)}{rand},{X} with a multiplier of {col(33)}{guesses + 1}.{X}')
        return True, multiplier

    if guesses == 0: # losing logic
        print(f'\nOh no, you lost the game! The correct number was {col(95)}{rand}.{X}')
        return True, -bet

    return finished, result

def get_numbers() -> tuple[int, int]:
    '''Number range configuration.'''

    while True:
        while True: # establish lower bound
            low = input("What's your lucky number (lower bound)? ")
            if not low.isdecimal():
                print(f'Invalid value (not an integer >= 0).')
            else:
                low = int(low)
                break

        while True: # establish upper bound
            upp = input("What's your other lucky number (upper bound)? ")
            if not upp.isdecimal():
                print(f'Invalid value (not an integer >= 0).')
            elif not low + 9 <= int(upp):
                print(f'Invalid value (must be >= low + 9).')
            else:
                upp = int(upp)
                break

        difficulty = mod_log(low, upp) % 10
        print(f'Difficulty: {(X, col(32), col(33), col(31))[m.ceil(difficulty / 3)]}{difficulty + 1}{X}/10')

        for i in range(difficulty): # print difficulty bar
            print(bar[i], end='')
        print(X + '■' * (9 - difficulty) + '\n')

        if yn_validate('Keep these numbers (y/n)? '): # reconfig validation loop
            break
        else:
            print()

    print(f"{col(31)}\nYour numbers have been saved!{X}\n")
    return low, upp


# Main Game

def play(bet, low, upp):
    '''Plays Number Guesser.'''
    border('NUMBER GUESSER', 32)

    rand = r.randint(low, upp)
    guesses = mod_log(low, upp) // 10 # guesses -> # of times you can effectively halve the range

    print(f'Guess a random number between {col(95)}{low:,}{X} and {col(95)}{upp:,}{X}. \
You have {gs_msg(guesses)}\n')

    # Guess loop
    while True:
        guess = get_guess(low, upp, guesses)
        guesses -= 1

        finished, result = handle_guess(guess, guesses, rand, bet)

        if finished:
            break

    return result