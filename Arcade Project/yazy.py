# Yahtzee Game
# Recreation of Yahtzee gameplay for a single player
# Noah Verdon
# Last edited: Dec. 4, 2024

import random
from common import X, col, border


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

def play(bet):
    border('YAHTZEE', 32)



    while True:
        dice = roll()
        display_dice()
        input()

    return result