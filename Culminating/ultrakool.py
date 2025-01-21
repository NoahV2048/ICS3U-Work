# ULTRAKOOL
# A really cool combat platformer game (ICS3U Culminating Project)
# Noah Verdon
# Last Edited: January 20, 2024

# ALL ASSETS ARE LISTED UNDER A SEPARATE GOOGLE DOC
# All Music is Original

import pgzrun, os, random, sys, pygame as pg
from pgzhelper import *
from levels import *

# CLASSES

class Player(Actor): # Player is a child class of Actor
    def __init__(self):
        super().__init__('microwave_idle_0') # inherit Actor

        # Attributes
        self.animation = None
        self.time_mod, self.time_mod_simple = 1, 1
        self.input = True
        self.visible = True
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
            if sfx: sounds.respawn.play()

            if hard_mode:
                init_level()
            else:
                self.respawn()
        else:
            if sfx: sounds.hurt.play()

    def respawn(self):
        '''Respawns the player.'''
        player.alive = True
        player.input = True
        self.hitbox.center = self.spawn

        if current_scene.enemies: # respawn all enemies in the scene if there are still any remaining
            reset_enemies(current_scene)

        for enemy in current_scene.enemies:
            if player.hitbox.colliderect(enemy.hitbox) and enemy.can_hurt:
                enemy.die() # ensures player doesn't die on respawn

        touch_ground(self)
        self.dash_cancel()
        self.overclock_cancel()
        self.attack_cancel()

        for scene in levels[level]:
            scene.attacks = [] # reset player attacks
            scene.enemy_attacks = [] # reset enemy attacks
            for enemy in scene.enemies:
                enemy.cooldown = True
    
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
        self.dy += 20

    # Attack

    def attack(self, pos: tuple):
        '''Attack a position specified by a mouse click.'''
        self.overclock_cancel()
        self.dash_cancel()
        if sfx: sounds.player_attack.play()

        self.switch_animation('attack')
        self.gravity, self.input = False, False
        self.can_attack = False

        self.pos = self.hitbox.center
        new_attack = Actor('attack_0')
        new_attack.scale = 1.5
        new_attack.pos = self.hitbox.center
        new_attack.images = [f'attack_{i}' for i in range(5)]
        new_attack.direction = self.direction_to(pos)
        new_attack.angle = self.direction_to(pos) + 180

        current_scene.attacks.append(new_attack)

        clock.schedule(self.attack_end, 0.5)
        clock.schedule(self.attack_cooldown, 1)

    def attack_end(self):
        '''Give back player controls.'''
        self.gravity, self.input = True, True
        self.dx, self.dy = 0, 0

    def attack_cooldown(self):
        '''Let the player attack again.'''
        if not (level == 0 and 'attack' not in used_triggers):
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

        if sfx: sounds.swoosh.play()
        self.overclock_cancel() # make dashing and overclocking exclusive

        dash_duration = 0.05 / self.time_mod_simple # no reason to multiply by time_mod_simple unless functionality is changed later

        if controller_mode:
            if joystick.get_axis(0) < -controller_deadzone:
                self.animation_dash = animate(self, dx=-55, duration=dash_duration, tween='linear') # left
            elif joystick.get_axis(0) > controller_deadzone:
                self.animation_dash = animate(self, dx=55, duration=dash_duration, tween='linear') # right
            elif self.flip_x:
                self.animation_dash = animate(self, dx=55, duration=dash_duration, tween='linear') # right
            else:
                self.animation_dash = animate(self, dx=-55, duration=dash_duration, tween='linear') # left
        else:
            if keyboard.a and not keyboard.d:
                self.animation_dash = animate(self, dx=-55, duration=dash_duration, tween='linear') # left
            elif keyboard.d and not keyboard.a:
                self.animation_dash = animate(self, dx=55, duration=dash_duration, tween='linear') # right
            elif self.flip_x:
                self.animation_dash = animate(self, dx=55, duration=dash_duration, tween='linear') # right
            else:
                self.animation_dash = animate(self, dx=-55, duration=dash_duration, tween='linear') # left

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
        for enemy_attack in current_scene.enemy_attacks:
            enemy_attack.fps *= self.time_mod_simple
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
        for enemy_attack in current_scene.enemy_attacks:
            enemy_attack.fps /= self.time_mod_simple
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

        self.time_mod = 1
        if self.time_mod_simple != 1:
            self.overclock_end()


class Trigger:
    def __init__(self, name, x, y):
        self.rect = Rect((32*x, 32*y), (32, 32))
        self.name = name
        current_scene.triggers.append(self)
    
    def use(self):
        '''Trigger an action and add the trigger name to a set.'''
        used_triggers.add(self.name) # expandable system for triggers

        if self.name == 'overclock':
            player.can_overclock = True
        elif self.name == 'attack':
            player.can_attack = True


class Slime(Actor): # Slime is a child class of Actor
    def __init__(self, x, y):
        super().__init__('slime_idle_0') # inherit Actor

        # Attributes
        self.hitbox = Rect((0,0), (80, 48))
        self.hitbox.midbottom = 32 * x + 16, 32 * y + 32
        self.gravity, self.dx, self.dy = True, 0, 0

        self.lives = 1
        self.can_hurt = True
        self.can_attack = False
        self.cooldown = True

        self.idle()
    
    def face_player(self):
        '''Turn the slime towards the player unless it is within 15 pixels horizontal.'''
        if self.hitbox.centerx + 15 < player.hitbox.centerx: # the slime can rapidly turn around if near the x coordinate of the player, but this is intentional
            self.flip_x = True
        elif self.hitbox.centerx - 15 > player.hitbox.centerx:
            self.flip_x = False

    def idle(self):
        '''Return slime to idle state.'''
        self.images = [f'slime_idle_{i}' for i in range(4)]
        self.fps = 6 * player.time_mod_simple

    def hurt(self): # no current functionality as slime starts with one life
        '''Trigger hurt animation for the slime.'''
        self.images = [f'slime_hurt_{i}' for i in range(5)] # extra image in the list used to trigger other actions
        self.fps = 4 * player.time_mod_simple
        self.lives -= 1
        self.can_hurt = False
    
    def hurt_cooldown(self): # no current functionality as slime starts with one life
        '''Allow the slime to hurt again (i-frames).'''
        self.can_hurt = True
        self.idle()

    def die(self):
        '''Trigger death animation for the slime.'''
        if sfx: sounds.enemy_die.play()
        self.can_hurt = False
        self.images = [f'slime_die_{i}' for i in range(5)] # extra image in the list used to trigger other actions
        self.fps = 8 * player.time_mod_simple

    def attack(self):
        '''Trigger attack for the slime.'''
        self.images = [f'slime_attack_{i}' for i in range(6)] # extra image in the list used to trigger other actions
        self.fps = 8 * player.time_mod_simple
        self.can_attack = False
        self.face_player()
    
    def attack_cooldown(self):
        '''Allow the slime to attack again.'''
        self.can_attack = True
        self.idle()
    
    def projectile_attack(self):
        '''Have the slime shoot a projectile towards the player.'''
        self.images = [f'slime_hurt_{i}' for i in range(6)] # extra image in the list used to trigger other actions
        self.fps = 8 * player.time_mod_simple
        self.can_attack = False
        self.face_player()
        if sfx: sounds.laser.play()

        new_attack = Actor('enemy_attack_0')
        new_attack.scale = 1.2
        new_attack.pos = self.hitbox.center
        new_attack.images = [f'enemy_attack_{i}' for i in range(5)]
        new_attack.direction = self.direction_to(player.hitbox.center)
        new_attack.angle = self.direction_to(player.hitbox.center) + 180
        new_attack.origin = self
        current_scene.enemy_attacks.append(new_attack)

    def step(self):
        '''Movement logic towards the player for the slime.'''
        move_images = [f'slime_move_{i}' for i in range(4)] # even if the slime can't actually move, the animation will still display to indicate aggression
        if self.images != move_images:
            self.images = move_images
            self.fps = 8 * player.time_mod_simple
        
        self.face_player()

        right_collide = False
        for tile in (tiles_clip + tiles_back + hazards): # using all hazards instead of just water so that enemies can wander into spike pits
            if tile.collidepoint(self.hitbox.right + 16, self.hitbox.bottom + 48) or tile.collidepoint(self.hitbox.right + 16, self.hitbox.bottom + 16):
                right_collide = True
                break

        left_collide = False
        for tile in (tiles_clip + tiles_back + hazards): # using all hazards instead of just water so that enemies can wander into spike pits
            if tile.collidepoint(self.hitbox.left - 16, self.hitbox.bottom + 48) or tile.collidepoint(self.hitbox.left - 16, self.hitbox.bottom + 16):
                left_collide = True
                break

        if self.flip_x and right_collide:
            self.hitbox.x -= -5 * player.time_mod
        elif not self.flip_x and left_collide:
            self.hitbox.x -= 5 * player.time_mod


# FUNCTIONS

def init_menu():
    '''Initializes the menu scene.'''
    global menu, menu_scene, bg_menu, bg_x, bg_y, bg_dx, bg_dy

    menu = True
    menu_scene = 'main'
    bg_menu = f'background_space_{random.randint(0, 9)}'
    bg_x, bg_y = 0, 0
    bg_dx, bg_dy = 0, -0.25
    music.play('menu')


def init_level():
    '''Initializes the current level.'''
    global menu, game_paused, current_scene, attacks, used_triggers, player
    global bg_levels_visible, bg_x, bg_y, bg_dx, bg_dy
    global level_beat, level_end_screen, level_start_time, level_subtracted_time

    if menu: # this makes sure music doesn't restart after every death in hard mode
        music.play(f'level_{level}')
    menu = False
    game_paused = False
    level_beat, level_end_screen = False, False
    bg_levels_visible = True
    bg_x, bg_y = 0, 0
    bg_dx, bg_dy = level + 1, 0 # make the background more turbulent for each level
    attacks = []
    used_triggers = set()
    
    player = Player()

    if level == 0:
        player.can_attack, player.can_overclock = False, False # level 1 prohibits some functionality to start

        if controller_mode: # change the tutorial text a bit if controller mode is activated
            tutorial_controller()
        else:
            tutorial_keyboard()

    current_scene = levels[level][0]
    switch_level_scene(current_scene)
    player.respawn()

    for scene in levels[level]: # configure level enemies
        reset_enemies(scene)
    
    level_subtracted_time = 0 # keep track of time to subtract (note: currently unused but could be implemented so pauses and deaths don't progress the clock) (TODO maybe later)
    level_start_time = time.time() # create a timer for the duration of the level


def reset_enemies(scene):
    '''Respawns all enemies in a given scene.'''
    scene.enemies = []
    for enemy in scene.enemies_raw:
        if enemy[0] == 'slime':
            new_enemy = Slime(enemy[1], enemy[2])

        elif enemy[0] == 'mushroom': # I had ideas and assets for other anemy types, but I decided not to implement them for the sake of time (TODO maybe later)
            pass

        elif enemy[0] == 'spider': # I had ideas and assets for other anemy types, but I decided not to implement them for the sake of time (TODO maybe later)
            pass

        scene.enemies.append(new_enemy)


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
    '''Return current settings.'''
    settings = open('settings.txt', 'r')
    settings_list = settings.readlines()
    settings.close()

    music.set_volume(float(settings_list[5]))
    return int(settings_list[0]), int(settings_list[1]), int(settings_list[2]), int(settings_list[3]), int(settings_list[4])


def write_settings():
    '''Save current settings.'''
    settings = open('settings.txt', 'w')
    settings.writelines(map(lambda x: str(x) + '\n', (instant_respawn, hard_mode, debug_mode, sfx, levels_unlocked, music.get_volume())))
    settings.close()


def create_explosion(x, y):
    '''Summons an explosion actor at a specified location.'''
    new_explosion = Actor('explosion_0', (x, y))
    new_explosion.images = [f'explosion_{i}' for i in range(7)]
    new_explosion.fps = 14 * player.time_mod_simple
    new_explosion.scale = 2
    current_scene.explosions.append(new_explosion)
    if sfx: sounds.hit.play()


def touch_ground(entity):
    '''Change various attributes when touching the ground.'''
    entity.dx, entity.dy = 0, 0

    if type(entity) == Player: # resets some player attributes
        entity.can_boost = True
        entity.can_jump = True
        entity.gravity = True
        entity.jumps = 2


def movement(entity):
    '''Call the movement procedure for a variety of entities.'''
    
    # Gravity
    if entity.gravity:
        entity.hitbox.y += min(32 * player.time_mod, entity.dy * player.time_mod) # terminal velocity of 32
        entity.dy += 1.1 * player.time_mod # gravity value of 1.1

    entity.hitbox.x += entity.dx * player.time_mod

    # Collision Detection

    down_boost = False
    for tile in tiles_clip: # up and down
        counter = 0
        while tile.colliderect(entity.hitbox):
            counter += 1
            if counter > 64:
                break
            
            if type(entity) == Player: # separate logic for player and enemies
                if (entity.hitbox.top + 15 < tile.top) and 'u' in tile.image: # top + 15 is the minimum height for auto-jumping
                    entity.hitbox.y -= 1
                    touch_ground(entity)

                elif (entity.hitbox.bottom - 16) > tile.bottom and 'd' in tile.image:
                    entity.hitbox.y += 1
                    down_boost = True

            else: # separate logic for player and enemies
                if entity.hitbox.top < tile.top and 'u' in tile.image:
                    entity.hitbox.y -= 1
                    touch_ground(entity)

                elif entity.hitbox.bottom > tile.bottom and 'd' in tile.image:
                    entity.hitbox.y += 1
                    down_boost = True

    for tile in tiles_clip: # left and right
        counter = 0
        while tile.colliderect(entity.hitbox): # left and right
            counter += 1
            if counter > 64:
                if type(entity) == Player:
                    player.respawn()
                else:
                    entity.die()
                    pass
                break

            if entity.hitbox.left < tile.right and 'r' in tile.image.replace('water', ''):
                entity.hitbox.x += 1
                if type(entity) == Player and player.alive:
                    entity.dash_cancel()

            elif entity.hitbox.right > tile.left and 'l' in tile.image.replace('tile', ''):
                entity.hitbox.x -= 1
                if type(entity) == Player and player.alive:
                    entity.dash_cancel()

    if down_boost:
        entity.dy -= entity.dy * 1.1
    
    # Hazards

    for hazard in hazards:
        if hazard.colliderect(entity.hitbox): # hazard collision kills the entity
            if type(entity) != Player:
                if 'water' not in hazard.image and entity.can_hurt: # this allows enemies to survive on water
                    entity.die()
            elif entity.alive:
                entity.die()

        counter = 0
        while hazard.colliderect(entity.hitbox) and 'water' in hazard.image:
            counter += 1
            if counter > 64:
                if type(entity) == Player:
                    entity.respawn()
                else:
                    entity.die()
                break
            
            entity.hitbox.y -= 1
            touch_ground(entity)


# Level End

def level_end():
    '''Starts a sequence of events after the level has been beat.'''
    global level_beat, levels_unlocked, level_final_time, level_enemies_killed, level_enemies_total

    level_final_time = time.time() - level_start_time - level_subtracted_time
    level_enemies_killed, level_enemies_total = 0, 0

    for scene in levels[level]:
        level_enemies_killed -= len(scene.enemies)
        level_enemies_total += len(scene.enemies_raw)
    level_enemies_killed += level_enemies_total

    level_beat = True
    if level == levels_unlocked and levels_unlocked != 3:
        levels_unlocked += 1

    write_settings()
    music.stop()
    if sfx: sounds.respawn.play()

    clock.schedule(level_end_0, 1.0)
    clock.schedule(level_end_1, 1.5)
    clock.schedule(level_end_2, 2.0)


def level_end_0():
    '''Event 1 of 3 after the game is beat.'''
    global tiles_clip, tiles_back, tiles_front, tiles_animate, bg_levels_visible
    tiles_clip, tiles_back, tiles_front, tiles_animate = [], [], [], []
    bg_levels_visible = False
    if sfx: sounds.menu_confirm.play()


def level_end_1():
    '''Event 2 of 3 after the game is beat.'''
    player.visible = False
    if sfx: sounds.menu_confirm.play()

    # Change level background
    for y, row in enumerate(level_end_tiles): # tiles could be animated instead of all appearing at once (TODO maybe later)
        for x, tile in enumerate(row):
            tile_name = tile_unicode_dict[tile]
            manage_tile(tile_name, x, y)


def level_end_2():
    '''Event 3 of 3 after the game is beat.'''
    global level_end_screen
    level_end_screen = True
    if sfx: sounds.menu_confirm.play()


def display_background(index: int, scale: int):
    '''Blits a tiled image to the background to simulate parallax.'''
    res_x, res_y = 1280, 1280

    if player_parallax: # player movement controls background movement
        x = -((player.mx * WIDTH + player.hitbox.centerx) / scale / 32) % res_x
        y = -((player.my * HEIGHT + player.hitbox.centery) / scale / 128) % res_y
    else: # background movement is automated
        x = (bg_x / scale) % res_x
        y = (bg_y / scale) % res_y

    screen.blit(f'background_levels_{index}', (x, y))
    screen.blit(f'background_levels_{index}', (x - res_x, y))
    screen.blit(f'background_levels_{index}', (x, y - res_y))
    screen.blit(f'background_levels_{index}', (x - res_x, y - res_y))


# Controller Functionality (Note: due to limited event functionality in Pygame Zero, button presses are more complicated)

def check_controllers():
    global controller_mode, joystick, controller_buttons
    pg.joystick.init()

    controller_mode = False
    if pg.joystick.get_count() == 1:
        if pg.joystick.Joystick(0).get_numaxes() >= 6 and pg.joystick.Joystick(0).get_numbuttons() >= 8:
            controller_mode = True
            joystick = pg.joystick.Joystick(0)
            controller_buttons = [False for i in range(10)] # save the states of controller buttons
            tutorial_controller() # change the tutorial text if controller mode is activated


def check_buttons_down() -> list:
    '''Manually check for changes in controller button states and return pressed buttons.'''
    buttons_down = []

    for i in range(8):
        if joystick.get_button(i) == True and controller_buttons[i] == False:
            buttons_down.append(i)
            controller_buttons[i] = True
    
    if joystick.get_axis(4) > controller_deadzone and controller_buttons[8] == False:
        buttons_down.append(8)
        controller_buttons[8] = True
    if joystick.get_axis(5) > controller_deadzone and controller_buttons[9] == False:
        buttons_down.append(9)
        controller_buttons[9] = True

    return buttons_down


def check_buttons_up() -> list:
    '''Manually check for changes in controller button states and return released buttons.'''
    buttons_up = []

    for i in range(8):
        if joystick.get_button(i) == False and controller_buttons[i] == True:
            buttons_up.append(i)
            controller_buttons[i] = False
    
    if joystick.get_axis(4) <= controller_deadzone and controller_buttons[8] == True:
        buttons_up.append(8)
        controller_buttons[8] = False
    if joystick.get_axis(5) <= controller_deadzone and controller_buttons[9] == True:
        buttons_up.append(9)
        controller_buttons[9] = False

    return buttons_up


# SETTINGS

# Standard Settings
os.environ["SDL_VIDEO_CENTERED"] = "1" # center the window
WIDTH, HEIGHT = 1280, 704 # game resolution: 1280 x 704
TITLE = "ULTRAKOOL"
controller_deadzone = 0.5 # not changeable in-game
player_parallax = False

# Saved Settings
instant_respawn, hard_mode, debug_mode, sfx, levels_unlocked = read_settings()

# HUD
hud_box_overclock, hud_box_overclock_simple = Actor('button_dark'), Actor('button_dark')
hud_box_overclock.scale, hud_box_overclock_simple.scale = 0.5, 0.5
hud_box_overclock.bottomright = WIDTH - 15, HEIGHT - 15
hud_box_overclock_simple.bottomright = WIDTH - 15, HEIGHT - 90

hud_controller = Actor('button_dark')
hud_controller.scale = 0.4
hud_controller.topleft = 15, 15

hud_timer = Actor('button_dark')
hud_timer.scale = 0.5
hud_timer.bottomleft = 10, HEIGHT - 15

# Death Screen
hud_box_death_screen = Actor('button_dark')
hud_box_death_screen.scale = 1.5
hud_box_death_screen.pos = WIDTH / 2, HEIGHT / 2

# Level End Screen
level_beat_box_up, level_beat_box_down = Actor('button_dark'), Actor('button_dark')
level_beat_box_up.scale, level_beat_box_down.scale = 1.5, 0.75
level_beat_box_up.pos, level_beat_box_down.pos = (WIDTH / 2, HEIGHT / 2 - 90), (WIDTH / 2, HEIGHT / 2 + 200)

# Stats
time_stat_box, enemy_stat_box = Actor('button_dark'), Actor('button_dark')
time_stat_box.scale, enemy_stat_box.scale = 0.75, 0.75
time_stat_box.pos, enemy_stat_box.pos = (WIDTH / 2 - 225, HEIGHT / 2 + 90), (WIDTH / 2 + 225, HEIGHT / 2 + 90)

# Controller Support
check_controllers()

# Buttons
buttons_main = [Actor('button_dark', center=(640, 300 + 150 * i)) for i in range(3)] # main menu

buttons_levels = [] # levels menu
for coord in ((380, 350), (900, 350), (380, 500), (900, 500)):
    buttons_levels.append(Actor('button_dark', center=(coord)))

buttons_settings = [] # settings menu
for coord in ((380, 250), (380, 400), (380, 550), (900, 250), (900, 400), (900, 550)):
    buttons_settings.append(Actor('button_dark', center=(coord)))

buttons_pause = [Actor('button_dark', center=(WIDTH / 2, HEIGHT / 2  + 140 * i)) for i in (-1, 0, 1)]

buttons_dict = {'main': buttons_main, 'levels': buttons_levels, 'settings': buttons_settings}


# Event Handlers (one-time inputs)

def on_mouse_down(pos, button):
    if menu:
        global menu_scene, level, instant_respawn, hard_mode, debug_mode, sfx, levels_unlocked
        if button == mouse.LEFT:
            for i, button in enumerate(buttons_dict[menu_scene]):
                if button.collidepoint(pos):
                    if menu_scene == 'main':
                        if sfx: sounds.menu_confirm.play()
                        if i == 0:
                            menu_scene = 'levels'
                        elif i == 1:
                            menu_scene = 'settings'
                        elif i == 2:
                            pg.quit()
                            sys.exit()

                    elif menu_scene == 'levels':
                        if levels_unlocked >= i:
                            level = i
                            if sfx: sounds.respawn.play()
                            init_level()
                    
                    elif menu_scene == 'settings':
                        if i == 0:
                            instant_respawn = 0 if instant_respawn else 1
                        elif i == 1:
                            debug_mode = 0 if debug_mode else 1
                        elif i == 2:
                            if levels_unlocked == 3:
                                levels_unlocked = 0
                            else:
                                levels_unlocked = 3
                        elif i == 3:
                            hard_mode = 0 if hard_mode else 1
                        elif i == 4:
                            sfx = 0 if sfx else 1
                        elif i == 5:
                            if music.get_volume() == 1:
                                music.set_volume(0)
                            else:
                                music.set_volume(round(music.get_volume() + 0.2, 1))
                        
                        if sfx: sounds.menu_click.play() # moved to the end of the conditional to align with the state of sfx after the button press

    else:
        global game_paused
        if game_paused and button == mouse.LEFT:
            for i, button in enumerate(buttons_pause):
                if button.collidepoint(pos):
                    if sfx: sounds.menu_back.play()
                    if i == 0:
                        game_paused = False
                        player.input = True if player.alive else False
                    elif i == 1:
                        init_level()
                    elif i == 2:
                        init_menu()

        if player.input:
            if button == mouse.LEFT and player.can_attack:
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
        if controller_mode:
            controller_mode = False
            pygame.joystick.quit()
            pygame.mouse.set_visible(True)
            tutorial_keyboard() # change the tutorial text if controller mode is deactivated
        else:
            check_controllers()

    if menu:
        global menu_scene
        if key == keys.ESCAPE:
            if sfx: sounds.menu_back.play()
            if menu_scene == 'levels':
                menu_scene = 'main'
            elif menu_scene == 'settings':
                menu_scene = 'main'
                write_settings()

    else:
        global game_paused
        if key == keys.ESCAPE:
            if level_end_screen:
                init_menu()
                if sfx: sounds.menu_back.play()
            elif game_paused:
                game_paused = False
                player.input = True if player.alive else False
                if sfx: sounds.menu_back.play()
            elif not game_paused and player.input:
                game_paused = True
                if sfx: sounds.menu_back.play()
                player.overclock_end()
    
        elif key == keys.R and not player.alive and not game_paused:
            if sfx: sounds.respawn.play()

            if hard_mode:
                init_level() # reset the level entirely in hard mode
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


# Controller Event Handlers

def on_button_down(buttons):
    '''Copied and modified on_key_down. Copying on_mouse_down completely was unfortunately not implemented.'''
    if menu:
        global menu_scene
        if 1 in buttons: # B on Xbox
            if sfx: sounds.menu_back.play()

            if menu_scene == 'levels':
                menu_scene = 'main'
            elif menu_scene == 'settings':
                menu_scene = 'main'
                write_settings()

    else:
        # From on_key_down

        global game_paused
        if 7 in buttons: # start on Xbox
            if game_paused:
                game_paused = False
                player.input = True if player.alive else False
            elif not game_paused and player.input:
                game_paused = True
                player.overclock_end()
    
        elif 3 in buttons and not player.alive and not game_paused: # Y on Xbox
            if sfx: sounds.respawn.play()

            if hard_mode:
                init_level() # reset the level entirely in hard mode
            else:
                player.respawn()

        elif player.input:
            if 0 in buttons and player.can_jump and player.jumps > 0: # A on Xbox
                player.jump()
            
            elif 1 in buttons and player.can_boost: # B on Xbox
                player.boost()
            
            elif 2 in buttons and player.can_dash: # X on Xbox
                player.dash()
        elif 1 in buttons: # B on Xbox
            if level_end_screen:
                init_menu()
            elif game_paused:
                game_paused = False
                player.input = True if player.alive else False
        
        # From on_mouse_down

        if player.input:
            if 9 in buttons and player.can_attack: # right trigger on Xbox
                if not (-controller_deadzone < joystick.get_axis(2) < controller_deadzone) or not (-controller_deadzone < joystick.get_axis(3) < controller_deadzone): # aim priority given to right joystick
                    pos = (player.hitbox.centerx + 10 * joystick.get_axis(2), player.hitbox.centery + 10 * joystick.get_axis(3))
                elif not (-controller_deadzone < joystick.get_axis(0) < controller_deadzone) or not (-controller_deadzone < joystick.get_axis(1) < controller_deadzone): # left joystick checked next
                    pos = (player.hitbox.centerx + 10 * joystick.get_axis(0), player.hitbox.centery + 10 * joystick.get_axis(1))
                elif player.flip_x: # aims in direction of the player if there is no joystick information
                    pos = (player.hitbox.centerx + 10, player.hitbox.centery)
                else:
                    pos = (player.hitbox.centerx - 10, player.hitbox.centery)

                player.attack(pos)

            elif 8 in buttons and player.can_overclock: # left trigger on Xbox
                player.overclock()


def on_button_up(buttons):
    '''Trigger events when a controller button is released.'''
    if menu:
        pass
    else:
        if 8 in buttons and player.time_mod_simple != 1: # left trigger on Xbox
            player.overclock_end()


# UPDATE

def update():
    global game_paused, bg_x, bg_y, controller_mode

    if controller_mode: # trigger controller response
        buttons_down, buttons_up = check_buttons_down(), check_buttons_up()
        on_button_down(buttons_down)
        on_button_up(buttons_up)
        pg.mouse.set_visible(False) # hide cursor in controller mode by default
        if pg.joystick.get_count() != 1:
            controller_mode = False

    if menu:
        # Background movement
        bg_y += bg_dy

        # Button color response
        for button in buttons_dict[menu_scene]:
            if button.collidepoint(pg.mouse.get_pos()):
                if button.image == 'button_dark':
                    button.image = 'button_light'
                    if sfx: sounds.menu_click.play()
            else:
                button.image = 'button_dark'
        
        pg.mouse.set_visible(True) # show cursor in menus
        
    else:
        bg_x += bg_dx * player.time_mod
        bg_y += bg_dy * player.time_mod

        if game_paused:
            player.input = False
            pg.mouse.set_visible(True) # show cursor in menus

            # Button color response
            for button in buttons_pause:
                if button.collidepoint(pg.mouse.get_pos()):
                    if button.image == 'button_dark':
                        button.image = 'button_light'
                        if sfx: sounds.menu_click.play()
                else:
                    button.image = 'button_dark'

        if player.input:
            # Flipping
            if controller_mode: # flip player based on joystick positions
                if joystick.get_axis(2) > controller_deadzone:
                    player.flip_x = True
                elif joystick.get_axis(2) < -controller_deadzone:
                    player.flip_x = False
                elif joystick.get_axis(0) > controller_deadzone:
                    player.flip_x = True
                elif joystick.get_axis(0) < -controller_deadzone:
                    player.flip_x = False

            else: # flip player based on mouse position
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
        
        if not level_beat:
            movement(player)
        
        # Triggers

        for trigger in current_scene.triggers:
            if trigger.rect.colliderect(player.hitbox) and trigger.name not in used_triggers:
                trigger.use() # use the trigger and add it to the set of used triggers in the level

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

        # Enemy Display

        for enemy in current_scene.enemies:
            movement(enemy)
            enemy.pos = (enemy.hitbox.centerx, enemy.hitbox.centery - 10)
            enemy.scale = 3
            enemy.animate()

            if enemy.cooldown: # ensure the player isn't obliterated when walking into a scene
                enemy.can_attack = False
                enemy.cooldown = False
                clock.schedule(enemy.attack_cooldown, random.uniform(0.2, 1))

            if enemy.image == 'slime_die_4':
                current_scene.enemies.remove(enemy)
            elif enemy.image in ('slime_attack_5', 'slime_hurt_5'):
                enemy.attack_cooldown()

            # Automatic movement
            if enemy.can_hurt and enemy.can_attack:
                if enemy.hitbox.left - 32 < player.hitbox.centerx < enemy.hitbox.right + 32 and enemy.hitbox.top - 128 < player.hitbox.centery < enemy.hitbox.bottom + 32:
                    enemy.attack()
                elif enemy.hitbox.left - 960 < player.hitbox.centerx < enemy.hitbox.right + 960 and enemy.hitbox.top - 768 < player.hitbox.centery < enemy.hitbox.bottom + 512:
                    if random.randint(1, (120 if hard_mode else 180)) == 77:
                        enemy.projectile_attack()
                    else:
                        enemy.step()
                elif 'move' in enemy.image:
                    enemy.idle()


        # Player Attacks

        for attack in current_scene.attacks:
            attack.move_in_direction(15 * player.time_mod)
            attack.scale = 1.5
            attack.animate()
            explode = False

            for enemy in current_scene.enemies:
                if attack.collide_pixel(enemy):
                    explode = True
                    if enemy.lives <= 1:
                        enemy.die()
                    else:
                        enemy.hurt()

            if attack.collidelistall_pixel(tiles_clip + tiles_animate):
                explode = True
                
            for enemy_attack in current_scene.enemy_attacks:
                if enemy_attack.collide_pixel(attack):
                    explode = True
                    current_scene.enemy_attacks.remove(enemy_attack)
            
            if explode:
                current_scene.attacks.remove(attack)
                create_explosion(attack.x + 10, attack.y)

        # Enemy Attacks
    
        saved_attacks = []
        for enemy_attack in current_scene.enemy_attacks:
            enemy_attack.move_in_direction((12 if hard_mode else 10) * player.time_mod)
            enemy_attack.scale = 1.2
            enemy_attack.animate()
            explode = False

            if enemy_attack.collide_pixel(player) and player.alive:
                explode = True
                if player.alive:
                    player.die()
                    break # this is important otherwise it crahses in instant respawn mode

            other_enemies = list(set(current_scene.enemies) - {enemy_attack.origin}) # list(set) is a little ugly but works for list subtraction
            if enemy_attack.collidelistall_pixel(tiles_clip + tiles_animate + other_enemies): # enemy attacks explode after hitting an enemy they did not originate from
                explode = True
            
            for other_attack in list(set(current_scene.enemy_attacks) - {enemy_attack}): # allow attacks to hit each other
                if enemy_attack.collide_pixel(other_attack):
                    explode = True
                    saved_attacks.append(other_attack)

            if explode:
                current_scene.enemy_attacks.remove(enemy_attack)
                create_explosion(enemy_attack.x + 10, enemy_attack.y)
        
        for saved_attack in saved_attacks: # this ensures both attacks are destroyed when a collision occurs
            if saved_attack in current_scene.enemy_attacks: # could crash otherwise
                current_scene.enemy_attacks.remove(saved_attack)
                create_explosion(enemy_attack.x + 10, saved_attack.y)

        # Enemy Collision

        for enemy in current_scene.enemies:
            if enemy.hitbox.colliderect(player.hitbox) and player.alive: # touching an enemy will kill the player
                player.die()
            
            if not (0 <= enemy.hitbox.centerx <= WIDTH and 0 <= enemy.hitbox.centery <= HEIGHT):
                current_scene.enemies.remove(enemy)

        # Player Display

        player.pos = (player.hitbox.x + 30, player.hitbox.y)
        player.scale = 2
        player.animate()

        # End Level

        if current_scene == levels[level][-1] and not current_scene.enemies and not level_beat:
            level_end()
        
        if level_beat:
            player.switch_animation('idle')
            player.input, player.gravity = False, False
            game_paused = False


# DRAW

def draw():
    screen.clear()

    if menu:
        # Moving background
        screen.blit(bg_menu, (bg_x, bg_y % 720))
        screen.blit(bg_menu, (bg_x, bg_y % 720 - 720))

        screen.blit('text_title', (0, 0)) # title

        if menu_scene == 'main': # main menu
            for button in buttons_main:
                button.draw()
            
            for i in range(3):
                screen.draw.text(('LEVELS', 'SETTINGS', 'QUIT')[i], center=buttons_main[i].pos, fontname='roboto_thin', fontsize=75, color=('white' if buttons_main[i].image == 'button_dark' else 'black'))
            
            if controller_mode:
                screen.draw.text('CONTROLLER MODE ENABLED. PRESS K AT ANY POINT TO TOGGLE.', center=(WIDTH/2, 190), fontname='vcr_ocd_mono', fontsize=20)
                screen.draw.text('MENU NAVIGATION IS STILL CONTROLLED BY THE MOUSE.', center=(WIDTH/2, 210), fontname='vcr_ocd_mono', fontsize=15)
        
        elif menu_scene == 'levels': # levels menu
            screen.draw.text('*LEVELS 3 AND 4 ARE CURRENTLY UNFINISHED*', center=(WIDTH/2, 220), fontname='vcr_ocd_mono', fontsize=32) # TODO: Add levels 3 and 4 and remove this text

            for i, button in enumerate(buttons_levels):
                button.draw()

                if levels_unlocked >= i:
                    screen.draw.text(f'LEVEL {i + 1}', center=button.pos, fontname='roboto_thin', fontsize=75, color=('white' if button.image == 'button_dark' else 'black'))
                else:
                    screen.draw.text(f'???', center=button.pos, fontname='roboto_thin', fontsize=75, color=('white' if button.image == 'button_dark' else 'black'))
            
            screen.draw.text('ESC TO GO BACK', center=(640, 650), fontname='roboto_thin', fontsize=40, color='white')

        elif menu_scene == 'settings': # settings menu
            settings_text = [f'INSTANT RESPAWN: {'ON' if instant_respawn else 'OFF'}', # text list for settings menu buttons
                             f'DEBUG MODE: {'ON' if debug_mode else 'OFF'}',
                             f'UNLOCKED LEVELS: {levels_unlocked + 1}',
                             f'HARD MODE: {'ON' if hard_mode else 'OFF'}',
                             f'SOUND EFFECTS: {'ON' if sfx else 'OFF'}',
                             f'MUSIC VOLUME: {int(round(music.get_volume(), 1) * 100)}%']
            
            for i, button in enumerate(buttons_settings):
                button.draw()
                screen.draw.text(settings_text[i], center=button.pos, fontname='roboto_thin', fontsize=35, color=('white' if button.image == 'button_dark' else 'black'))
            
            screen.draw.text('ESC TO GO BACK', center=(640, 660), fontname='roboto_thin', fontsize=40, color='white')
    
    else:
        # Background

        if bg_levels_visible:
            screen.blit('background_levels_0', (0, 0)) # layer 0
            display_background(1, 16) # layer 1
            display_background(2, 8) # layer 2
            display_background(3, 4) # layer 3

        # Behind Entities
    
        for tile in (tiles_back + tiles_animate):
            tile.draw()
        
        for tile in tiles_clip:
            tile.draw()

        if not level_beat:
            # Level Text
            for text in current_scene.text:
                screen.draw.text(text.message, center=(text.x, text.y), fontname='vcr_ocd_mono', fontsize=32, color=text.color)

        # Entities

        for enemy in current_scene.enemies:
            enemy.draw()

        if player.visible:
            player.draw()

        if not level_beat:
            # Attacks
            for attack in current_scene.attacks:
                attack.draw()
            for enemy_attack in current_scene.enemy_attacks:
                enemy_attack.draw()

            # In Front of Entities
            if not debug_mode:
                for tile in tiles_front:
                    tile.draw()

            # Explosions
            for explosion in current_scene.explosions:
                explosion.draw()

            # HUD and Debug
            hud_timer.draw()
            time_elapsed = time.time() - level_start_time - level_subtracted_time
            screen.draw.text(f'{int(time_elapsed // 60)}:{time_elapsed % 60:.3f}', center=hud_timer.center, fontname='vcr_ocd_mono', fontsize=32)

            hud_box_overclock.draw()
            screen.draw.text(f'OVERCLOCKING: {int((player.time_mod - 0.2) / -0.8 * 100) + 100}%', center=hud_box_overclock.center, fontname='vcr_ocd_mono', fontsize=20)

            if controller_mode:
                hud_controller.draw()
                screen.draw.text(f'CONTROLLER CONNECTED', center=hud_controller.center, fontname='vcr_ocd_mono', fontsize=16)

            if debug_mode:
                screen.draw.rect(player.hitbox, 'RED')
                for enemy in current_scene.enemies:
                    screen.draw.rect(enemy.hitbox, 'RED')

                hud_box_overclock_simple.draw()
                screen.draw.text(f'SIMPLE TIME MOD: {player.time_mod_simple:.1f}', center=hud_box_overclock_simple.center, fontname='vcr_ocd_mono', fontsize=16)

            # Death Screen
            if not player.alive and not game_paused:
                hud_box_death_screen.draw(), hud_box_death_screen.draw() # not the cleanest but drawing twice doubles the opacity
                screen.draw.text(f'PRESS {'Y' if controller_mode else 'R'} TO RESPAWN', center=hud_box_death_screen.pos, fontname='vcr_ocd_mono', fontsize=60)

            if game_paused:
                for i, button in enumerate(buttons_pause):
                    button.draw(), button.draw() # not the cleanest but drawing twice doubles the opacity
                    screen.draw.text(['BACK TO GAME', 'RESTART LEVEL', 'EXIT TO MENU'][i], center=button.pos, fontname='roboto_thin', fontsize=50, color=('white' if button.image == 'button_dark' else 'black'))

        if level_end_screen:
            for tile in tiles_clip:
                tile.draw()

            level_beat_box_up.draw(), level_beat_box_up.draw() # not the cleanest but drawing twice doubles the opacity
            level_beat_box_down.draw(), level_beat_box_down.draw() # not the cleanest but drawing twice doubles the opacity

            screen.draw.text(f'END OF LEVEL {level + 1}', center=level_beat_box_up.pos, fontname='vcr_ocd_mono', fontsize=70, color=('RED' if hard_mode else 'WHITE'))
            screen.draw.text(f'{'B' if controller_mode else 'ESC'} TO CONTINUE', center=level_beat_box_down.pos, fontname='vcr_ocd_mono', fontsize=32, color=('RED' if hard_mode else 'WHITE'))

            # Stats

            time_stat_box.draw(), time_stat_box.draw() # not the cleanest but drawing twice doubles the opacity
            enemy_stat_box.draw(), enemy_stat_box.draw() # not the cleanest but drawing twice doubles the opacity
            screen.draw.text(f'TIME: {int(level_final_time // 60)}:{level_final_time % 60:0>6.3f}', center=time_stat_box.pos, fontname='vcr_ocd_mono', fontsize=32, color=('RED' if hard_mode else 'WHITE'))
            screen.draw.text(f'KILLS: {level_enemies_killed}/{level_enemies_total}', center=enemy_stat_box.pos, fontname='vcr_ocd_mono', fontsize=32, color=('RED' if hard_mode else 'WHITE'))


# START

init_menu()
pgzrun.go()