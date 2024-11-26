# Number Guessing Game

import random as r, math as m

# Color abbreviations
X = '\x1b[0m'
def col(i): return f'\x1b[1;{i}m'

# Welcome
cred = 500 # Start with 500 credits
minc, maxc, won, lost = 500, 500, 0, 0 # For stats later
bar = [f'{col(32)}■'] * 3 + [f'{col(33)}■'] * 3 + [f'{col(31)}■'] * 3 # Difficulty bar
print(f'{col(31)}Welcome to the casino!\n{X}')

# Range config loop
while True:
    while True: # Establish lower bound
        low = input("What's your lucky number (lower bound)? ")
        if not low.isdecimal():
            print(f'Invalid value (not an integer >= 0).')
        else:
            low = int(low)
            break

    while True: # Establish upper bound
        upp = input("What's your other lucky number (upper bound)? ")
        if not upp.isdecimal():
            print(f'Invalid value (not an integer >= 0).')
        elif not low + 9 <= int(upp):
            print(f'Invalid value (must be >= low + 9).')
        else:
            upp = int(upp)
            break

    log = m.floor(m.log2(upp - low + 1) * 10)
    diff = log % 10 # Assigns 0-9 rating of logarithmic "difficulty"

    # Line below saves the formatting of the diff for the stats later, if wonkily
    print(statdiff := f'Difficulty: {(X, col(32), col(33), col(31))[m.ceil(diff / 3)]}{diff + 1}{X}/10')

    for i in range(diff): # Print difficulty bar
        print(bar[i], end='')
    print(X + '■' * (9 - diff) + '\n')

    # Reconfig validation loop
    reconfig = None
    while reconfig not in ('y', 'n'):
        reconfig = input('Keep these numbers (y/n)? ').strip().lower()
    if reconfig == 'n':
        print()
    else:
        break

print(f"{col(31)}\nLet's go gambling!{X}\n")

# Main loop
while True:
    rand = r.randint(low, upp)
    guesses = log // 10 # Guesses = # of times you can effectively halve the range

    # Bet validation loop
    while True:
        print(f'You have {col(36)}{cred:,}{X} credit{"s" * (cred != 1)}.')
        bet = input('How many would you like to bet? ')
        if not bet.isdecimal():
            print(f'Invalid bet (not an integer >= 0).')
        elif int(bet) == 0:
            print(f'Invalid bet (you have to bet something!).')
        elif not 1 <= int(bet) <= cred:
            print(f'Invalid bet (insufficient funds).')
        else:
            bet = int(bet)
            break

    if bet == cred: # All in
        print(f"{col(31)}Woah, you're all in!{X}")

    print(f'\nGuess a random number between {col(95)}{low:,}{X} and {col(95)}{upp:,}{X}. \
You have {col(33)}{guesses}{X} guesses.\n')

    # Guess loop
    while True:
        # Guess validation loop
        while True:
            guess = input('Enter a number: ')
            if not guess.isdecimal():
                print(f'Invalid guess (not an integer >= 0). You have {col(33)}{guesses}{X} guess{"es" * (guesses != 1)} left.')
            elif not low <= int(guess) <= upp:
                print(f'Invalid guess (not in range). You have {col(33)}{guesses}{X} guess{"es" * (guesses != 1)} left.')
            else:
                guess = int(guess)
                break
        guesses -= 1

        # Handling guess
        if guess < rand:
            print(f'Too {col(31)}low!{X} You have {col(33)}{guesses}{X} guess{"es" * (guesses != 1)} left.')
        elif guess > rand:
            print(f'Too {col(32)}high!{X} You have {col(33)}{guesses}{X} guess{"es" * (guesses != 1)} left.')
        else: # Winning logic
            print(f'\nYou won {col(32)}{bet * (guesses + 1):,}{X} credit{"s" * (bet * (guesses + 1) != 1)} \
for guessing {col(95)}{rand}{X}, with a multiplier of {col(33)}{guesses + 1}{X}.\n')
            cred += bet * (guesses + 1)
            won += 1
            break
        if guesses == 0: # Losing logic
            print(f'\nYou lost {col(31)}{bet:,}{X} credit{"s" * (bet != 1)}! \
The correct number was {col(95)}{rand}{X}.\n')
            cred -= bet
            lost += 1
            break

    if cred > maxc: # For stats later
        maxc = cred
    elif cred < minc:
        minc = cred

    # Replay
    if cred > 0:
        # y/n validation loop
        rep = None
        while rep not in ('y', 'n'):
            rep = input('Would you like to play again (y/n)? ').strip().lower()
        if rep == 'n':
            break
        else:
            print()
    else: # Game over
        print(f'{col(31)}Sorry, you ran out of credits. Game over!{X}')
        break

print(f'\n{col(32)}Thank you for playing!{X}')
print(f'Your final balance is {col(36)}{cred:,}{X} credit{"s" * (cred != 1)}.')

# Stats
print(f'''\n{col(36)}Stats:{X}
Number Range: {col(35)}{low:,}{X} to {col(35)}{upp:,}{X}
Range {statdiff}

Rounds Played: {col(33)}{won + lost}{X}
Wins-Losses: {col(32)}{won}{X}-{col(31)}{lost}{X}
Win Rate: {col(33)}{100 * won / (won + lost):.1f}%{X}

Max Credits: {col(32)}{maxc:,}{X}
Min Credits: {col(31)}{minc}{X}''')

def play(creds: int):
    creds += 1
    return creds