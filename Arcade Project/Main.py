# Arcade
# Allows user to play 3 different minigames
# Noah Verdon
# Last edited: Dec. 6, 2024

import time as t
import number_guesser, hangman, yazy
from common import X, col, pl, cred_msg, border, yn_validate


# Welcome & Init

border('WELCOME TO THE ARCADE!', 31)
creds = 1000
num_guess_lower, num_guess_upper, dice_setting = 0, 0, True
games = ['Number Guesser', 'Hangman', 'Yahtzee', 'Settings', 'Quit']

class Game_Stats: # stats unique to each game
    def __init__(self):
        self.won, self.lost, self.max_score = 0, 0, 0

min_creds, max_creds = (creds,) * 2 # global stats
num_stats, hang_stats, yazy_stats = Game_Stats(), Game_Stats(), Game_Stats()
stat_names = [num_stats, hang_stats, yazy_stats]


# Establish Functions

def int_from_list(indices: int, msg: str) -> int:
    '''Integer input validation for specific cases.'''
    while True:
        selection = input(msg)
        if selection.isdecimal():
            if 1 <= (selection := int(selection)) <= indices:
                break
    return selection - 1

def game_select() -> int:
    '''Game selection.'''
    print(f'{col(32)}Game Selection:{X}')

    for i, item in enumerate(games, start=1):
        print(f'{i}. {item}')
    print()
    t.sleep(0.25)

    game = int_from_list(5, 'Which game would you like to play? ')
    return game

def get_bet() -> int:
    '''Bet validation loop.'''
    while True:
        print(f'You have {cred_msg(creds)} ', end='')
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
        print(f"{col(31)}Woah, you're all in!{X}\n")
    else:
        print()
    return bet

def game_stats(i: int) -> None:
    '''Print game-specific stats.'''
    stats = stat_names[i]

    print(f'''{col(36)}{games[i]}:{X}
Rounds Played: {col(33)}{(total := stats.won + stats.lost)}{X}''')
    
    if games[i] == 'Yahtzee': # yahtzee stats different because you win every time
        print(f'Highest Score: {col(32)}{stats.max_score}{X}')

        if total == 0:
            print(f'Yahtzee Rate: {col(33)}No percentage available{X}\n')
        else:
            print(f'Yahtzee Rate: {col(33)}{100 * stats.won / (total):.1f}%{X}\n')

    else:
        print(f'Wins-Losses: {col(32)}{stats.won}{X}-{col(31)}{stats.lost}{X}')

        if total == 0:
            print(f'Win Rate: {col(33)}No percentage available{X}\n')
        else:
            print(f'Win Rate: {col(33)}{100 * stats.won / (total):.1f}%{X}\n')

def settings() -> None:
    '''Allows user to configure settings for the arcade.'''
    print(col(33) + 'Settings:' + X)
    for i, item in enumerate(['Pick New Numbers (Number Guesser)', 'Toggle Custom Dice Characters (Yahtzee)', 'Exit Settings'], start=1):
        print(f'{i}. {item}')
    print()
    t.sleep(0.25)

    setting = int_from_list(3, 'Select a setting: ')

    if setting == 0:
        print('You selected: Pick New Numbers (Number Guesser)\n')
        global num_guess_lower, num_guess_upper
        num_guess_lower, num_guess_upper = number_guesser.get_numbers()
    elif setting == 1:
        print('You selected: Toggle Custom Dice Characters (Yahtzee)')
        global dice_setting
        dice_setting = not dice_setting
        print('Custom characters are now ' + (f'{col(32)}enabled.' if dice_setting else f'{col(31)}disabled.') + X + '\n')
    else:
        print('You selected: Exit Settings\n')


# Main Loop

while True:
    game = game_select()
    
    if game == 3:
        print('You selected: Settings\n')
        settings()
        continue
    elif game == 4:
        print('You selected: Quit\n')
        break

    print(f'You have chosen {col(33)}{games[game]}.{X}\n')
    bet = get_bet()

    # Play a game
    if game == 0:
        if not num_guess_lower and not num_guess_upper:
            num_guess_lower, num_guess_upper = number_guesser.get_numbers()
        result = number_guesser.play(bet, num_guess_lower, num_guess_upper)

    elif game == 1:
        result = hangman.play(bet)

    elif game == 2:
        result, yazy_score, yazy_bool = yazy.play(bet, dice_setting)

        if yazy_score > yazy_stats.max_score: # extra stats for yahtzee
            yazy_stats.max_score = yazy_score
        
        if yazy_bool:
            yazy_stats.won += 1
        else:
            yazy_stats.lost += 1

    if result >= 0: # win or loss logic
        print(f'You won {col(32)}{result:,} credit{pl(result, False)}.{X}\n')
        if game != 2:
            stat_names[game].won += 1
    else:
        print(f'You lost {col(31)}{-result:,} credit{pl(-result, False)}.{X}\n')
        if game != 2:
            stat_names[game].lost += 1

    creds += result

    if creds > max_creds: # for stats
        max_creds = creds
    elif creds < min_creds:
        min_creds = creds

    # Replay
    if creds > 0:
        print(f'You have {cred_msg(creds)}')
        rep = yn_validate('Would you like to play a game again (y/n)? ')
        if rep:
            print()
        else:
            break
    
    else: # game over perhaps
        print(f'{col(31)}Sorry, you ran out of credits!{X}')

        if yn_validate('Okay, would you like 1 credit to keep going (y/n)? '):
            creds = 1
            print(f'''\n{col(31)}You have accepted money from the mob. You will be in debt forever. Never look back,
never pause for a moment's grace. You will be followed. If they find you, they will end
you. Heed this warning: this single credit has determined your entire future.
{col(32)}Anyways, best of luck and get those earnings back!{X}\n''')
            t.sleep(0.5)
        else:
            break


# End & Stats

print(f'\n{col(32)}Thank you for playing!{X}')
print(f'Your final balance is {cred_msg(creds)}\n')
t.sleep(0.75)
border('ARCADE STATS', 36)

print(f'''{col(36)}Global:{X}
Max Credits: {col(32)}{max_creds:,}{X}
Min Credits: {col(31)}{min_creds:,}{X}\n''')
t.sleep(0.25)

for i in range(3):
    game_stats(i)
    t.sleep(0.25)

border('COME BACK SOON!', 31)