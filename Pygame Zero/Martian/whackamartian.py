import pgzrun, os, random, pygame

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 600
HEIGHT = 600

# Global Variables
score = 0
lives = 5
frames = 0
cooldown = 0
game_started, whack = False, False # events

# Initialize primary Actors
alien = Actor('alien_stand', (WIDTH//2, 450))
alien.moving = False
indicator = Actor('yes', (WIDTH-50, HEIGHT-50))
mallet = Actor('whack_mallet', anchor=('right', 'bottom'))

def start_game():
    global game_started
    game_started = True

    # Schedule the alien to move every 3 seconds.
    clock.schedule(move_alien, 2)

def set_alien_hurt():
    global score
    alien.image = 'alien_hit'
    clock.schedule_unique(set_alien_normal, 1.0)
    
def set_alien_normal():
    alien.image = 'alien_front'

def move_alien():
    x = random.randint(64, WIDTH - 64)
    y = random.randint(78, HEIGHT - 78)
    
    alien.moving = True
    animate(alien, pos=(x, y), tween='accel_decel', duration=0.5, on_finished=stop_moving) # Animate the alien's motion to the new position, using the animate() function.

def stop_moving():
    alien.moving = False
    set_alien_normal()

    if lives > 0:
        clock.schedule(move_alien, 2 ** (-score / 12 + 1))

def rotate_alien():
    animate(alien, angle=(alien.angle+360), tween='accel_decel', duration=0.75) # Rotate the dude
    animate(alien, y=400, tween='decelerate', duration=0.5)
    clock.schedule_unique(jump, 0.5)

def jump():
    animate(alien, y=450, tween='accelerate', duration=0.5)

def smash_hammer(pos): # timing gets a bit messed up later
    global whack
    whack = True

    mallet.image = 'whack_mallet'
    mallet.pos = (pos[0] + 156, pos[1])
    mallet.angle = -120

    animate(mallet, angle=30, tween='accelerate', duration=(2 ** (-score / 12 - 1)), on_finished=kaboom)

def kaboom():
    mallet.image = 'whack_burst_edit'
    mallet.angle = 30
    sounds.laser_003.play()
    clock.schedule_unique(end_whack, (2 ** (-score / 12 - 1)))

def end_whack():
    global whack
    whack = False

# Mouse and Keyboard Events
def on_key_down(key):
    global game_started

    if key == keys.SPACE and not game_started:
        start_game()

def on_mouse_down(pos, button):
    global lives, score, cooldown

    if cooldown == 0 and game_started and lives > 0:
        cooldown = 45
        smash_hammer(pos)
        clock.unschedule(end_whack)

        if alien.collidepoint(pos):
            if not alien.moving:
                set_alien_hurt()
            score += 1
            sounds.laser_000.play() # Play a sound on hit, and increase the player's score.
    
        else:
            lives -= 1 # Subtract 1 from the player's lives when they miss.
            sounds.laser_002.play()

            if lives == 0: # final whack
                clock.unschedule(move_alien) # When the player's lives reach zero, stop the alien's motion.
                alien.moving = True
                animate(alien, pos=(300, 450), tween='accel_decel', duration=1, on_finished=stop_moving)
                clock.schedule_interval(rotate_alien, 1)


# Update - Handle ongoing input, update positions, check interactions
def update():
    mouse_pos = pygame.mouse.get_pos() # if you want the indicator to follow the mouse
    indicator.pos = (mouse_pos[0] - 10, mouse_pos[1] - 10)

    global frames, cooldown

    cooldown -= 1 if cooldown > 0 else 0

    if cooldown == 0:
        indicator.image = 'yes'
    else:
        indicator.image = 'no'

    if alien.moving:
        frames += 1
        if frames == 5:
            alien.image = 'alien_walk1'
        elif frames == 10:
            alien.image = 'alien_walk2'
            frames = 0


# Draw - Draw each Actor, and any other UI elements
def draw():
    screen.clear()
    screen.blit('colored_shroom', (0, 0))
    
    alien.draw()

    if lives > 0 and not whack: indicator.draw()
    if whack: mallet.draw()

    if lives == 0: # Display a Game Over message when the player's lives reach zero.
        screen.draw.text(f'GAME OVER', center=(300, 250), fontsize=100, shadow=(1, 1))
    elif not game_started:
        screen.draw.text(f'PRESS SPACE', center=(300, 250), fontsize=100, shadow=(1, 1))

    # Draw the player's score and lives on the screen.
    screen.draw.text(f'Lives: {lives}', (15, 15), fontsize=50, shadow=(1, 1))
    screen.draw.text(f'Score: {score}', topright=(WIDTH-15, 15), fontsize=50, shadow=(1, 1))

# Go:
pgzrun.go()