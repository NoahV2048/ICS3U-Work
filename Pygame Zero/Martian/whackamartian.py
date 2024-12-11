import pgzrun
import os
import random 

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 600
HEIGHT = 600

# Global Variables
score = 0
lives = 10

# Initialize primary Actors
alien = Actor('alien_front', (WIDTH//2, HEIGHT//2))

def set_alien_hurt():
    global score
    alien.image = 'alien_hit'
    clock.schedule_unique(set_alien_normal, 1.0)
    
def set_alien_normal():
    alien.image = 'alien_front'

def move_alien():
    x = random.randint(64, WIDTH - 64)
    y = random.randint(78, HEIGHT - 78)
    
    animate(alien, pos = (x, y), tween='accel_decel') # Animate the alien's motion to the new position, using the animate() function.
    
    
# Mouse and Keyboard Events

def on_mouse_down(pos, button):
    global lives, score
    
    if alien.collidepoint(pos):
        if lives > 0:
            set_alien_hurt()
            score += 1
            sounds.laser_000.play() # Play a sound on hit, and increase the player's score.
    else:
        if lives > 0:
            lives -= 1 # Subtract 1 from the player's lives when they miss.
            sounds.laser_002.play()
        if lives == 0:
            clock.unschedule(move_alien) # When the player's lives reach zero, stop the alien's motion.

# Update - Handle ongoing input, update positions, check interactions
def update():
    pass
    
# Draw - Draw each Actor, and any other UI elements
def draw():
    screen.clear()
    screen.blit('colored_shroom', (0, 0))
    alien.draw()
    
    # Draw the player's score and lives on the screen.
    screen.draw.text(f'Lives: {lives}', (10, 10), fontsize=50)
    screen.draw.text(f'Score: {score}', topright=(590, 10), fontsize=50)
    
    if lives == 0: # Display a Game Over message when the player's lives reach zero.
        screen.draw.text(f'GAME OVER', center=(300, 300), fontsize=100)

# Go:
# Schedule the alien to move every 3 seconds.
clock.schedule_interval(move_alien, 2)
pgzrun.go()