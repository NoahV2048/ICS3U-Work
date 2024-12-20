import pgzrun, os, random, sys, pygame as pg
from pgzhelper import *

# Window Settings
os.environ["SDL_VIDEO_CENTERED"] = "1" # center the window
# pygame.mouse.set_visible(False) # set cursor invisible
# pygame.mouse.set_cursor

WIDTH, HEIGHT = 1280, 720 # game resolution: 1280 x 720
TITLE = "ULTRAKOOL"
background = f'background_space_{random.randint(0, 9)}'


# Initialize global variables
game_stage = None
background_y = 0
time_mult = 1

# Initialize primary Actors
# player = Actor('sprite')


# Game Stage Initializations

def init_menu():
    global game_stage, button_levels

    game_stage = 'menu'
    button_levels = Actor('text_levels', center=(WIDTH/2, HEIGHT/2))
    music.play('intro')
    
# Event Handlers (one-time inputs)

def on_mouse_down(pos, button):
    global background

    if button == mouse.LEFT:
        background = f'background_space_{random.randint(0, 9)}'

def on_mouse_up(pos, button):
    pass

def on_mouse_move(pos, rel, buttons):
    pass

def on_key_down(key, unicode):
    if key == keys.ESCAPE: # temporary (easier than ctrl + Q)
        sys.exit()

def on_key_up(key):
    pass

def on_music_end():
    pass


# UPDATE

def update():
    global background_y # globals

    if game_stage == 'menu':
        background_y -= 0.25
        if background_y <= -720:
            background_y = 0
        
        if button_levels.obb_collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]):
            if button_levels.scale == 1:
                animate(button_levels, scale=1.1, duration=0.1, tween='linear')
        else:
            animate(button_levels, scale=1, duration=0.1, tween='linear')


# DRAW

def draw():
    screen.clear()

    if game_stage == 'menu':
        screen.blit(background, (0, background_y))
        screen.blit(background, (0, background_y + 720))
        screen.blit('text_title', (240, 50))
        button_levels.draw()


# Scheduling and Go:

init_menu()
pgzrun.go()