import random
import pgzrun
import os

# Screen dimensions (WIDTH , HEIGHT)
WIDTH, HEIGHT = 1536, 864
# 1536, 864 or 1280, 1024
os.environ['SDL_VIDEO_CENTERED'] = '1'

shooting_star = Actor('star', (0, 0))
snow = [Actor('snowflake', (random.randint(0, WIDTH), random.randint(0, HEIGHT))) for i in range(12)]

stars, little_stars = [], []

for i in range(20):
    starx = random.randint(0, WIDTH)
    stary = random.randint(0, int(2 * HEIGHT / 3))
    mystar = (starx, stary)
    stars.append(mystar)

for i in range(80):
    starx = random.randint(0, WIDTH)
    stary = random.randint(0, int(2 * HEIGHT / 3))
    mystar = (starx, stary)
    little_stars.append(mystar)


def draw():
    screen.clear()
    
    # Sky
    screen.fill((0, 0, 100)) # sky
    
    # Stars
    for x, y in stars:
        screen.draw.filled_circle((x, y), 3, "yellow")

    for x, y in little_stars:
        screen.draw.filled_circle((x, y), 1, "yellow")
    
    # Shooting Star
    shooting_star.draw()

    # Ground
    ground = Rect((0, 2 * HEIGHT / 3), (WIDTH, HEIGHT))
    screen.draw.filled_rect(ground, (220, 220, 200))

    # Snowman
    screen.draw.filled_circle((500, 450), 50, "white")
    screen.draw.filled_circle((500, 550), 65, "white")
    screen.draw.filled_circle((500, 650), 80, "white")

    # Eyes
    screen.draw.filled_circle((480, 435), 8, "black")
    screen.draw.filled_circle((520, 435), 8, "black")

    # Nose
    for i in range(450, 470):
        screen.draw.line((500, i), (530, 460), 'orange')
    
    # Buttons
    screen.draw.filled_circle((500, 525), 10, "black")
    screen.draw.filled_circle((500, 550), 10, "black")
    screen.draw.filled_circle((500, 575), 10, "black")

    # Arms
    for i in range(520, 530):
        screen.draw.line((550, i), (600, 500), (100, 50, 0))
        screen.draw.line((450, i), (400, 500), (100, 50, 0))

    # Bush
    screen.draw.filled_circle((1200, 600), 65, (50, 200, 50))
    screen.draw.filled_circle((1150, 650), 65, (50, 200, 50))
    screen.draw.filled_circle((1250, 650), 65, (50, 200, 50))

    # Snow
    for flake in snow:
        flake.draw()

def update():
    shooting_star.x += 3
    shooting_star.y += 1
  
    if shooting_star.left > WIDTH or shooting_star.top > 2 * HEIGHT / 3:
        shooting_star.pos = (0, 0)
    
    for flake in snow:
        flake.y += 1
        if flake.top > HEIGHT:
            flake.bottom = 0

pgzrun.go()