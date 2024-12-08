import pgzrun
import os
from random import randint

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 600
HEIGHT = 600
WHITE = (255, 255, 255)

# Initialize primary Actors
paddle1 = Actor('paddle_blue')
paddle1.score = 0
paddle1.angle = 90
paddle1.pos = (25, 300)

paddle2 = Actor('paddle_red')
paddle2.score = 0
paddle2.angle = 90
paddle2.pos = (575, 300)

ball = Actor('ball_grey')

def reset_ball():
    ball.pos = (300, 300)

    ball.dx = 0
    while ball.dx == 0:
        ball.dx = randint(-5, 5)

    ball.dy = 0
    while ball.dy == 0:
        ball.dy = randint(-1, 1) * 3

# Update - Handle ongoing input, update positions, check interactions
def update():
    
    # Move the paddles up or down according to keyboard input
    if keyboard.w and paddle1.top > 0:
        paddle1.y -= 5
    if keyboard.s and paddle1.bottom < HEIGHT:
        paddle1.y += 5

    if keyboard.UP and paddle2.top > 0:
        paddle2.y -= 5
    if keyboard.DOWN and paddle2.bottom < HEIGHT:
        paddle2.y += 5
    
    ball.x += ball.dx
    ball.y += ball.dy
    
    # Have ball change direction when it hits paddle
    if ball.colliderect(paddle1):
        ball.dx *= -1
        sounds.impactmetal.play()
    elif ball.colliderect(paddle2):
        ball.dx *= -1
        sounds.impactmetal.play()
    
    # Top and bottom collision detection
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball.dy *= -1
    
    # Scoring and reset
    if ball.left >= WIDTH:
        paddle1.score += 1
        sounds.lasersmall.play()
        reset_ball()
    elif ball.right <= 0:
        paddle2.score += 1
        sounds.lasersmall.play()
        reset_ball()

# Draw each Actor, and any other UI elements
def draw():
    screen.clear()

    screen.draw.text(str(paddle1.score), (150, 50), fontsize=50, color="white")
    screen.draw.text(str(paddle2.score), (450, 50), fontsize=50, color="white")

    paddle1.draw()
    paddle2.draw()
    ball.draw()
 
# Setup and Go:
reset_ball()

pgzrun.go()