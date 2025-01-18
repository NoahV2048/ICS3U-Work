# ULTRAKOOL
# A really cool combat platformer game
# Noah Verdon
# Last Edited: January 17, 2024

import pgzrun, os, random, sys, pygame as pg
from pgzhelper import *
from levels import *


# CLASSES

class Player(Actor): # Player is a child class of Actor
    def __init__(self, image):
        super().__init__(image) # inherit Actor

        # Attributes
        self.animation = None
        self.time_mod, self.time_mod_simple = 1, 1
        self.input = True
        self.alive = True

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

        # Animations
        self.animation_dash = None
        self.animation_overclock = None

    # Methods

    def switch_animation(self, animation: str, reverse=False):
        '''Allow the player to dynamically change animations.'''
        animation_length = {'idle': 5, 'walk': 6, 'attack': 15, 'hit': 4, 'death': 7}
        animation_fps = {'idle': 10, 'walk': 12, 'attack': 15, 'hit': 8, 'death': 4}

        if self.animation != animation:
            self.animation = animation
            self.fps = animation_fps[animation] * self.time_mod_simple
  
            if reverse:
                self.images = [f'microwave_{animation}_{x}' for x in range(animation_length[animation]-1, -1, -1)] # option to animate backwards
            else:
                self.images = [f'microwave_{animation}_{x}' for x in range(0, animation_length[animation])]

    # Death and Resetting

    def die(self):
        '''Kills the player and cancels various actions.'''
        self.attack_cancel()
        self.dash_cancel()
        self.overclock_cancel()

        self.alive = False
        self.input = False
        self.switch_animation('death')

        if instant_respawn:
            if hard_mode:
                init_level()
            else:
                self.respawn()

    def respawn(self):
        '''Respawns the player.'''
        player.alive = True
        player.input = True
        self.hitbox.center = self.spawn
        self.touch_ground()

        current_scene.attacks = []
        current_scene.enemies = []
    
    def touch_ground(self):
        '''Resets some attributes upon the player hitting the ground.'''
        self.can_boost = True
        self.can_jump = True
        self.gravity = True
        self.jumps = 2
        self.dx, self.dy = 0, 0
    
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
        self.switch_animation('attack')
        self.gravity, self.input = False, False
        self.can_attack = False

        new_attack = Actor('attack_0', self.hitbox.center)
        new_attack.images = [f'attack_{i}' for i in range(5)]
        new_attack.direction = self.direction_to(pos)
        new_attack.angle = self.direction_to(pos) + 180

        current_scene.attacks.append(new_attack)
        self.overclock_cancel() # make attacking and overclocking exclusive BUG

        clock.schedule(self.attack_end, 0.5)
        clock.schedule(self.attack_cooldown, 1)

    def attack_end(self):
        '''Give back player controls.'''
        self.gravity, self.input = True, True
        self.dx, self.dy = 0, 0

    def attack_cooldown(self):
        '''Let the player attack again.'''
        self.can_attack = True
    
    def attack_cancel(self):
        '''Call and unschedule attack termination.'''
        self.attack_end()
        self.attack_cooldown()
        clock.unschedule(self.attack_end)
        clock.unschedule(self.attack_cooldown)

    # Dash

    def dash(self):
        '''Animates dx, disables controls, and schedules a cooldown for the ability.'''
        self.gravity, self.input = False, False
        self.can_dash = False
        self.dy = 0

        self.overclock_cancel() # make dashing and overclocking exclusive

        dash_duration = 0.05 / self.time_mod_simple # no reason to multiply by time_mod_simple unless functionality is changed later
        if keyboard.a and not keyboard.d:
            self.animation_dash = animate(self, dx=-55, duration=dash_duration, tween='linear')
        elif keyboard.d and not keyboard.a:
            self.animation_dash = animate(self, dx=55, duration=dash_duration, tween='linear')
        elif self.flip_x:
            self.animation_dash = animate(self, dx=55, duration=dash_duration, tween='linear')
        else:
            self.animation_dash = animate(self, dx=-55, duration=dash_duration, tween='linear')

        clock.schedule(self.dash_mid, dash_duration * 2)
        clock.schedule(self.dash_end, dash_duration * 5)
        clock.schedule(self.dash_cooldown, dash_duration * 10)

    def dash_mid(self):
        '''Pause the player in midair after dashing by setting dx to zero.'''
        self.dx = 0

    def dash_end(self):
        '''Give back player controls.'''
        self.gravity, self.input = True, True

    def dash_cooldown(self):
        '''Let the player dash again.'''
        self.can_dash = True
    
    def dash_cancel(self):
        '''Call and unschedule dash termination.'''
        if self.animation_dash != None:
            if self.animation_dash.running:
                self.animation_dash.stop()

        self.dash_mid()
        self.dash_end()
        self.dash_cooldown()
        clock.unschedule(self.dash_mid)
        clock.unschedule(self.dash_end)
        clock.unschedule(self.dash_cooldown)

    # Overclock

    def overclock(self):
        '''Animate self.time_mod to the slow game.'''
        self.time_mod_simple = 0.2
        if self.animation_overclock != None:
            if self.animation_overclock.running:
                self.animation_overclock.stop()
        self.animation_overclock = animate(self, time_mod=self.time_mod_simple, duration=0.5)
        
        self.fps *= self.time_mod_simple

        for tile in tiles_animate:
            tile.fps *= self.time_mod_simple
        for attack in current_scene.attacks:
            attack.fps *= self.time_mod_simple
        for explosion in current_scene.explosions:
            explosion.fps *= self.time_mod_simple
        for enemy in current_scene.enemies:
            enemy.fps *= self.time_mod_simple

    def overclock_end(self):
        '''Animate self.time_mod to return the game to normal speed.'''
        self.fps /= self.time_mod_simple

        for tile in tiles_animate:
            tile.fps /= self.time_mod_simple
        for attack in current_scene.attacks:
            attack.fps /= self.time_mod_simple
        for explosion in current_scene.explosions:
            explosion.fps /= self.time_mod_simple
        for enemy in current_scene.enemies:
            enemy.fps /= self.time_mod_simple
        
        self.time_mod_simple = 1
        if self.animation_overclock != None:
            if self.animation_overclock.running:
                self.animation_overclock.stop()
        self.animation_overclock = animate(self, time_mod=self.time_mod_simple, duration=0.5)

    def overclock_cancel(self):
        '''Call overclock termination.'''
        if self.animation_overclock != None:
            if self.animation_overclock.running:
                self.animation_overclock.stop()

        if self.time_mod_simple != 1:
            self.time_mod = 1
            self.overclock_end()


class Trigger:
    def __init__(self, name, x, y):
        self.rect = Rect((32*x, 32*y), (32, 32))
        self.name = name
        current_scene.triggers.append(self)
    
    def use(self):
        '''Trigger an action and add the trigger name to a set.'''
        used_triggers.add(self.name)

        if self.name == 'overclock':
            player.can_overclock = True
        elif self.name == 'attack':
            player.can_attack = True


class Slime:
    def __init__(self, level: int, mx: int, my: int):
        self.level, self.mx, self.my =  level, mx, my
        for scene in levels[level]:
            if scene.mx == mx and scene.my == my:
                scene.enemies.append(self)
                break
    
    def die(self):
        self.images = []
        current_scene.enemies.remove(self)

    def attack(self):
        pass


# FUNCTIONS

def init_menu():
    '''Initializes the menu scene.'''
    global menu, bg_menu, bg_y, bg_dy, menu_scene

    menu = True
    menu_scene = 'main'
    bg_menu = f'background_space_{random.randint(0, 9)}'
    bg_y, bg_dy = 0, 0.25
    music.play('menu')


def init_level():
    '''Initializes the current level.'''
    global menu, game_paused, current_scene, bg_levels, bg_y, bg_dy, attacks, used_triggers, player

    menu = False
    game_paused = False
    bg_levels = 'background_levels'
    bg_y, bg_dy = 0, 0
    attacks = []
    used_triggers = set()
    
    player = Player('microwave_idle_0')
    if level == 0: # level 1 prohibits some functionality to start
        player.can_attack, player.can_overclock = False, False

    current_scene = levels[level][0]
    switch_level_scene(current_scene)
    player.respawn()
    music.play('level_4')


def check_level_scene(mx: int, my: int) -> Scene:
    '''Returns the updated scene of the level. If it does not exist, the player respawns.'''
    for scene in levels[level]:
        if scene.mx == mx and scene.my == my:
            return scene
    
    player.respawn()
    return current_scene


def switch_level_scene(scene: Scene):
    '''Initializes a new scene to display in a level.'''
    global tiles_clip, tiles_front, tiles_back, tiles_animate, hazards, current_scene
    tiles_clip, tiles_front, tiles_back, tiles_animate, hazards = [], [], [], [], []

    player.mx, player.my = scene.mx, scene.my
    current_scene = scene

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
    new_tile = Actor(f'tile_{name}', (32 * x + 16, 32 * y + 16))
    new_tile.scale = 2

    if 'spike' in name or 'water' in name:
        new_tile.images = [f'tile_{name[:-1]}{i}' for i in range(4 if 'water' in name else 6)]
        new_tile.fps = (6 if 'water' in name else 8) * player.time_mod_simple
        tiles_animate.append(new_tile)
        hazards.append(new_tile)
    
    elif name == 'warning_0':
        new_tile.images = [f'tile_{name[:-1]}{i}' for i in range(9)]
        new_tile.fps = 18 * player.time_mod_simple
        tiles_animate.append(new_tile)

    elif name[0].isdecimal():
        tiles_clip.append(new_tile)

    elif 'floor' in name or 'ceil' in name or 'side' in name:
        tiles_front.append(new_tile)

    else:
        tiles_back.append(new_tile)


def read_settings() -> list:
    settings = open('settings.txt', 'r')
    settings_list = settings.readlines()
    settings.close()

    music.set_volume(float(settings_list[5]))
    return [True] * int(settings_list[0]) + [False] * (4 - int(settings_list[0])), int(settings_list[1]), int(settings_list[2]), int(settings_list[3]), float(settings_list[4])


def write_settings():
    settings = open('settings.txt', 'w')
    settings.writelines(map(lambda x: str(x) + '\n', (levels_unlocked.count(True), instant_respawn, hard_mode, hitbox_debug, controller_deadzone, music.get_volume())))
    settings.close()


# SETTINGS

# Standard Settings
os.environ["SDL_VIDEO_CENTERED"] = "1" # center the window
WIDTH, HEIGHT = 1280, 704 # game resolution: 1280 x 704
TITLE = "ULTRAKOOL"

# Saved Settings
levels_unlocked, instant_respawn, hard_mode, hitbox_debug, controller_deadzone = read_settings()

# Controller Support
controller_mode = False
if pygame.joystick.get_count() == 1:
    if pygame.joystick.Joystick(0).get_numaxes() >= 2:
        controller_mode = True
        joystick = pg.joystick.Joystick(0)
        pygame.mouse.set_visible(False) # hide cursor in controller mode

# Menu
buttons_main = [Actor('button_dark', center=(640, 300 + 150 * i)) for i in range(3)] # main menu

buttons_levels = [] # levels menu
for coord in ((380, 350), (900, 350), (380, 500), (900, 500)):
    buttons_levels.append(Actor('button_dark', center=(coord)))

buttons_settings = [] # settings menu
for coord in ((380, 250), (380, 400), (380, 550), (900, 250), (900, 400), (900, 550)):
    buttons_settings.append(Actor('button_dark', center=(coord)))

buttons_dict = {'main': buttons_main, 'levels': buttons_levels, 'settings': buttons_settings}


# Event Handlers (one-time inputs)

def on_mouse_down(pos, button):
    if menu:
        global menu_scene, level, instant_respawn, hard_mode, hitbox_debug, controller_deadzone
        if button == mouse.LEFT:
            for i, b in enumerate(buttons_dict[menu_scene]):
                if b.collidepoint(pos):
                    if menu_scene == 'main':
                        sounds.menu_confirm.play()
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
                            sounds.menu_play.play()
                            init_level()
                    
                    elif menu_scene == 'settings':
                        sounds.menu_click.play()

                        if i == 0:
                            instant_respawn = 0 if instant_respawn else 1
                        elif i == 1:
                            if music.get_volume() == 1:
                                music.set_volume(0)
                            else:
                                music.set_volume(round(music.get_volume() + 0.2, 1))
                        elif i == 2:
                            hitbox_debug = 0 if hitbox_debug else 1
                        elif i == 3:
                            hard_mode = 0 if hard_mode else 1
                        elif i == 4:
                            controller_deadzone += 0.1
                            if controller_deadzone > 0.5:
                                controller_deadzone = 0.1
                        elif i == 5:
                            pass

    else:
        if player.input:
            if button == mouse.LEFT and player.can_attack: # TODO removed and player.can_ dash but should be fine
                player.attack(pos)
            elif button == mouse.RIGHT and player.can_overclock:
                player.overclock()


def on_mouse_up(pos, button):
    if menu:
        pass

    else:
        if button == mouse.RIGHT and player.time_mod_simple != 1: # canceled the condition for if player.input == True so overclocking can always be ended
            player.overclock_end()


def on_mouse_move(pos, rel, buttons):
    pass


def on_key_down(key, unicode):
    if key == keys.K:
        global controller_mode
        controller_mode = False
        pygame.mouse.set_visible(True)

    if menu:
        global menu_scene
        if key == keys.ESCAPE:
            sounds.menu_back.play()
            if menu_scene == 'levels':
                menu_scene = 'main'
            elif menu_scene == 'settings':
                menu_scene = 'main'
                write_settings()

    else:
        #global game_paused
        if key == keys.ESCAPE:
            init_menu() # TODO
            #game_paused = not game_paused

        elif key == keys.R and not player.alive:
            if hard_mode:
                init_level()
            else:
                player.respawn()

        elif player.input:
            if key in (keys.W, keys.SPACE) and player.can_jump and player.jumps > 0:
                player.jump()
            
            elif key == keys.S and player.can_boost:
                player.boost()
            
            elif key == keys.LSHIFT and player.can_dash: # shift could trigger sticky keys on Windows
                player.dash()


def on_key_up(key):
    pass


def on_music_end():
    pass


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
                if button.image == 'button_dark':
                    button.image = 'button_light'
                    sounds.menu_click.play()
            else:
                button.image = 'button_dark'
        
    else:
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
                if joystick.get_axis(0) < -controller_deadzone:
                    player.step_left()
                    walking = True
            
            if keyboard.d:
                player.step_right()
                walking = True
            elif controller_mode:
                if joystick.get_axis(0) > controller_deadzone:
                    player.step_right()
                    walking = True
            
            if not walking:
                player.switch_animation('idle')
        
        # Gravity

        if player.gravity:
            player.hitbox.y += min(32 * player.time_mod, player.dy * player.time_mod) # terminal velocity of 32
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

                elif player.hitbox.bottom > tile.bottom and 'd' in tile.image:
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
                    if player.alive:
                        player.dash_cancel()

                elif player.hitbox.right > tile.left and 'l' in tile.image.replace('tile', ''):
                    player.hitbox.x -= 1
                    if player.alive:
                        player.dash_cancel()
        
        player.hitbox.x += player.dx * player.time_mod

        if down_boost:
            player.dy -= player.dy * 1.1

        # Hazards

        for hazard in hazards:
            if hazard.colliderect(player.hitbox) and player.alive: # hazard collision kills the player
                player.die()

            counter = 0
            while hazard.colliderect(player.hitbox) and 'water' in hazard.image:
                counter += 1
                if counter > 64:
                    player.respawn()
                    break
                
                player.hitbox.y -= 1
                player.touch_ground()
        
        # Triggers

        for trigger in current_scene.triggers:
            if trigger.rect.colliderect(player.hitbox) and trigger.name not in used_triggers: # TODO
                trigger.use()

        # Scene Switching

        dmx, dmy = 0, 0
        if player.hitbox.centerx > WIDTH:
            dmx = 1
        elif player.hitbox.centerx < 0:
            dmx = -1
        elif player.hitbox.centery > HEIGHT:
            dmy = 1
        elif player.hitbox.centery < 0:
            dmy = -1
        
        new_scene = check_level_scene(player.mx + dmx, player.my + dmy)
        if current_scene != new_scene:
            switch_level_scene(new_scene)
            player.hitbox.x += WIDTH * -dmx
            player.hitbox.y += HEIGHT * -dmy

        # Tiles

        for tile in tiles_animate:
            tile.scale = 2
            tile.animate()

        # Explosions

        for explosion in current_scene.explosions:
            if explosion.image == 'explosion_6':
                current_scene.explosions.remove(explosion)
            explosion.scale = 2
            explosion.animate()

        # Attacks

        for attack in current_scene.attacks:
            attack.move_in_direction(10 * player.time_mod)
            attack.scale = 1.5
            attack.animate()

            if attack.collidelistall_pixel(tiles_clip + tiles_animate):
                current_scene.attacks.remove(attack)

                # Create explosion effect
                new_explosion = Actor('explosion_0', (attack.x + 10, attack.y))
                new_explosion.images = [f'explosion_{i}' for i in range(7)]
                new_explosion.fps = 14 * player.time_mod_simple
                new_explosion.scale = 2
                current_scene.explosions.append(new_explosion)

        # Player Display

        player.pos = (player.hitbox.x + 30, player.hitbox.y)
        player.scale = 2
        player.animate()


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
            
            if controller_mode:
                screen.draw.text('CONTROLLER MODE ENABLED. PRESS K AT ANY POINT TO PERMANANTLY DISABLE.', center=(WIDTH/2, 200), fontname='vcr_ocd_mono', fontsize=20)
                # Note: due to limited event functionality in Pygame Zero, button presses are more complicated
        
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
            
            settings_text = [f'INSTANT RESPAWN: {'ON' if instant_respawn else 'OFF'}', # text list for settings menu buttons
                             f'MUSIC VOLUME: {music.get_volume():.1f}',
                             f'HITBOX DEBUG: {'ON' if hitbox_debug else 'OFF'}',
                             f'HARD MODE: {'ON' if hard_mode else 'OFF'}',
                             f'JOYSTICK DEADZONE: {controller_deadzone:.1f}',
                             f'UNKNOWN']
            
            for i in range(6):
                screen.draw.text(settings_text[i], center=buttons_settings[i].pos, fontname='roboto_thin', fontsize=35, color=('white' if buttons_settings[i].image == 'button_dark' else 'black'))

            screen.draw.text('ESC TO GO BACK', center=(640, 660), fontname='roboto_thin', fontsize=40, color='white')
    
    else:
        # Behind Entities
        screen.blit(bg_levels, (0, 0))
        
        for tile in (tiles_back + tiles_animate):
            tile.draw()
        
        for tile in (tiles_clip):
            tile.draw()

        # Level Text
        for text in current_scene.text:
            screen.draw.text(text.message, center=(text.x, text.y), fontname='vcr_ocd_mono', fontsize=32, color=text.color)

        # Entities
        if hitbox_debug: # only for debug
            screen.draw.rect(player.hitbox, 'RED')
        player.draw()

        for attack in current_scene.attacks:
            attack.draw()

        # In Front of Entities
        for tile in tiles_front:
            tile.draw()

        # Explosions
        for explosion in current_scene.explosions:
            explosion.draw()

        # Death Screen
        if not player.alive: #TODO
            pass


# START

init_menu()
pgzrun.go()