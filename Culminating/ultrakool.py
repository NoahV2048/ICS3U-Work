# ULTRAKOOL
# A really cool combat platformer game
# Noah Verdon
# Last Edited: TBD

import pgzrun, os, random, sys, pygame as pg
from pgzhelper import *
from levels import *

# Standard Settings
os.environ["SDL_VIDEO_CENTERED"] = "1" # center the window
WIDTH, HEIGHT = 1280, 720 # game resolution: 1280 x 720 (16:9)
TITLE = "ULTRAKOOL"

# Standard Pygame Settings
# pg.mouse.set_cursor(*pygame.cursors.broken_x) # TODO


# Saved Settings # TODO: hook up custom settings

joystick_drift = 0.1
music.set_volume(0)


# Controller Support

if pg.joystick.Joystick(0):
    controller_mode = True
    pygame.mouse.set_visible(False) # hide cursor in controller mode
else:
    controller_mode = False


# Initialize Global Variables

scene = None
gravity = 2
player_animate_info = {'idle': 5, 'walk': 6, 'attack': 15, 'hit': 4, 'death': 8}


# Scene Initializations

def init_menu():
    '''Initializes the main, levels, and settings menus.'''
    global scene, bg_image, bg_dy, main_buttons, levels_buttons, settings_buttons

    # General menu
    scene = 'menu'
    bg_image = f'background_space_{random.randint(0, 9)}'
    bg_dy = 0.25
    music.play('intro')

    # Main screen
    main_buttons = [Actor('button_dark', center=(640, 300 + 150 * i)) for i in range(3)]

    # Levels screen
    levels_buttons = [Actor('button_dark', center=(640, 300 + 150 * i)) for i in range(3)]

    # Settings screen
    settings_buttons = [Actor('button_dark', center=(640, 300 + 150 * i)) for i in range(3)]

def init_level(num):
    global scene, player, attacks, level

    scene = 'level'
    level = num - 1
    attacks = []

    player = Actor('microwave_idle_0')
    player.state = None
    player.alive = True
    player.mx, player.my = 0, 0
    player.time_mod = 1
    
    player_animate('idle')

    switch_screen(0, 0)
    player_reset()

    #music.fadeout(1)
    #music.play('song_7')

def switch_screen(x: int, y: int):
    global tiles_clip, tiles_front, tiles_back, hazards
    tiles_clip, tiles_front, tiles_back, hazards = [], [], [], []

    for i, row in enumerate(levels[level][f'{x}-{y}']):
        print(row)
        for j, tile in enumerate(row):
            name = tile_unicode_dict[tile]

            if name == 'air':
                pass
            
            elif name == 'player_spawn':
                player.spawn = (32*j, 32*i)

            else:
                new_tile = Actor(f'tile_{name}')

                if name == 'spike': # TODO spike animations
                    new_tile = Actor('tile_water_0', topleft=(32*j, 32*i))
                    new_tile.images = [f'tile_water_{i}' for i in range(4)]
                    hazards.append(new_tile)

                elif name == 'water_0':
                    new_tile.images = [f'tile_water_{i}' for i in range(4)]
                    hazards.append(new_tile)

                elif name[0].isdecimal():
                    tiles_clip.append(new_tile)

                elif 'floor' in name or 'ceil' in name or 'side' in name:
                    tiles_front.append(new_tile)

                else:
                    tiles_back.append(new_tile)
                
                new_tile.scale = 2
                if 'big' in name:
                    new_tile.scale = 4

                new_tile.topleft=(32*j, 32*i)

# Player Functions

def player_animate(arg: str, reverse=True) -> None:
    if player.state != arg:
        player.state = arg
        frames = player_animate_info[arg] # something screwy here
        player.fps = frames * 2
        if reverse:
            player.images = [f'microwave_{arg}_{x}' for x in range(frames-1, 0, -1)] # option to animate backwards
        else:
            player.images = [f'microwave_{arg}_{x}' for x in range(0, frames, 1)]

def player_reset():
    player.pos = player.spawn
    player_ground_reset()

def player_ground_reset():
    player.vertical_reset, player.dashing = True, False
    player.dx, player.dy = 0, 0
    player.jumps = 2

def player_attack(pos): # position curently misaligned
    attack = Actor('TBD', pos)
    attack.direction = player.direction_to(pos)
    attacks.append(attack)

def player_die():
    player_animate('death')

def player_dash():
    player.dashing = True
    player.dy = 0
    dash_duration = 0.05 / player.time_mod

    if keyboard.a and not keyboard.d:
        animate(player, dx=-55, duration=dash_duration, tween='linear')
    elif keyboard.d and not keyboard.a:
        animate(player, dx=55, duration=dash_duration, tween='linear')
    elif player.flip_x:
        animate(player, dx=55, duration=dash_duration, tween='linear')
    else:
        animate(player, dx=-55, duration=dash_duration, tween='linear')

    clock.schedule(player_dash_mid, dash_duration * 2)
    clock.schedule(player_dash_end, dash_duration * 5)

def player_dash_mid():
    player.dx, player.dy = 0, 0

def player_dash_end():
    player.dashing = False

    if player.dx > 0:
        player.dx = 10
    elif player.dx < 0:
        player.dx = -10


# Event Handlers (one-time inputs)

def on_mouse_down(pos, button):
    if scene == 'menu':
        if button == mouse.LEFT:
            for i, b in enumerate(buttons):
                if b.collidepoint(pos):
                    if i == 0:
                        menu_levels

            if False:
                music.fadeout(1)
                bg_dy = 2
                # sounds.play() # TODO: click noise
                init_level(1) # temp

                # global thingy and level = 1
                #clock.schedule(init_level, 1)
    
    elif scene == 'level':
        #if button == mouse.LEFT:
            #pass
            # player_attack(pos)

        if button == mouse.RIGHT:
            animate(player, time_mod=0.2, duration=0.5)
            music.set_volume(0.5)
            player.fps *= 0.2
            for hazard in hazards:
                hazard.fps *= 0.2

def on_mouse_up(pos, button):
    if scene == 'menu':
        pass

    elif scene == 'level':
        if button == mouse.RIGHT:
            animate(player, time_mod=1, duration=0.5)
            music.set_volume(1)
            player.fps /= 0.2
            for hazard in hazards:
                hazard.fps /= 0.2

def on_mouse_move(pos, rel, buttons):
    pass

def on_key_down(key, unicode):
    if scene == 'menu':
        if key == keys.ESCAPE:
            sys.exit()

    if scene == 'level':
        if key in (keys.W, keys.SPACE) and player.jumps > 0:
            player.jumps -= 1
            player.dy = 30
        
        elif key == keys.S and player.vertical_reset:
            player.dy -= 30
            player.vertical_reset = False
        
        elif key == keys.LSHIFT: # shift could trigger sticky keys on Windows
            player_dash() # dash

def on_key_up(key):

    if scene == 'level':
        pass

def on_music_end():
    pass

# TODO implement controller events for button presses

# UPDATE

def update():
    if scene == 'menu':
        global bg_y, buttons

        # background movement
        bg_y -= bg_dy
        if bg_y <= -720:
            bg_y = 0
        
        for button in buttons:
            if button.collidepoint(pg.mouse.get_pos()):
                button.image = 'button_light'
            else:
                button.image = 'button_dark'
    
    elif scene == 'level':

        # Flipping

        if pg.mouse.get_pos()[0] >= player.x:
            player.flip_x = True
        else:
            player.flip_x = False


        # Gravity

        if not player.dashing:
            player.y -= player.dy * player.time_mod


        # Player Collision Detection

        for tile in tiles_clip:
            counter = 0

            while player.collide_pixel(tile):
                counter += 1
                if counter > 64:
                    player_reset()
                    break

                if player.x > tile.right and 'r' in tile.image:
                    player.x += 1
                    player.dx = 0
                    player.dashing = False
                elif player.x < tile.left and 'l' in tile.image.replace('tile', ''):
                    player.x -= 1
                    player.dx = 0
                    player.dashing = False
                
                if player.top < tile.top and 'u' in tile.image:
                    player.y -= 1
                    player.dx, player.dy = 0, 0 # stop movement
                    player.jumps = 2 # reset jumps

                elif player.bottom > tile.bottom and 'd' in tile.image:
                    player.y += 1
                    player.dy -= 1

        if player.collidelistall_pixel(hazards): # hazard collision detection
            player_die()
        
        player.dy -= gravity * player.time_mod

        if player.y > HEIGHT:
            player_reset()

        # Side movement

        if player.dx != 0:
            player.x += player.dx * player.time_mod

        else:
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
        # Moving background
        screen.blit(bg_image, (0, bg_y))
        screen.blit(bg_image, (0, bg_y + 720))
        screen.blit('text_title', (240, 0)) # title

        if screen == 'main': # main menu
            for button in main_buttons:
                button.draw()

        screen.draw.text('LEVELS', center=(640, 300), fontname="roboto_thin", fontsize=75, color="white")
        screen.draw.text('SETTINGS', center=(640, 450), fontname="roboto_thin", fontsize=75, color="white")
        screen.draw.text('QUIT', center=(640, 600), fontname="roboto_thin", fontsize=75, color="white")
        
    
    elif scene == 'level':
        screen.blit(bg_image, (0, bg_y))


        for tile in (tiles_clip + tiles_back):
            tile.draw()

        for tile in hazards:
            tile.scale = 2
            tile.draw()
            #tile.animate()

        player.draw()

        for tile in tiles_front:
            tile.draw()


# Scheduling and Go:

init_menu()
pgzrun.go()