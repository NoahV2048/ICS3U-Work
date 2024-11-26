# Arcade
# Incorporates 3 different minigames
# Noah Verdon
# Last edited: Nov. 26, 2024

import numberGuesser, hangman
from common import X, col


# Init & Welcome

creds = 500
print(f'{col(31)}Welcome to the Arcade!\n{X}')


# Establish Stats

class Game_stats: # unique to each game
    def __init__(self):
        self.games_won, self.game_lost = 0, 0

min_creds, max_creds = 500, 500 # global stats
numberGuesser_stats = Game_stats



while True:
   print(f'''You have 1000 credits.
         1. Number Guesser
2. Hangman
3. Quit''')

#Which game would you like to play? 2

#You have chosen Hangman!

#Simulating Hangman: You lose 300 credits.

#You have 700 credits.
