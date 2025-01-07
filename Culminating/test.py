import pgzrun
from pgzhelper import *
import os

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on scene.
pygame.mouse.set_visible(False) #Make mouse cursor invisible. 
WIDTH = 600
HEIGHT = 600

player = Actor("microwave_idle_0")
player.pos = WIDTH//2, 50
player.dx = 0
player.dy = 0


def on_key_down(key):
    if key == keys.SPACE:
        player.dy = -20
        
    if key == keys.LEFT:
        player.dx = -5
    if key == keys.RIGHT:
        player.dx = 5

def update():
    
    player.x += player.dx
    player.y += player.dy
    
    #accelleration    
    player.dy += 1
    
    player.dx *= 0.99
    
    if player.bottom >= HEIGHT:
        player.dy = 0
        player.bottom = HEIGHT

def draw():
    screen.clear()
    player.draw()
    
pgzrun.go()