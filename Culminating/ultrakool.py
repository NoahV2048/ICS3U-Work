# ULTRAKOOL
# A really cool combat platformer game
# Noah Verdon
# Last Edited: TBD

import pgzrun, os, random, sys, pygame as pg
from pgzhelper import *
from levels import *

# Standard Settings
os.environ["SDL_VIDEO_CENTERED"] = "1" # center the window
WIDTH, HEIGHT = 1280, 704 # game resolution: 1280 x 720 (16:9)
TITLE = "ULTRAKOOL"

# Standard Pygame Settings
# pg.mouse.set_cursor(*pygame.cursors.broken_x) # TODO


# Saved Settings # TODO: hook up custom settings

levels_unlocked = [True, True, False, False]
joystick_drift = 0.1
music.set_volume(0)


# Controller Support

if pygame.joystick.get_count() == 1:
    joystick = pg.joystick.Joystick(0)
    controller_mode = True
    pygame.mouse.set_visible(False) # hide cursor in controller mode
else:
    controller_mode = False


# Initialize Global Variables (That Don't Change)

# Global
scene = None

# Menu
buttons_main = [Actor('button_dark', center=(640, 300 + 150 * i)) for i in range(3)] # main screen

buttons_levels = [] # levels screen
for coord in ((380, 350), (900, 350), (380, 500), (900, 500)): # 250, 400, 550 for 3 vertical
    buttons_levels.append(Actor('button_dark', center=(coord)))

buttons_settings = [Actor('button_dark', center=(640, 300 + 150 * i)) for i in range(0)] # settings screen

buttons_dict = {'main': buttons_main, 'levels': buttons_levels, 'settings': buttons_settings}

# Levels
player = Actor('microwave_idle_0')
gravity = 1.1
player_animate_info = {'idle': 5, 'walk': 6, 'attack': 15, 'hit': 4, 'death': 8}


# Classes

class Trigger:
    def __init__(self, name, x, y):
        self.rect = Rect((32*x, 32*y), (32, 32))
        self.name = name
        triggers.append(self)


# Scene and Screen Initializations

def init_menu():
    '''Initializes the menu scene.'''
    global scene, bg_menu, bg_y, bg_dy, menu_screen

    scene = 'menu'
    menu_screen = 'main'
    bg_menu = f'background_space_{random.randint(0, 9)}'
    bg_y, bg_dy = 0, 0.25
    # music.play('intro')

def init_level(num):
    global scene, bg_levels, bg_y, bg_dy, attacks, time_modded, level, used_triggers

    scene = 'level'
    bg_levels = 'background_levels'
    bg_y, bg_dy = 0, 0
    time_modded = False
    level = num - 1
    attacks = []
    used_triggers = set()

    player.state = None
    player.alive = True
    player.can_dash = True
    player.static = False
    player.mx, player.my = 0, 0
    player.time_mod = 1

    player.can_overclock, player.can_attack = (False, True) if num == 1 else (True, True) # level 1 prohibits some functionality
    
    player_animate('idle')

    switch_level_screen()
    player_reset()

    #music.fadeout(1)
    #music.play('song_7')

def switch_level_screen():
    global tiles_clip, tiles_front, tiles_back, hazards, tiles_animate, triggers, floating_text
    tiles_clip, tiles_front, tiles_back, hazards, tiles_animate, triggers = [], [], [], [], [], []

    if time_modded: # BUG maybe...
        player.time_mod = 0.2
        time_mod_start()

    if f'{player.mx},{player.my}' not in levels[level].keys():
        player.mx, player.my = 0, 0
        clock.schedule(player_reset, 1/60)

    for i, row in enumerate(levels[level][f'{player.mx},{player.my}']):
        for j, tile in enumerate(row):
            name = tile_unicode_dict[tile]

            if name == 'air':
                pass
            
            elif name == 'player_spawn':
                player.spawn = (32*j, 32*i)
            
            elif 'trigger' in name:
                Trigger(name.replace('trigger_', ''), j, i)

            else:
                new_tile = Actor(f'tile_{name}')

                if 'spike' in name:
                    new_tile.images = [f'tile_{name[:-1]}{i}' for i in range(6)]
                    new_tile.fps = 8 * player.time_mod
                    hazards.append(new_tile)
                    tiles_animate.append(new_tile)

                elif name == 'water_0':
                    new_tile.images = [f'tile_{name[:-1]}{i}' for i in range(4)]
                    new_tile.fps = 6 * player.time_mod
                    hazards.append(new_tile)
                    tiles_animate.append(new_tile)
                
                elif name == 'warning_0':
                    new_tile.images = [f'tile_{name[:-1]}{i}' for i in range(9)]
                    new_tile.fps = 18 * player.time_mod
                    tiles_animate.append(new_tile)

                elif name[0].isdecimal():
                    tiles_clip.append(new_tile)

                elif 'floor' in name or 'ceil' in name or 'side' in name:
                    tiles_front.append(new_tile)

                else:
                    tiles_back.append(new_tile)

                new_tile.center=(32*j+16, 32*i+16)
                new_tile.scale = 2
                if 'big' in name:
                    new_tile.scale = 3
    
    floating_text = []
    if f'{player.mx},{player.my}' in level_text[level].keys(): # level text
        floating_text = level_text[level][f'{player.mx},{player.my}']

def use_trigger(name):
    global used_triggers
    used_triggers.add(name)

    if name == 'overclock':
        player.can_overclock = True

# Player Functions

def player_animate(arg: str, reverse=False) -> None:
    if player.state != arg:
        player.state = arg
        frames = player_animate_info[arg]
        player.fps = frames * 2 * player.time_mod

        if arg == 'dying':
            player.images = ['microwave_idle_1', 'microwave_death_0']
        elif arg == 'death':
            player.images = [f'microwave_{arg}_{x}' for x in range(1, frames)]
            player.fps /= 2
        elif arg == 'attack':
            player.images = [f'microwave_{arg}_{x}' for x in range(1, frames)]
            player.fps /= 4
        else:
            if reverse:
                player.images = [f'microwave_{arg}_{x}' for x in range(frames-1, -1, -1)] # option to animate backwards
            else:
                player.images = [f'microwave_{arg}_{x}' for x in range(0, frames)]
            
def player_reset():
    player.pos = player.spawn
    player_ground_reset()

def player_ground_reset():
    player.can_vertical_reset = True
    player.dashing = False
    player.dx, player.dy = 0, 0
    player.jumps = 2

def player_attack(pos):
    global attacks

    player_animate('attack')
    player.can_attack = False

    new_attack = Actor('attack_0', ())
    new_attack.images = [f'attack_{i}' for i in range(5)]
    new_attack.pos = player_hitbox.center
    new_attack.dy = player.dy

    new_attack.direction = player.direction_to(pos)
    new_attack.angle = player.direction_to(pos) + 180

    attacks.append(new_attack)

    if not player.flip_x:
        player.dx = 1
        #new_attack.direction = 180
        #new_attack.flip_x
    else:
        player.dx = -1

    player.dashing = True

    clock.schedule(player_attack_end, 1)

def player_attack_end():
    player.can_attack = True
    player.dashing = False
    player.dx, player.dy = 0, 0

def player_die():
    player.alive = False
    player.static = True
    if time_modded:
        player.time_mod = 1
        time_mod_end()
    player_animate('death')

def player_dash():
    player.dashing = True
    player.can_dash = False
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
    clock.schedule(player_dash_cooldown, 0.5 / player.time_mod)

def player_dash_mid():
    player.dx, player.dy = 0, 0

def player_dash_end():
    player.dashing = False

def player_dash_cooldown():
    player.can_dash = True

def time_mod_start():
    global time_modded
    time_modded = True

    animate(player, time_mod=0.2, duration=0.5)
    music.set_volume(music.get_volume() / 2)
    player.fps *= 0.2
    for tile in tiles_animate:
        tile.fps *= 0.2

def time_mod_end():
    global time_modded
    time_modded = False
    animate(player, time_mod=1, duration=0.5)
    music.set_volume(music.get_volume() * 2)
    player.fps /= 0.2
    for tile in tiles_animate:
        tile.fps /= 0.2


# Event Handlers (one-time inputs)

def on_mouse_down(pos, button):
    if scene == 'menu':
        global menu_screen

        if button == mouse.LEFT:
            for i, b in enumerate(buttons_dict[menu_screen]):
                if b.collidepoint(pos):
                    if menu_screen == 'main':
                        if i == 0:
                            menu_screen = 'levels'
                        elif i == 1:
                            menu_screen = 'settings'
                        elif i == 2:
                            sys.exit()
    
                    elif menu_screen == 'levels':
                        if levels_unlocked[i]:
                            init_level(i + 1)

                        if False:
                            music.fadeout(1)
                            bg_dy = 2
                            # sounds.play() # TODO: click noise
                            init_level(1) # temp

                            # global thingy and level = 1
                            #clock.schedule(init_level, 1)
    
    elif scene == 'level':
        if button == mouse.LEFT and player.can_attack:
            player_attack(pos)

        if button == mouse.RIGHT and not time_modded and not player.static and player.can_overclock:
            time_mod_start()

def on_mouse_up(pos, button):
    if scene == 'menu':
        pass

    elif scene == 'level':
        if button == mouse.RIGHT and time_modded and not player.static:
            time_mod_end()

def on_mouse_move(pos, rel, buttons):
    pass

def on_key_down(key, unicode):
    if scene == 'menu':
        global menu_screen

        if key == keys.ESCAPE:
            if menu_screen in ('levels', 'settings'):
                menu_screen = 'main'

    if scene == 'level':
        if key in (keys.W, keys.SPACE) and player.jumps > 0 and not player.static:
            player.jumps -= 1
            player.dy = 18
        
        elif key == keys.S and player.can_vertical_reset and not player.static:
            if player.dy > -32:
                player.dy -= 32
            else:
                player.dy = -48
            player.can_vertical_reset = False
        
        elif key == keys.LSHIFT and player.can_dash and not player.static: # shift could trigger sticky keys on Windows
            player_dash() # dashing gets a unique function due to its complexity
        
        elif key == keys.R and not player.alive:
            init_level(1)

def on_key_up(key):

    if scene == 'level':
        pass

def on_music_end():
    pass

# TODO implement controller events for button presses

# UPDATE

def update():
    if scene == 'menu':
        global bg_y

        # Background movement
        bg_y -= bg_dy
        if bg_y <= -720:
            bg_y = 0

        # Button color response
        for button in buttons_dict[menu_screen]:
                if button.collidepoint(pg.mouse.get_pos()):
                    button.image = 'button_light'
                else:
                    button.image = 'button_dark'
    
    elif scene == 'level':
        global player_hitbox
        player_hitbox = Rect((player.x - 30, player.y - 0), (60, 48))

        # Tiles

        for tile in tiles_animate:
            tile.scale = 2
            tile.animate()

        # Flipping

        if not player.static:
            if pg.mouse.get_pos()[0] >= player.x:
                player.flip_x = True
            else:
                player.flip_x = False

        # Player Movement

        if not player.dashing:
                player_hitbox.y -= player.dy * player.time_mod # gravity

        if player.dy > -48 * player.time_mod:
            player.dy -= gravity * player.time_mod
        
        if player.dx != 0 or player.static:
            player_hitbox.x += player.dx * player.time_mod

        else:
            if keyboard.a: #or joystick.get_axis(0) < -joystick_drift: TODO
                player_hitbox.x -= 10 * player.time_mod

                reverse = False
                if player.flip_x:
                    reverse = True

                player_animate('walk', reverse=reverse) # reversing list gets rid of moonwalking effect
                
            if keyboard.d: #or joystick.get_axis(0) > joystick_drift: TODO
                player_hitbox.x += 10 * player.time_mod

                reverse = True
                if player.flip_x:
                    reverse = False
                player_animate('walk', reverse=reverse) # reversing list gets rid of moonwalking effect
            
            if not (keyboard.a or keyboard.d): # (joystick.get_axis(0) < -joystick_drift or joystick.get_axis(0) > joystick_drift): TODO
                player_animate('idle')

        # Player Collision Detection

        down_boost = False
        for tile in tiles_clip: # up and down
            counter = 0
            while tile.colliderect(player_hitbox):
                counter += 1
                if counter > 64:
                    break

                if player_hitbox.top < tile.top and 'u' in tile.image: # TODO MAYBE CHANGE TO <=
                    player_hitbox.y -= 1
                    player_ground_reset() # change various player attributes when touching the ground

                elif player_hitbox.bottom > tile.bottom and 'd' in tile.image:
                    player_hitbox.y += 1
                    down_boost = True
            
            counter = 0
            while tile.colliderect(player_hitbox): # left and right
                counter += 1
                if counter > 64:
                    player_reset()
                    break

                if player_hitbox.left < tile.right and 'r' in tile.image.replace('water', ''):
                    player_hitbox.x += 1
                    #player.dx = 0
                    player.dashing = False

                elif player_hitbox.right > tile.left and 'l' in tile.image.replace('tile', ''):
                    player_hitbox.x -= 1
                    #player.dx = 0
                    player.dashing = False

        # Hazards and Triggers

        for hazard in hazards:
            if hazard.colliderect(player_hitbox) and player.alive: # hazard collision detection
                player_die()

            counter = 0
            while hazard.colliderect(player_hitbox):
                counter += 1
                if counter > 64:
                    break

                if player_hitbox.top < hazard.top and 'water' in hazard.image:
                    player_hitbox.y -= 1
                    player_ground_reset()
        
        for trigger in triggers:
            if trigger.rect.colliderect(player_hitbox) and trigger.name not in used_triggers:
                use_trigger(trigger.name)
        
        if down_boost and player.dy > 0:
            player.dy -= player.dy * 1.1

        switch_screen = True
        if player_hitbox.centerx > WIDTH:
            player_hitbox.x -= WIDTH
            player.mx += 1
        elif player_hitbox.centerx < 0:
            player_hitbox.x += WIDTH
            player.mx -= 1
        elif player_hitbox.centery > HEIGHT:
            player_hitbox.y -= HEIGHT
            player.my -= 1
        elif player_hitbox.centery < 0:
            player_hitbox.y += HEIGHT
            player.my += 1
        else:
            switch_screen = False
        
        if switch_screen:
            player.pos = player_hitbox.center
            switch_level_screen()

        for attack in attacks:
            attack.move_in_direction(5 * player.time_mod)
            attack.scale = True

        player.pos = (player_hitbox.x + 30, player_hitbox.y)
        player.scale = 2
        player.animate()

        for attack in attacks:
            attack.animate()


# DRAW

def draw():
    screen.clear()

    if scene == 'menu':
        # Moving background
        screen.blit(bg_menu, (0, bg_y))
        screen.blit(bg_menu, (0, bg_y + 720))

        screen.blit('text_title', (0, 0)) # title

        if menu_screen == 'main': # main menu
            for button in buttons_main:
                button.draw()
            
            for i in range(3):
                screen.draw.text(('LEVELS', 'SETTINGS', 'QUIT')[i], center=buttons_main[i].pos, fontname='roboto_thin', fontsize=75, color=('white' if buttons_main[i].image == 'button_dark' else 'black'))
        
        elif menu_screen == 'levels': # levels menu
            for button in buttons_levels:
                button.draw()

            for i in range(4):
                if levels_unlocked[i]:
                    screen.draw.text(f'LEVEL {i + 1}', center=buttons_levels[i].pos, fontname='roboto_thin', fontsize=75, color=('white' if buttons_levels[i].image == 'button_dark' else 'black'))
                else:
                    screen.draw.text(f'???', center=buttons_levels[i].pos, fontname='roboto_thin', fontsize=75, color=('white' if buttons_levels[i].image == 'button_dark' else 'black'))
            
            screen.draw.text('ESC TO GO BACK', center=(640, 650), fontname='roboto_thin', fontsize=40, color='white')

        elif menu_screen == 'settings': # settings menu
            for button in buttons_settings:
                button.draw()
            
            screen.draw.text('ESC TO GO BACK', center=(640, 650), fontname='roboto_thin', fontsize=40, color='white')
    
    elif scene == 'level':

        # Behind entities
        screen.blit(bg_levels, (0, 0))
        
        for tile in (tiles_back + tiles_animate):
            tile.draw()
        
        for tile in (tiles_clip):
            tile.draw()

        # Level Text
        for text in floating_text:
            if len(text) == 4:
                col = text[3]
            else:
                col = 'white'
            screen.draw.text(text[0], center=(text[1] * 32 + 16, text[2] * 32 + 16), fontname='vcr_ocd_mono', fontsize=32, color=col)

        # Entities
        #screen.draw.rect(player_hitbox, 'RED') # only for debug
        player.draw()

        for attack in attacks:
            attack.draw()

        # In front of entities
        for tile in tiles_front:
            tile.draw()

        # Death screen
        if not player.alive:
            pass


# Start Game

init_menu()
pgzrun.go()