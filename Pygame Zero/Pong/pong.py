import pgzrun
import os
import math
from random import randint, choice

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 600
HEIGHT = 600
WHITE = (255, 255, 255)

# Initialize primary Actors
paddle1 = Actor('paddle_blue')
paddle1.angle = 90
paddle1.pos = (25, 300)

paddle2 = Actor('paddle_red')
paddle2.angle = 90
paddle2.pos = (575, 300)

ball = Actor('ball_grey')

running, interim = (False,) * 2
winner, single = 0, 0
bias, response = 30, 150

def reset_score():
    paddle1.score = 0
    paddle2.score = 0

def reset_game():
    global running, interim, single
    ball.pos = (-100, -100)

    running, interim = (False,) * 2
    single = 0

def move_ball():
    global interim
    interim = False
    sounds.lasersmall.play()

    direction = choice([1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15])
    ball.dx = math.cos(math.pi * direction / 8) * 5
    ball.dy = math.sin(math.pi * direction / 8) * 5

def reset_ball():
    global running, interim
    running, interim = True, True

    ball.pos = (300, randint(25, 575))
    ball.dx = 0
    ball.dy = 0
    
    clock.schedule(move_ball, 1.0)

def on_key_down(key):
    global single, winner

    if key == keys.K_1 and not running:
        single = 1
        winner = 0
        sounds.lasersmall.play()
        reset_score()
        reset_ball()
    elif key == keys.K_2 and not running:
        winner = 0
        sounds.lasersmall.play()
        reset_score()
        reset_ball()
    elif key == keys.K_3 and not running:
        single = 2
        winner = 0
        sounds.lasersmall.play()
        reset_score()
        reset_ball()

# Update - Handle ongoing input, update positions, check interactions
def update():
    
    # Move ball
    if running:
        ball.x += ball.dx
        ball.y += ball.dy

        # Collision
        if ball.colliderect(paddle1):
            sounds.impactmetal.play()
            # dir = math.atan2(ball.dy, ball.dx)

            if ball.y < paddle1.top:
                ball.bottom = paddle1.top
                ball.dy = -abs(ball.dy)
            elif ball.y > paddle1.bottom:
                ball.top = paddle1.bottom
                ball.dy = abs(ball.dy)
            #if ball.x < paddle1.right:
            else:
                mag = math.sqrt(ball.dx ** 2 + ball.dy ** 2) + 1 # add 1 to increase velocity

                sine = (ball.y - paddle1.y) / 50
                if sine > 0.75:
                    sine = 0.75
                elif sine < -0.75:
                    sine = -0.75
                cosine = math.sqrt(1 - sine ** 2)

                ball.dx = cosine * mag
                ball.dy = sine * mag

                ball.left = paddle1.right + 1

        elif ball.colliderect(paddle2):
            sounds.impactmetal.play()

            if ball.y < paddle2.top:
                ball.bottom = paddle2.top
                ball.dy = -abs(ball.dy)
            
            elif ball.y > paddle2.bottom:
                ball.top = paddle2.bottom
                ball.dy = abs(ball.dy)

            else:
                mag = math.sqrt(ball.dx ** 2 + ball.dy ** 2) + 1 # add 1 to increase velocity

                sine = (ball.y - paddle2.y) / 50
                if sine > 0.75:
                    sine = 0.75
                elif sine < -0.75:
                    sine = -0.75
                cosine = math.sqrt(1 - sine ** 2)

                ball.dx = -cosine * mag
                ball.dy = sine * mag

                ball.right = paddle2.left - 1
    
        # Top and bottom collision detection
        if ball.top <= 0:
            ball.dy *= -1
            ball.top = 0
            sounds.impactmetal.play()
        elif ball.bottom >= HEIGHT:
            ball.dy *= -1
            ball.bottom = HEIGHT
            sounds.impactmetal.play()

        # Scoring and reset
        if ball.left >= WIDTH:
            paddle1.score += 1
            sounds.lasersmall.play()
            reset_ball()
        elif ball.right <= 0:
            paddle2.score += 1
            sounds.lasersmall.play()
            reset_ball()

    # Move the paddles up or down according to keyboard input
    if single != 2:
        if keyboard.w and paddle1.top > 0:
            paddle1.y -= 10
        if keyboard.s and paddle1.bottom < HEIGHT:
            paddle1.y += 10
    else: # no players
        if ball.y < paddle1.y - bias and paddle1.top > 0 and ball.x < 600 - response:
            paddle1.y -= min(ball.y, 10)
        elif ball.y > paddle1.y + bias and paddle1.bottom < HEIGHT and ball.x < 600 - response:
            paddle1.y += min(ball.y, 10)

    if not single:
        if keyboard.UP and paddle2.top > 0:
            paddle2.y -= 10
        if keyboard.DOWN and paddle2.bottom < HEIGHT:
            paddle2.y += 10
    else: # singleplayer
        if ball.y < paddle2.y - bias and paddle2.top > 0 and ball.x > response:
            paddle2.y -= min(ball.y, 10)
        elif ball.y > paddle2.y + bias and paddle2.bottom < HEIGHT and ball.x > response:
            paddle2.y += min(ball.y, 10)

    # Winning logic
    global winner
    if paddle1.score >= 10:
        winner = 1
        reset_game()
    elif paddle2.score >= 10:
        winner = 2
        reset_game()

# Draw each Actor, and any other UI elements
def draw():
    screen.clear()

    screen.draw.text(str(paddle1.score), center=(150, 100), fontname="future", fontsize=75, color="white")
    screen.draw.text(str(paddle2.score), center=(450, 100), fontname="future", fontsize=75, color="white")

    paddle1.draw()
    paddle2.draw()
    ball.draw()

    if not running:
        screen.draw.text('PRESS 1 for Singleplayer\nPRESS 2 for Two-Player\nPRESS 3 for No-Player', center=(300, 300), fontname="future", fontsize=20, color="white")
        screen.draw.text('WASD', center=(150, 400), fontname="pixel", fontsize=45, color="white")
        screen.draw.text('ARROWS', center=(450, 400), fontname="pixel", fontsize=45, color="white")
    
    if interim:
        screen.draw.text('READY...', center=(300, 300), fontname="future", fontsize=50, color="white")

    if winner:
        screen.draw.text(f'Player {winner} won!', center=(300, 200), fontname="future", fontsize=50, color="white")

# Setup and Go:
reset_game()
reset_score()
pgzrun.go()