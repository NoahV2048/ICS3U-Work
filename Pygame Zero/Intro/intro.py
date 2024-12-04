import pgzrun, os
import math

os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 1280
HEIGHT = 1024

alien = Actor('alien')
r = 0

def on_mouse_down(pos, button):
    if button == mouse.LEFT and alien.collidepoint(pos):
        set_alien_hurt()

def set_alien_hurt():
    alien.image = 'alien_hurt'
    sounds.eep.play()
    clock.schedule_unique(set_alien_normal, 1.0)

def set_alien_normal():
    alien.image = 'alien'

def update():
    global r
    r += 10 * math.pi/360
    alien.pos = (WIDTH / 2 + 100 * math.cos(r), HEIGHT / 2 + 100 * math.sin(r))
    if alien.left > WIDTH:
        alien.right = 0

def draw():
    screen.clear()
    alien.draw()

pgzrun.go()