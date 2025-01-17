# ULTRAKOOL
# A really cool combat platformer game
# Noah Verdon
# Last Edited: January 17, 2024

import pgzrun, os, random, sys, pygame as pg
from pgzhelper import *
from levels import *


# SETTINGS

# Standard Settings
os.environ["SDL_VIDEO_CENTERED"] = "1" # center the window
WIDTH, HEIGHT = 1280, 704 # game resolution: 1280 x 704
TITLE = "ULTRAKOOL"

# Saved Settings TODO: hook up custom settings
levels_unlocked = [True, True, True, False]
joystick_drift = 0.1
music.set_volume(0)
instant_respawn = False

# Controller Support
if pygame.joystick.get_count() == 1:
    controller_mode = True
    joystick = pg.joystick.Joystick(0)
    pygame.mouse.set_visible(False) # hide cursor in controller mode
else:
    controller_mode = False

# Temporary Values
# player = None TODO
level = None


# Initialize Unchanging Global Variables

# Global
# menu = True BUG

# Menu
buttons_main = [Actor('button_dark', center=(640, 300 + 150 * i)) for i in range(3)] # main menu

buttons_levels = [] # levels menu
for coord in ((380, 350), (900, 350), (380, 500), (900, 500)): # 250, 400, 550 for 3 vertical
    buttons_levels.append(Actor('button_dark', center=(coord)))

buttons_settings = [Actor('button_dark', center=(640, 300 + 150 * i)) for i in range(0)] # settings menu

buttons_dict = {'main': buttons_main, 'levels': buttons_levels, 'settings': buttons_settings}


# CLASSES

class Player(Actor): # Player is a child class of Actor
    def __init__(self, image):
        super().__init__(image) # inherit Actor

        # Attributes
        self.animation = None
        self.time_mod = 1
        self.input = True

        self.spawn = (0, 0)
        self.dx, self.dy = 0, 0
        self.mx, self.my = 0, 0
        self.hitbox = Rect((0,0), (60, 48))

        # Abilities
        self.gravity = True
        self.jumps = 2

        self.can_jump = True
        self.can_boost = True
        self.can_dash = True
        self.can_attack = True
        self.can_overclock = True

    # Methods

    def switch_animation(self, animation: str, reverse=False):
        '''Allow the player to dynamically change animations.'''
        animation_length = {'idle': 5, 'walk': 6, 'attack': 15, 'hit': 4, 'death': 8}
        animation_fps = {'idle': 10, 'walk': 12, 'attack': 7.5, 'hit': 8, 'death': 4}

        if self.animation != animation:
            self.animation = animation
            self.fps = animation_fps[animation] * self.time_mod
  
            if reverse:
                self.images = [f'microwave_{animation}_{x}' for x in range(animation_length[animation]-1, -1, -1)] # option to animate backwards
            else:
                self.images = [f'microwave_{animation}_{x}' for x in range(0, animation_length[animation])]

    def respawn(self):
        '''Respawns the player.'''
        self.hitbox.center = self.spawn
        self.touch_ground()

    def touch_ground(self):
        '''Resets some attributes upon the player hitting the ground.'''
        self.can_boost = True
        self.can_jump = True
        self.gravity = True
        self.jumps = 2
        self.dx, self.dy = 0, 0

    def die(self):
        '''Kills the player'''
        # BUG self.alive??
        self.input = False
        self.switch_animation('death')

        # BUG reset time_mod maybe instead
        if time_modded:
            self.time_mod = 1
            self.overclock_end()
    
    # Walking

    def step_left(self):
        '''Step the player left by 10 pixels.'''
        player.hitbox.x -= 10 * player.time_mod
        player.switch_animation('walk', reverse=(True if player.flip_x else False)) # reversing list can get rid of moonwalking effect

    def step_right(self):
        '''Step the player right by 10 pixels.'''
        player.hitbox.x += 10 * player.time_mod
        player.switch_animation('walk', reverse=(False if player.flip_x else True)) # reversing list can get rid of moonwalking effect

    # Jump

    def jump(self):
        '''Jumping functionality by changing dy.'''
        self.jumps -= 1
        self.dy = -18

    # Boost

    def boost(self):
        '''Boost ability by changing dy.'''
        self.can_boost = False
        if self.dy < 12:
                self.dy += 20
        else:
            self.dy = 32 # BUG

    # Attack

    def attack(self, pos: tuple):
        '''Attack a position specified by a mouse click.'''
        global attacks

        self.animate('attack')
        self.gravity, self.input = False, False
        self.can_attack = False

        new_attack = Actor('attack_0', self.hitbox.center)
        new_attack.images = [f'attack_{i}' for i in range(5)]
        new_attack.direction = self.direction_to(pos)
        new_attack.angle = self.direction_to(pos) + 180

        attacks.append(new_attack)

        clock.schedule(self.attack_end, 0.5)
        clock.schedule(self.attack_cooldown, 1)

    def attack_end(self):
        '''Give back player controls.'''
        self.gravity, self.input = True, True
        self.dx, self.dy = 0, 0

    def attack_cooldown(self):
        '''Let the player attack again.'''
        self.can_attack = True

    # Dash

    def dash(self):
        '''Animates dx, disables controls, and schedules a cooldown for the ability.'''
        self.gravity, self.input = False, False
        self.can_dash = False
        self.dy = 0

        dash_duration = 0.05 / self.time_mod # BUG
        if keyboard.a and not keyboard.d:
            animate(self, dx=-55, duration=dash_duration, tween='linear')
        elif keyboard.d and not keyboard.a:
            animate(self, dx=55, duration=dash_duration, tween='linear')
        elif self.flip_x:
            animate(self, dx=55, duration=dash_duration, tween='linear')
        else:
            animate(self, dx=-55, duration=dash_duration, tween='linear')

        clock.schedule(self.dash_mid, dash_duration * 2)
        clock.schedule(self.dash_end, dash_duration * 5)
        clock.schedule(self.dash_cooldown, 0.5 / self.time_mod)

    def dash_mid(self):
        '''Pause the player in midair after dashing by setting dx to zero.'''
        self.dx = 0

    def dash_end(self):
        '''Give back player controls.'''
        self.gravity, self.input = True, True

    def dash_cooldown(self):
        '''Let the player dash again.'''
        self.can_dash = True

    # Overclock

    def overclock(self):
        '''Animate time_mod to the slow game.'''
        global time_modded
        time_modded = True # TODO remove

        animate(self, time_mod=0.2, duration=0.5)
        self.fps *= 0.2
        for tile in tiles_animate:
            tile.fps *= 0.2

        music.set_volume(music.get_volume() / 2)

    def overclock_end(self):
        '''Animate time_mod to return the game to normal speed.'''
        global time_modded
        time_modded = False

        animate(self, time_mod=1, duration=0.5)
        self.fps /= 0.2
        for tile in tiles_animate:
            tile.fps /= 0.2

        music.set_volume(music.get_volume() * 2)


class Trigger:
    def __init__(self, name, x, y):
        self.rect = Rect((32*x, 32*y), (32, 32))
        self.name = name
        triggers.append(self)
    
    def use(self):
        '''Trigger an action and add the trigger name to a set.'''
        used_triggers.add(self.name)

        if self.name == 'overclock':
            player.can_overclock = True
        elif self.name == 'attack':
            player.can_attack = True


class Entities: # TODO
    def __init__(self):
        self.attacks = None


# FUNCTIONS

def init_menu():
    '''Initializes the menu scene.'''
    global menu, bg_menu, bg_y, bg_dy, menu_scene

    menu = True
    menu_scene = 'main'
    bg_menu = f'background_space_{random.randint(0, 9)}'
    bg_y, bg_dy = 0, 0.25
    music.play('intro')


def init_level():
    '''Initializes the current level.'''
    global menu, current_scene, bg_levels, bg_y, bg_dy, time_modded, attacks, used_triggers

    menu = False
    bg_levels = 'background_levels'
    bg_y, bg_dy = 0, 0
    time_modded = False
    attacks = []
    used_triggers = set()
    
    player = Player('microwave_idle_0')
    if level == 0: # level 1 prohibits some functionality to start
        player.can_attack, player.can_overclock = False, False

    player.alive = True # BUG

    current_scene = check_level_scene(player.mx, player.my)
    switch_level_scene(current_scene)
    music.fadeout(1) # TODO
    music.play('song_7')


def check_level_scene(mx: int, my: int): # TODO
    #'''Checks if the specified scene is a part of the current level. Returns 0, 0 if it is not.''' TODO

    #in_level_bounds = False
    for scene in levels[level]:
        if scene.mx == mx and scene.my == my:
            return scene
            #in_level_bounds = True
            break
    
    if not in_level_bounds: # TODO maybe change respawning
        found_scene = 0, 0
        #player.mx, player.my = 0, 0 # TODO remove!
        player.respawn()
    
    new_scene = levels[level][0]
    return new_scene


def switch_level_scene(scene: Scene):
    '''Initializes a new scene to display in a level.'''
    global triggers # TODO make not global

    #if time_modded: # BUG maybe...
     #   player.time_mod = 0.2 TODO maybe use simple_time_mod instead
      #  player.overclock()

    player = Player('microwave_idle_0')

    triggers = []
    for y, row in enumerate(scene.map):
        for x, tile in enumerate(row):
            tile_name = tile_unicode_dict[tile]

            if tile_name == 'air':
                pass
            
            elif tile_name == 'player_spawn':
                player.spawn = (32 * x + 16,  32 * y + 16)
            
            elif 'trigger' in tile_name:
                Trigger(tile_name.replace('trigger_', ''), x, y)

            else:
                manage_tile(tile_name, x, y)


def manage_tile(name: str, x: int, y: int):
    '''Configures lists of tiles within a scene.'''
    global tiles_clip, tiles_front, tiles_back, tiles_animate, hazards
    tiles_clip, tiles_front, tiles_back, tiles_animate, hazards = [], [], [], [], []

    new_tile = Actor(f'tile_{name}', (32 * x + 16, 32 * y + 16))
    new_tile.scale = 2

    if 'spike' in name or 'water' in name:
        new_tile.images = [f'tile_{name[:-1]}{i}' for i in range(6 if 'water' in name else 8)]
        new_tile.fps = (6 if 'water' in name else 8) * player.time_mod # TODO USE simple_time_mod that only is 0.2 or 1
        tiles_animate.append(new_tile)
        hazards.append(new_tile)
    
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


# Event Handlers (one-time inputs)

def on_mouse_down(pos, button):
    if menu:
        global menu_scene, level

        if button == mouse.LEFT:
            for i, b in enumerate(buttons_dict[menu_scene]):
                if b.collidepoint(pos):
                    if menu_scene == 'main':
                        if i == 0:
                            menu_scene = 'levels'
                        elif i == 1:
                            menu_scene = 'settings'
                        elif i == 2:
                            pg.quit()
                            sys.exit()

                    elif menu_scene == 'levels':
                        if levels_unlocked[i]:
                            level = i
                            init_level()

    else:
        if player.input:
            if button == mouse.LEFT and player.can_attack:
                player.attack(pos)

            if button == mouse.RIGHT and player.can_overclock:
                player.overclock()


def on_mouse_up(pos, button):
    if menu:
        pass

    else:
        if player.input:
            if button == mouse.RIGHT and player.time_mod_simple == 0.2:
                player.overclock_end()


def on_mouse_move(pos, rel, buttons):
    pass


def on_key_down(key, unicode):
    if menu:
        global menu_scene

        if key == keys.ESCAPE:
            if menu_scene in ('levels', 'settings'):
                menu_scene = 'main'

    else:
        if player.input:
            if key in (keys.W, keys.SPACE) and player.can_jump and player.jumps > 0:
                player.jump()
            
            elif key == keys.S and player.can_boost:
                player.boost()
            
            elif key == keys.LSHIFT and player.can_dash: # shift could trigger sticky keys on Windows
                player.dash()
            
        if key == keys.R and not player.alive: # TODO alive stuff
            init_level(level)


def on_key_up(key):
    pass


def on_music_end():
    pass


# TODO implement controller events for button presses


# UPDATE

def update():
    if menu:
        global bg_y

        # Background movement
        bg_y -= bg_dy
        if bg_y <= -720:
            bg_y = 0

        # Button color response
        for button in buttons_dict[menu_scene]:
                if button.collidepoint(pg.mouse.get_pos()):
                    button.image = 'button_light'
                else:
                    button.image = 'button_dark'
        
    else:
        # Player

        if player.input:
            # Flipping
            if pg.mouse.get_pos()[0] >= player.x:
                player.flip_x = True
            else:
                player.flip_x = False

            # Walking
            walking = False
            if keyboard.a:
                player.step_left()
                walking = True
            elif controller_mode:
                if joystick.get_axis(0) < -joystick_drift:
                    player.step_left()
                    walking = True
            
            if keyboard.d:
                player.step_right()
                walking = True
            elif controller_mode:
                if joystick.get_axis(0) > joystick_drift:
                    player.step_right()
                    walking = True
            
            if not walking:
                player.switch_animation('idle')
        
        # dx and dy
        player.hitbox.x += player.dx * player.time_mod

        if player.gravity:
            player.hitbox.y += player.dy * player.time_mod

        if player.dy < 32 * player.time_mod: # BUG
            player.dy += 1.1 * player.time_mod # gravity value of 1.1

        # Player Collision Detection

        down_boost = False
        for tile in tiles_clip: # up and down
            counter = 0
            while tile.colliderect(player.hitbox):
                counter += 1
                if counter > 64:
                    break

                if (player.hitbox.top + 15 < tile.top) and 'u' in tile.image: # top + 15 is the minimum height for auto-jumping
                    player.hitbox.y -= 1
                    player.touch_ground() # change various player attributes when touching the ground

                elif player.hitbox.bottom - 20 > tile.bottom and 'd' in tile.image:
                    player.hitbox.y += 1
                    down_boost = True
        
        for tile in tiles_clip: # left and right
            counter = 0
            while tile.colliderect(player.hitbox): # left and right
                counter += 1
                if counter > 64:
                    player.respawn()
                    break

                if player.hitbox.left < tile.right and 'r' in tile.image.replace('water', ''):
                    player.hitbox.x += 1
                    player.dx = 0

                elif player.hitbox.right > tile.left and 'l' in tile.image.replace('tile', ''):
                    player.hitbox.x -= 1
                    player.dx = 0
        
        if down_boost: #and player.dy > 0: TODO
            player.dy -= player.dy * 1.1 # maybe change this TODO

        # Hazards and Triggers

        for hazard in hazards:
            if hazard.colliderect(player.hitbox) and player.alive: # hazard collision detection
                player.die()

            counter = 0
            while hazard.colliderect(player.hitbox):
                counter += 1
                if counter > 64:
                    break

                if player.hitbox.top < hazard.top and 'water' in hazard.image:
                    player.hitbox.y -= 1
                    player_ground_reset()
        
        for trigger in triggers:
            if trigger.rect.colliderect(player.hitbox) and trigger.name not in used_triggers:
                use_trigger(trigger.name)

        switch_scene = True
        if player.hitbox.centerx > WIDTH:
            player.hitbox.x -= WIDTH
            player.mx += 1
        elif player.hitbox.centerx < 0:
            player.hitbox.x += WIDTH
            player.mx -= 1
        elif player.hitbox.centery > HEIGHT:
            player.hitbox.y -= HEIGHT
            player.my -= 1
        elif player.hitbox.centery < 0:
            player.hitbox.y += HEIGHT
            player.my += 1
        else:
            switch_scene = False
        
        if switch_scene:
            player.pos = player.hitbox.center
            switch_level_scene()

        #global attacks
        for attack in attacks:
            attack.move_in_direction(5 * player.time_mod)
            attack.scale = True
            if attack.collidelistall_pixel(tiles_clip):
                attacks.remove(attack)

        player.pos = (player.hitbox.x + 30, player.hitbox.y)
        player.scale = 2
        player.animate()

        for attack in attacks:
            attack.animate()
        
        # Tiles

        for tile in tiles_animate:
            tile.scale = 2
            tile.animate()


# DRAW

def draw():
    screen.clear()

    if menu:
        # Moving background
        screen.blit(bg_menu, (0, bg_y))
        screen.blit(bg_menu, (0, bg_y + 720))

        screen.blit('text_title', (0, 0)) # title

        if menu_scene == 'main': # main menu
            for button in buttons_main:
                button.draw()
            
            for i in range(3):
                screen.draw.text(('LEVELS', 'SETTINGS', 'QUIT')[i], center=buttons_main[i].pos, fontname='roboto_thin', fontsize=75, color=('white' if buttons_main[i].image == 'button_dark' else 'black'))
        
        elif menu_scene == 'levels': # levels menu
            for button in buttons_levels:
                button.draw()

            for i in range(4):
                if levels_unlocked[i]:
                    screen.draw.text(f'LEVEL {i + 1}', center=buttons_levels[i].pos, fontname='roboto_thin', fontsize=75, color=('white' if buttons_levels[i].image == 'button_dark' else 'black'))
                else:
                    screen.draw.text(f'???', center=buttons_levels[i].pos, fontname='roboto_thin', fontsize=75, color=('white' if buttons_levels[i].image == 'button_dark' else 'black'))
            
            screen.draw.text('ESC TO GO BACK', center=(640, 650), fontname='roboto_thin', fontsize=40, color='white')

        elif menu_scene == 'settings': # settings menu
            for button in buttons_settings:
                button.draw()
            
            screen.draw.text('ESC TO GO BACK', center=(640, 650), fontname='roboto_thin', fontsize=40, color='white')
    
    else:
        # Behind entities
        screen.blit(bg_levels, (0, 0))
        
        for tile in (tiles_back + tiles_animate):
            tile.draw()
        
        for tile in (tiles_clip):
            tile.draw()

        # Level Text
        for text in current_scene.text:
            screen.draw.text(text.message, center=(text.x, text.y), fontname='vcr_ocd_mono', fontsize=32, color=text.color)

        # Entities
        #screen.draw.rect(player.hitbox, 'RED') # only for debug
        player.draw()

        for attack in attacks:
            attack.draw()

        # In front of entities
        for tile in tiles_front:
            tile.draw()

        # Death screen
        #if not player.alive: TODO
         #   pass


# START

player = Player('microwave_idle_0') # BUG
init_menu()
pgzrun.go()