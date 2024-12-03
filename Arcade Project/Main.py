# Arcade
# Allows user to play 3 different minigames
# Noah Verdon
# Last edited: Dec. 3, 2024

# Import numberGuesser, hangman
from common import X, col, pl, border


# Welcome & Init

border('WELCOME TO THE ARCADE!', 31)
creds = 500
games = ['Number Guesser', 'Hangman', 'Other TBD', 'Quit']

class Game_stats: # stats unique to each game
    def __init__(self):
        self.won, self.lost = 0, 0

min_creds, max_creds = 500, 500 # global stats
num_stats, hang_stats, TBD_stats = (Game_stats(),) * 3
short_games = [num_stats, hang_stats, TBD_stats]


# Establish Functions

def cred_msg() -> str: # credit message function
    return f'{col(36)}{creds}{X} credit{pl(creds, 0)}.'

def game_select() -> int:
    '''Game selection.'''
    print(f'''{col(32)}Game Selection:{X}
1. Number Guesser
2. Hangman
3. Other
4. Quit\n''')
    while True:
        game = input('Which game would you like to play? ')
        if game.isdecimal():
            if 1 <= (game := int(game)) <= 4:
                break
    return game - 1

def get_bet():
    '''Bet validation loop.'''
    while True:
        print(f'You have {col(36)}{creds:,}{X} credit{"s" * (creds != 1)}.')
        bet = input('How many would you like to bet? ')
        if not bet.isdecimal():
            print(f'Invalid bet (not an integer >= 0).')
        elif int(bet) == 0:
            print(f'Invalid bet (you have to bet something!).')
        elif not 1 <= int(bet) <= creds:
            print(f'Invalid bet (insufficient funds).')
        else:
            bet = int(bet)
            break

    if bet == creds: # All in
        print(f"{col(31)}Woah, you're all in!{X}")
    
    print()
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
    return ('y', 'n').index(yn)


# Main Loop

while True:
    game = game_select()
    
    if game == 3:
        break

    print(f'\nYou have chosen {games[game]}.')
    bet = get_bet()

    #[numberGuesser, hangman][game].play()
    creds += 1

    if creds > maxc: # for stats later
        maxc = creds
    elif creds < minc:
        minc = creds

    # Replay
    if creds > 0:
        print(f'You have {cred_msg}')
        rep = yn_validate('Would you like to play again (y/n)? ')
        if rep:
            print()
        else:
            break

    else: # game over
        print(f'{col(31)}Sorry, you ran out of credits!{X}')
        one_cred = yn_validate('Okay, would you like 1 credit to keep going (y/n)? ')

        if one_cred:
            creds = 1
            print()
        else:
            break


# End & Stats

print(f'\n{col(32)}Thank you for playing!{X}')
print(f'Your final balance is {cred_msg()}\n')
border('ARCADE STATS', 36)

print(f'''{col(36)}Global:{X}
Max Credits: {col(32)}{max_creds:,}{X}
Min Credits: {col(31)}{min_creds:,}{X}\n''')

for i in range(3):
    game_stats(i)

border('COME BACK SOON!', 31)