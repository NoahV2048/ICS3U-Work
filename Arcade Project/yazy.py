# Yahtzee Game
# Recreation of Yahtzee gameplay for a single player
# Noah Verdon
# Last edited: Dec. 6, 2024

# Scores based on "2 Player Games" simplified Yahtzee scorecard (called "Yazy")
# https://apps.apple.com/us/app/2-player-games-the-challenge/id1465731199

import random, time
from common import X, col, pl, border


# Init

dice_map = ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
quick_keys = ['1', '2', '3', '4', '5', '6', '3_kind', '4_kind', 'house', 'straight', 'yazy']

def roll_animate() -> None:
    '''Plays a snazzy sequence.'''
    print(f'{col(33)}Rolling', end='')
    for _ in range(3):
        time.sleep(0.35)
        print('.', end='')
    time.sleep(0.35)
    print(X + '\n')

def roll(dice: list, kept: list) -> list:
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
            scores.append(col(35) + str(scorecard[str(i)]) + X)
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
            scores.append(col(35) + str(scorecard[str(n) + '_kind']) + X)
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
        scores.append(col(35) + str(scorecard['house']) + X)
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
        scores.append(col(35) + str(scorecard['straight']) + X)
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
        scores.append(col(35) + str(scorecard['yazy']) + X)
        score_ints.append(scorecard['yazy'])

    return scores, score_ints

def print_scorecard(scores: list, current_score: int, available: list) -> None:
    '''Displays current scorecard to user.'''

    print(f'''╔═════════════════╦═════════╗
║    {col(33)}SCORECARD{X}    ║ {col(33)}INDEXES{X} ║
╟────────────┬────╫─────────╢
║ \x1b[33m{'Total ' + dice_map[1]:10}{X} │ {scores[0]:>13} ║   {col(34)}#1{X}    ║
║ \x1b[33m{'Total ' + dice_map[2]:10}{X} │ {scores[1]:>13} ║   {col(34)}#2{X}    ║
║ \x1b[33m{'Total ' + dice_map[3]:10}{X} │ {scores[2]:>13} ║   {col(34)}#3{X}    ║
║ \x1b[33m{'Total ' + dice_map[4]:10}{X} │ {scores[3]:>13} ║   {col(34)}#4{X}    ║
║ \x1b[33m{'Total ' + dice_map[5]:10}{X} │ {scores[4]:>13} ║   {col(34)}#5{X}    ║
║ \x1b[33m{'Total ' + dice_map[6]:10}{X} │ {scores[5]:>13} ║   {col(34)}#6{X}    ║
║ \x1b[33m{'◼ ◼ ◼':10}{X} │ {scores[6]:>13} ║   {col(34)}#7{X}    ║
║ \x1b[33m{'◉ ◉ ◉ ◉ ':10}{X} │ {scores[7]:>13} ║   {col(34)}#8{X}    ║
║ \x1b[33m{'⯁ ⯁ ⯁ ◉ ◉':10}{X} │ {scores[8]:>13} ║   {col(34)}#9{X}    ║
║ \x1b[33m{'◼ ⯁ ◉ ⯅ ★':10}{X} │ {scores[9]:>13} ║   {col(34)}#10{X}   ║
║ \x1b[33m{'★ ★ ★ ★ ★':10}{X} │ {scores[10]:>13} ║   {col(34)}#11{X}   ║
╟────────────┴────╫─────────╢
║ {col(33)}YOUR SCORE: {col(35)}{current_score:>3}{X} ║ {col(33)}LEFT:{col(34)}{available.count(True):2}{X} ║
╚═════════════════╩═════════╝\n''')

def cycle(scorecard):
    '''A single iteration that updates the scorecard.'''
    dice, kept, rolls = [0, 0, 0, 0, 0], [False] * 5, 3

    input('Ready to roll the dice? Press enter: ')
    dice = roll(dice, kept)
    rolls -= 1

    while True:
        scores, score_ints = score_list(dice, scorecard)

        current_score, available = 0, []
        for val in scorecard.values():
            if val != None:
                current_score += val
                available.append(False)
            else:
                available.append(True)

        print_scorecard(scores, current_score, available)
        display_dice(dice, kept)

        print(f'Select {col(33)}A{X} to {col(33)}E{X} to keep dice for your next roll.')
        print(f'Select an {col(34)}available{X} index from {col(34)}1{X} to {col(34)}11{X} to choose a scoring category.')
        print(f'Select {col(31)}"R"{X} to reroll your {col(31)}unkept dice{X} {col(33)}({rolls} roll{pl(rolls, 0)} remaining).{X}')
        print(f'Picking an {col(34)}index{X} will {col(32)}progress{X} the game.')
        inp = input('Your choice: ').upper().strip()
        print()

        if inp in ['A', 'B', 'C', 'D', 'E', 'R'] or inp in list(map(str, range(1, 12))):
            if inp == 'R':
                if rolls > 0:
                    dice = roll(dice, kept)
                    rolls -= 1
            elif inp.isalpha():
                kept[['A', 'B', 'C', 'D', 'E'].index(inp)] = not kept[['A', 'B', 'C', 'D', 'E'].index(inp)]
            else:
                inp = int(inp) - 1
                if available[inp]:
                    scorecard[quick_keys[inp]] = score_ints[inp]
                    print(f'You selected {col(34)}#{inp + 1}{X} and gained {col(32)}{score_ints[inp]}{X} point{pl(score_ints[inp], 0)}.')
                    break
    
    return scorecard


# Main Game

def play(bet: int, dice_setting: bool) -> tuple[int, int, bool]:
    border('YAHTZEE', 32)

    global dice_map
    if not dice_setting:
        dice_map = list(map(str, range(7)))

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

    yazy_score = sum(scorecard.values())
    result = yazy_score // 100 * bet

    yazy_bool = False
    if scorecard['yazy'] == 50: # yahtzee bonus seems natural
        result += bet
        yazy_bool = True

    print(f'You gained {col(32)}{result:,}{X} credit{pl(result, 0)}, with {col(35)}{yazy_score}{X} point{pl(yazy_score, 0)}.')
    if yazy_score < 100:
        print('Do better next time!')
    elif 100 <= yazy_score < 200:
        print('Prety good game!')
    else:
        print('Amazing score!')

    if scorecard['yazy'] == 50:
        print('(+100% bet bonus for a Yahtzee)')

    print()
    return result, yazy_score, yazy_bool