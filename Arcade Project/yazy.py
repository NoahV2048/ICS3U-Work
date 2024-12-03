# Yahtzee Game

import random
from common import X, col


# Init

dice_map = ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
dice, kept = [1, 0, 1, 0, 0], [False] * 5

def roll():
    '''Rolls only unkept dice.'''
    for i in range(len((dice))):
        if not kept[i]:
            dice[i] = random.randint(1, 6)
    return dice

def display_dice():
    for i in dice:
        print(dice_map[i], end=' ')

def score_card():
    print()

# Main Game

def play(creds, bet):
    print(f'{col(32)}Playing Yahtzee...\n{X}')



    while True:
        dice = roll()
        display_dice()
        input()

    return creds

play(1, 1)