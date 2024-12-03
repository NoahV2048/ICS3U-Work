import pgzrun, os

os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 1280
HEIGHT = 1024

alien = Actor('alien')
alien.pos = 100, 56

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
    alien.left += 2
    if alien.left > WIDTH:
        alien.right = 0

def draw():
    screen.clear()
    alien.draw()

pgzrun.go()