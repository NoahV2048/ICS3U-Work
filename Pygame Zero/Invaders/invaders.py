import pgzrun
from pgzhelper import * 
import os

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 800
HEIGHT = 600
ALIENS_PER_ROW = 11

# Initialize Global Variables
score = 0

# Initialize primary Actors
player = Actor('playership2_orange')
player.pos = (WIDTH // 2, HEIGHT - 50)
player.scale = 0.5 #resizing sprite to something more reasonable

aliens = []
for x in range(ALIENS_PER_ROW):
    a = Actor('enemygreen1')
    a.scale = 0.5
    xc = (WIDTH - ALIENS_PER_ROW * 60)//2 + (x * 60) + 30 # A little math to center the row
    a.center = (xc, 150)
    aliens.append(a)

bullet = None
explosions = []

# Funcs

def move_aliens():
    for alien in aliens:
        alien.x += 1

def kaboom(pos):
    global bullet
    bullet = None
    
    explosion = Actor('explosion00', center=(pos))
    explosion.stage = 0
    explosions.append(explosion)
    clock.schedule(end_kaboom, 0.5)

def end_kaboom():
    explosions.pop(0)

# Event Handlers - Handle one-time input
# def on_mouse_down(pos, button):  
# def on_mouse_up(pos, button):
# def on_mouse_move(pos, rel, buttons):
# def on_key_up(key, unicode):
# def on_music_end():

def on_key_down(key, unicode):
    global bullet
    
    if key == keys.SPACE and bullet == None:
        bullet = Actor('laserblue01', player.pos)
        bullet.scale = 0.75


# Update - Handle ongoing input, update positions, check interactions
def update():
    
    if keyboard[keys.LEFT] and player.left > 0:
        player.x -= 5
    if keyboard[keys.RIGHT] and player.right < WIDTH:
        player.x += 5
        
    if bullet != None:
        bullet.y -= 5
        if bullet.top < 0:
            kaboom(bullet.midtop)
        for alien in aliens:
            if bullet != None:
                if bullet.colliderect(alien):
                    aliens.remove(alien)
                    kaboom(bullet.midtop)
    
    for alien_bullet in alien_bullets:
        sounds.explosioncrunch_003.play()
    
    move_aliens()

    # Display explosions
    for explosion in explosions:
        explosion.scale=0.1
        explosion.stage += 0.25
        explosion.image = f'explosion0{math.floor(explosion.stage % 9)}'

# Draw - Draw each Actor, and any other UI elements
def draw():
    screen.clear()
    
    for alien in aliens:
        alien.draw()
        
    if bullet != None:
        bullet.draw()
        
    player.draw()

    for explosion in explosions:
        explosion.draw()


# Setup, Scheduling, and Go:
pgzrun.go()