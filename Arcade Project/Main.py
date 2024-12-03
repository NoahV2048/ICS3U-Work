# Arcade
# Allows user to play 3 different minigames
# Noah Verdon
# Last edited: Dec. 3, 2024

import time as t
import numberGuesser, hangman, yazy
from common import X, col, cred_msg, border


# Welcome & Init

border('WELCOME TO THE ARCADE!', 31)
creds = 1000
c = creds
games = ['Number Guesser', 'Hangman', 'Yahtzee', 'Settings', 'Quit']

class Game_stats: # stats unique to each game
    def __init__(self):
        self.won, self.lost = 0, 0

min_creds, max_creds = 500, 500 # global stats
num_stats, hang_stats, yazy_stats = (Game_stats(),) * 3
short_games = [num_stats, hang_stats, yazy_stats]


# Establish Functions

def game_select() -> int:
    '''Game selection.'''
    print(f'{col(32)}Game Selection:{X}')
    for i, item in enumerate(games, start=1):
        print(f'{i}. {item}')
    print()
    t.sleep(0.25)
    while True:
        game = input('Which game would you like to play? ')
        if game.isdecimal():
            if 1 <= (game := int(game)) <= 5:
                break
    return game - 1

def get_bet():
    '''Bet validation loop.'''
    while True:
        print(f'You have {cred_msg(c)} ', end='')
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
    
    if bet == creds: # all in
        print(f"{col(31)}Woah, you're all in!{X}")
    return bet

def game_stats(i):
    '''Print game-specific stats.'''
    stats = short_games[i]
    print(f'''{col(36)}{games[i]}:{X}
Rounds Played: {col(33)}{(total := stats.won + stats.lost)}{X}
Wins-Losses: {col(32)}{stats.won}{X}-{col(31)}{stats.lost}{X}''')

    if total == 0:
        print(f'Win Rate: {col(33)}No percentage available{X}\n')
    else:
        print(f'Win Rate: {col(33)}{100 * stats.won / (total):.1f}%{X}\n')

def yn_validate(msg: str):
    '''Validate yes or no inputs.'''
    yn = None
    while yn not in ('y', 'n'):
        yn = input(msg).strip().lower()
    return ('n', 'y').index(yn)

def settings():
    pass


# Main Loop

t.sleep(0.5)
while True:
    game = game_select()
    
    if game == 4:
        print('You selected: Quit\n')
        break
    elif game == 3:
        print('You selected: Settings\n')
        settings()
        continue

    print(f'You have chosen {col(33)}{games[game]}.{X}\n')
    bet = get_bet()

    creds = [numberGuesser, hangman][game].play(creds, bet)

    if creds > max_creds: # for stats
        max_creds = creds
    elif creds < min_creds:
        min_creds = creds

    # Replay
    if creds > 0:
        print(f'You have {cred_msg(c)}')
        rep = yn_validate('Would you like to play again (y/n)? ')
        if rep:
            print()
        else:
            break

    else: # game over perhaps
        print(f'{col(31)}Sorry, you ran out of credits!{X}')
        one_cred = yn_validate('Okay, would you like 1 credit to keep going (y/n)? ')

        if one_cred:
            creds = 1
            print()
        else:
            break


# End & Stats

print(f'{col(32)}Thank you for playing!{X}')
print(f'Your final balance is {cred_msg(c)}\n')
t.sleep(0.75)
border('ARCADE STATS', 36)
t.sleep(0.5)

print(f'''{col(36)}Global:{X}
Max Credits: {col(32)}{max_creds:,}{X}
Min Credits: {col(31)}{min_creds:,}{X}\n''')
t.sleep(0.25)

for i in range(3):
    game_stats(i)
    t.sleep(0.25)

border('COME BACK SOON!', 31)