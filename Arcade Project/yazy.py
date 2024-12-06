# Yahtzee Game
# Recreation of Yahtzee gameplay for a single player
# Noah Verdon
# Last edited: Dec. 5, 2024

# Scores based on "2 Player Games" simplified Yahtzee scorecard (called "Yazy")
# https://apps.apple.com/us/app/2-player-games-the-challenge/id1465731199

import random, time
from common import X, col, border


# Init

dice_map = ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅']

def roll_animate():
    '''Plays a snazzy sequence.'''
    print(f'{col(33)}Rolling', end='')
    for _ in range(3):
        time.sleep(0.35)
        print('.', end='')
    time.sleep(0.35)
    print(X + '\n')

def roll(dice, kept):
    '''Rolls only unkept dice.'''
    roll_animate()

    for i in range(5):
        if not kept[i]:
            dice[i] = random.randint(1, 6)
    return dice

def display_dice(dice: list[int], kept: list[bool]) -> None:
    '''Gives user roll information.'''
    for n, letter in enumerate(['A', 'B', 'C', 'D', 'E']):
        print(col(32) + letter + X, end=' ') if kept[n] else print(col(31) + letter + X, end=' ')
    print()

    for i in dice:
        print(dice_map[i], end=' ')
    print('\n')

def score_list(dice: list, scorecard: dict) -> tuple[list, list]:
    '''Lengthy function calculating various scoring options.'''
    scores, score_ints = [], []
    check = [dice.count(i) for i in range(1, 7)]

    # Multiples of a certain number
    for i in range(1, 7):
        if scorecard[str(i)] == None:
            scores.append(col(32) + str(dice.count(i) * i) + X)
            score_ints.append(dice.count(i) * i)
        else:
            scores.append(col(34) + str(scorecard[str(i)]) + X)
            score_ints.append(scorecard[str(i)])
    
    # Three and four of a kind
    for n in [3, 4]:
        if scorecard[str(n) + '_kind'] == None:
            if max(check) >= n:
                scores.append(col(32) + str(sum(dice)) + X)
                score_ints.append(sum(dice))
            else:
                scores.append(col(32) + '0' + X)
                score_ints.append(0)
        else:
            scores.append(col(34) + str(scorecard[str(n) + '_kind']) + X)
            score_ints.append(scorecard[str(n) + '_kind'])
    
    # Full House
    if scorecard['house'] == None:
        if 2 in check and 3 in check:
            scores.append(col(32) + '25' + X)
            score_ints.append(25)
        else:
            scores.append(col(32) + '0' + X)
            score_ints.append(0)
    else:
        scores.append(col(34) + str(scorecard['house']) + X)
        score_ints.append(scorecard['house'])

    # Straight
    if scorecard['straight'] == None:
        if set(dice) in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}):
            scores.append(col(32) + '40' + X)
            score_ints.append(40)
        else:
            scores.append(col(32) + '0' + X)
            score_ints.append(0)
    else:
        scores.append(col(34) + scorecard['straight'] + X)
        score_ints.append(scorecard['straight'])
    
    # Yahtzee
    if scorecard['yazy'] == None:
        if max(check) == 5:
            scores.append(col(32) + '50' + X)
            score_ints.append(50)
        else:
            scores.append(col(32) + '0' + X)
            score_ints.append(0)
    else:
        scores.append(col(34) + str(scorecard['yazy']) + X)
        score_ints.append(scorecard['yazy'])

    return scores, score_ints

def print_scorecard(scores: list, score_ints: list, current_score: int) -> None:
    '''Displays current scorecard to user.'''

    print(f'''╔═════════════════╗
║    {col(33)}SCORECARD{X}    ║
╟────────────┬────╢
║ \x1b[33m{'Total ' + dice_map[1]:10}{X} │ {scores[0]:13} ║
║ \x1b[33m{'Total ' + dice_map[2]:10}{X} │ {scores[1]:13} ║
║ \x1b[33m{'Total ' + dice_map[3]:10}{X} │ {scores[2]:13} ║
║ \x1b[33m{'Total ' + dice_map[4]:10}{X} │ {scores[3]:13} ║
║ \x1b[33m{'Total ' + dice_map[5]:10}{X} │ {scores[4]:13} ║
║ \x1b[33m{'Total ' + dice_map[6]:10}{X} │ {scores[5]:13} ║
║ \x1b[33m{'◼ ◼ ◼':10}{X} │ {scores[6]:13} ║
║ \x1b[33m{'◉ ◉ ◉ ◉ ':10}{X} │ {scores[7]:13} ║
║ \x1b[33m{'⯁ ⯁ ⯁ ◉ ◉':10}{X} │ {scores[8]:13} ║
║ \x1b[33m{'◼ ⯁ ◉ ⯅ ★':10}{X} │ {scores[9]:13} ║
║ \x1b[33m{'★ ★ ★ ★ ★':10}{X} │ {scores[10]:13} ║
╟────────────┴────╢
║ {col(33)}YOUR SCORE:{col(32)} {current_score:3}{X} ║
╚═════════════════╝\n''')

def cycle(scorecard):
    '''A single iteration that updates the scorecard.'''
    dice, kept = [0, 0, 0, 0, 0], [False] * 5

    input('Ready to roll the dice? Press enter: ')
    dice = roll(dice, kept)

    while True:
        scores, score_ints = score_list(dice, scorecard)

        current_score = 0
        for val in scorecard.values():
            if val != None:
                current_score += scorecard[val]

        print_scorecard(scores, score_ints, current_score)
        display_dice(dice, kept)

        print('Select A to E to keep dice for your next roll.')
        print('Select a number from 1 to 11 to gain points. (or smth)')
        input('Enter "R" to reroll with your kept dice.')

    
# Main Game

def play(bet):
    border('YAHTZEE', 32)

    scorecard = { # initialize scorecard
    '1': None, # could use a list but dict is easier to visualize
    '2': None,
    '3': None,
    '4': None,
    '5': None,
    '6': None,
    '3_kind': None,
    '4_kind': None,
    'house': None,
    'straight': None,
    'yazy': None
}

    while None in scorecard.values():
        scorecard = cycle(scorecard)

    # lowest possible score is 0; highest possible score is 280
    # return value is the score // 100 * bet
    # the user isn't playing against an opponent so it isn't a win-lose scenario

    result = sum(scorecard.values()) // 100 * bet
    return result

play(1)