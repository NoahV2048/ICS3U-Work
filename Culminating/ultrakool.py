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
gravity = 2
music.set_volume(1)
player_animate_info = {'idle': 5, 'walk': 6, 'attack': 15, 'hit': 4, 'death': 8}

# Initialize primary Actors
# player = Actor('sprite')


# Game Stage Initializations

def init_menu():
    global game_stage, button_levels, bg_speed

    game_stage = 'menu'
    button_levels = Actor('text_levels', center=(WIDTH/2, HEIGHT/2))
    bg_speed = 0.25
    music.play('intro')

def init_endless():
    global game_stage, player

    game_stage = 'endless'
    player = Actor('microwave_idle_0', center=(WIDTH/2, HEIGHT))
    player.state, player.dx, player.dy, player.jumps = None, 0, 0, 2 # establish some custom attributes for the player
    player_animate('idle')

    music.fadeout(1)
    clock.schedule(music.play('song_7'), 1)


# Player Functions

def player_animate(arg: str, reverse=True) -> None:
    if player.state != arg:
        player.state = arg
        frames = player_animate_info[arg]
        player.fps = frames * 2 * time_mult
        if reverse:
            player.images = [f'microwave_{arg}_{x}' for x in range(frames - 1, 0, -1)] # option to animate backwards
        else:
            player.images = [f'microwave_{arg}_{x}' for x in range(0, frames, 1)]
    
# Event Handlers (one-time inputs)

def on_mouse_down(pos, button):
    global background, bg_speed

    if game_stage == 'menu':
        if button == mouse.LEFT:
            if button_levels.collidepoint(pos):
                music.fadeout(1)
                bg_speed = 2
                #sounds.play()

                clock.schedule(init_endless, 1)

        if button == mouse.RIGHT:
            background = f'background_space_{random.randint(0, 9)}'        
    
    elif game_stage == 'endless':
        if button == mouse.RIGHT:
            init_menu()

def on_mouse_up(pos, button):
    pass

def on_mouse_move(pos, rel, buttons):
    pass

def on_key_down(key, unicode):
    global time_mult

    if key == keys.ESCAPE: # temporary (easier than ctrl + Q)
        sys.exit()

    if game_stage == 'endless':
        if key == keys.W and player.jumps > 0:
            player.jumps -= 1
            player.dy = (2 * gravity * 3.5 * 60) ** 0.5 # rearranging projectiel height equation for velocity
        
        elif key == keys.LSHIFT: # shift could trigger sticky keys on Windows
            time_mult = 0.2
            player.fps *= time_mult
            music.set_volume(0.5)

def on_key_up(key):
    global time_mult

    if game_stage == 'endless':
        if key == keys.LSHIFT:
            player.fps /= time_mult
            time_mult = 1
            music.set_volume(1)

def on_music_end():
    pass


# UPDATE

def update():
    global background_y # globals

    if game_stage == 'menu':
        background_y -= bg_speed
        if background_y <= -720:
            background_y = 0
        
        if button_levels.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]):
            if button_levels.scale == 1:
                animate(button_levels, scale=1.1, duration=0.1, tween='linear')
        else:
            animate(button_levels, scale=1, duration=0.1, tween='linear')
    
    elif game_stage == 'endless':

        # Flipping
        if pg.mouse.get_pos()[0] >= player.x:
            player.flip_x = True
        else:
            player.flip_x = False

        # Gravity
        player.y -= player.dy * time_mult

        if player.bottom > HEIGHT:
            player.dy = 0
            player.jumps = 2
            player.bottom = HEIGHT

        if player.bottom < HEIGHT:
            player.dy -= gravity * time_mult

        # Side movement
        if keyboard.a:
            player.x -= 10 * time_mult

            reverse = False
            if player.flip_x:
                reverse = True

            player_animate('walk', reverse=reverse) # reversing list gets rid of moonwalking effect
            
        elif keyboard.d:
            player.x += 10 * time_mult

            reverse = True
            if player.flip_x:
                reverse = False
            player_animate('walk', reverse=reverse) # reversing list gets rid of moonwalking effect
        
        else:
            player_animate('idle')
        
        player.scale = 3
        player.animate()


# DRAW

def draw():
    screen.clear()

    if game_stage == 'menu':
        screen.blit(background, (0, background_y))
        screen.blit(background, (0, background_y + 720))
        screen.blit('text_title', (240, 50))
        button_levels.draw()
    
    elif game_stage == 'endless':
        screen.blit(background, (0, background_y))
        screen.blit(background, (0, background_y + 720))
        player.draw()


# Scheduling and Go:

init_menu()
pgzrun.go()