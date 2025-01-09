# ULTRAKOOL
# A really cool combat platformer game
# Noah Verdon
# Last Edited: TBD

import pgzrun, os, random, sys, pygame as pg
from pgzhelper import *

# Window Settings
os.environ["SDL_VIDEO_CENTERED"] = "1" # center the window
WIDTH, HEIGHT = 1280, 720 # game resolution: 1280 x 720 (16:9)
TITLE = "ULTRAKOOL"
bg_image = f'background_space_{random.randint(0, 9)}'

# Standard Pygame Settings
pg.mouse.set_cursor(*pygame.cursors.broken_x)

class FakeJoy():
    def __init__(self):
        pygame.mouse.set_visible(False) # hide cursor in controller mode
    def get_axis(*argsw):
        return 0
    def get_button(*args):
        return False

try:
    joystick = pg.joystick.Joystick(0)
except:
    joystick = FakeJoy()


# Initialize global variables
scene = None
bg_y = 0
gravity = 2
joystick_drift = 0.1
music.set_volume(1)
player_animate_info = {'idle': 5, 'walk': 6, 'attack': 15, 'hit': 4, 'death': 8}

# Initialize primary Actors
# player = Actor('sprite')


# Game Stage Initializations

def init_menu():
    global scene, button_levels, bg_dy

    scene = 'menu'
    button_levels = Actor('text_levels', center=(WIDTH/2, HEIGHT/2))
    bg_dy = 0.25
    music.play('intro')

def init_level():
    global scene, player, attacks

    scene = 'level'
    attacks = []

    player = Actor('microwave_idle_0', center=(WIDTH/2, HEIGHT))
    player.state = None
    player.time_mod = 1
    player.dx, player.dy = 0, 0 # simple movement attributes
    player.dashing, player.jumps = False, 2 # advanced movement attributes
    player_animate('idle')

    music.fadeout(1)
    clock.schedule(music.play('song_7'), 1)


# Player Functions

def player_animate(arg: str, reverse=True) -> None:
    if player.state != arg:
        player.state = arg
        frames = player_animate_info[arg]
        if reverse:
            player.images = [f'microwave_{arg}_{x}' for x in range(frames-1, 0, -1)] # option to animate backwards
        else:
            player.images = [f'microwave_{arg}_{x}' for x in range(0, frames, 1)]
    
def player_attack(pos): # position curently misaligned
    attack = Actor('TBD', pos)
    attack.direction = player.direction_to(pos)
    attacks.append(attack)

def player_dash():
    player.dashing = True
    player.dy = 0

    if player.flip_x:
        player.dx = 20
    else:
        player.dx = -20

    clock.schedule


# Event Handlers (one-time inputs)

def on_mouse_down(pos, button):
    if scene == 'menu':
        if button == mouse.LEFT:
            if button_levels.collidepoint(pos):
                music.fadeout(1)
                bg_dy = 2
                # sounds.play() # TODO: click noise

                clock.schedule(init_level, 1)
    
    elif scene == 'level':
        if button == mouse.LEFT:
            player_attack(pos)

        if button == mouse.RIGHT:
            animate(player, time_mod=0.2, duration=0.5)
            music.set_volume(0.5)
            player.fps *= 0.2

def on_mouse_up(pos, button):
    if scene == 'menu':
        pass

    elif scene == 'level':
        animate(player, time_mod=1, duration=0.5)
        music.set_volume(1)
        player.fps /= 0.2

def on_mouse_move(pos, rel, buttons):
    pass

def on_key_down(key, unicode):
    if scene == 'menu':
        if key == keys.ESCAPE:
            sys.exit()

    if scene == 'level':
        if key == keys.W and player.jumps > 0:
            player.jumps -= 1
            player.dy = (2 * gravity * 3.5 * 60) ** 0.5 # rearranging projectile height equation for initial velocity but should be simplified later
        
        elif key == keys.LSHIFT: # shift could trigger sticky keys on Windows
            pass # dash

def on_key_up(key):

    if scene == 'level':
        pass

def on_music_end():
    pass


# UPDATE

def update():
    global bg_y # globals

    if scene == 'menu':
        bg_y -= bg_dy
        if bg_y <= -720:
            bg_y = 0
        
        if button_levels.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]):
            if button_levels.scale == 1:
                animate(button_levels, scale=1.1, duration=0.1, tween='linear')
        else:
            animate(button_levels, scale=1, duration=0.1, tween='linear')
    
    elif scene == 'level':

        # Animations
        # player.fps = player_animate_info[player.state] * player.time_mod * 2

        # Flipping
        if pg.mouse.get_pos()[0] >= player.x:
            player.flip_x = True
        else:
            player.flip_x = False

        # Gravity
        player.y -= player.dy * player.time_mod

        if player.bottom > HEIGHT:
            player.dy = 0
            player.jumps = 2
            player.bottom = HEIGHT

        if player.bottom < HEIGHT:
            player.dy -= gravity * player.time_mod

        # Side movement
        if keyboard.a or joystick.get_axis(0) < -joystick_drift:
            player.x -= 10 * player.time_mod

            reverse = False
            if player.flip_x:
                reverse = True

            player_animate('walk', reverse=reverse) # reversing list gets rid of moonwalking effect
            
        if keyboard.d or joystick.get_axis(0) > joystick_drift:
            player.x += 10 * player.time_mod

            reverse = True
            if player.flip_x:
                reverse = False
            player_animate('walk', reverse=reverse) # reversing list gets rid of moonwalking effect
        
        if not (keyboard.a or joystick.get_axis(0) < -joystick_drift or keyboard.d or joystick.get_axis(0) > joystick_drift):
            player_animate('idle')
        
        player.scale = 2
        player.animate()


# DRAW

def draw():
    screen.clear()

    if scene == 'menu':
        screen.blit(bg_image, (0, bg_y))
        screen.blit(bg_image, (0, bg_y + 720))
        screen.blit('text_title', (240, 50))
        button_levels.draw()
    
    elif scene == 'level':
        screen.blit(bg_image, (0, bg_y))
        screen.blit(bg_image, (0, bg_y + 720))
        player.draw()


# Scheduling and Go:

init_menu()
pgzrun.go()