# Arcade
# Incorporates 3 different minigames
# Noah Verdon
# Last edited: Nov. __, 2024

# Import numberGuesser, hangman
from common import X, col, pl, cred_msg, gs_msg


# Init & Welcome

creds = 500
games = ['Number Guesser', 'Hangman', 'Other TBD', 'Quit']
print(f'{col(31)}Welcome to the Arcade!\n{X}')


# Establish Stats

class Game_stats: # unique to each game
    def __init__(self):
        self.games_won, self.game_lost = 0, 0

min_creds, max_creds = 500, 500 # global stats
numberGuesser_stats = Game_stats


# Establish Functions

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
    return game

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
    return bet


# Main Loop

while True:
    game = game_select()
    
    if game == 4:
        break

    print(f'\nYou have chosen {games[game - 1]}.')

    bet = get_bet()




#You have {creds} credits.
#You have chosen Hangman!

#Simulating Hangman: You lose 300 credits.

#You have 700 credits.
