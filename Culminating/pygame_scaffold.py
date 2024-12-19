import pgzrun, os, random
from pgzhelper import *

# Window Settings
os.environ["SDL_VIDEO_CENTERED"] = "1" # center the window
# pygame.mouse.set_visible(False) # set cursor invisible

WIDTH, HEIGHT = 1280, 720 # game resolution: 1280 x 720
TITLE = "ULTRAKOOL"
background = f'background_space_{random.randint(0, 9)}'


# Initialize global variables
background_y = 0
# score = 0

# Initialize primary Actors
# player = Actor('sprite')

# Event Handlers (one-time inputs)
def on_mouse_down(pos, button):
    global background
    if button == mouse.LEFT:
        background = f'background_space_{random.randint(0, 9)}'

# def on_mouse_up(pos, button):
# def on_mouse_move(pos, rel, buttons):
# def on_key_down(key, unicode):
# def on_key_up(key):
# def on_music_end():


# Update - Handle ongoing input, update positions, check interactions
def update():
    global background_y
    background_y -= 0.25
    if background_y <= -720:
        background_y = 0



# Draw - Draw each Actor, and any other UI elements
def draw():
    screen.clear()
    screen.blit(background, (0, background_y))
    screen.blit(background, (0, background_y + 720))
    screen.blit('title', (320, 0))


# Scheduling and Go:
pgzrun.go()