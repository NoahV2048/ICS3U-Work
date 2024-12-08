import pgzrun
import random
import os

os.environ["SDL_VIDEO_CENTERED"] = "1"  # Forces window to be centered on screen.
HEIGHT = 480
WIDTH = 640
TITLE = "DVD Screensaver"

logo = Actor('dvd_logo')

logo.pos = (random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
logo.bounces = 0

logo.dx = 0
while logo.dx == 0:
    logo.dx = random.randint(-5, 5)

logo.dy = 0
while logo.dy == 0:
    logo.dy = random.randint(-5, 5)

def update():
    if logo.right >= WIDTH:
        logo.right = WIDTH #fix for rotating logo sometimes getting stuck along the screen edge.
        logo.dx *= -1
        logo.bounces += 1
    if logo.left <= 0:
        logo.left = 0
        logo.dx *= -1
        logo.bounces += 1
    if logo.bottom >= HEIGHT:
        logo.bottom = HEIGHT
        logo.dy *= -1
        logo.bounces += 1
    if logo.top <= 0:
        logo.top = 0
        logo.dy *= -1
        logo.bounces += 1

    #Update the logo's position
    logo.x += logo.dx
    logo.y += logo.dy

    logo.dx *= 1.001
    logo.dy *= 1.001

    if logo.bounces >= 10:
        logo.angle += 1

def draw():
    screen.clear()
    screen.fill('white')
    logo.draw()

pgzrun.go()