import random
import pgzrun

# Screen dimensions (WIDTH , HEIGHT)
WIDTH, HEIGHT = 1280, 1024


shooting_star = Actor('star', (0, 0))

stars = []

for i in range(20):
    starx = random.randint(0, WIDTH)
    stary = random.randint(int(HEIGHT / 2), HEIGHT)
    mystar = (starx, stary)
    stars.append(mystar)


def draw():
    screen.clear()
    
    screen.fill((200, 200, 200))
    ground = Rect((0, HEIGHT/2), (WIDTH, HEIGHT))

    screen.draw.filled_rect(ground, 'brown')
   
    for star in stars:
        star.draw()

    
    # Draw snowman
    # use multiple screen.draw.filled_circle… 
    # you can find those here:
    # https://pygame-zero.readthedocs.io/en/stable/builtins.html
    screen.draw.filled_circle((400, 400), 50, "white") # Bottom circle
    # Middle circle
    # Head
    # Left eye
    # Right eye
    # Nose
    # anything else for your snowman?
    

    for x, y in stars:
        screen.draw.filled_circle((x, y), 3, "yellow")
    
    # Draw bush using filled circles and / or triangles
        
    # Draw shooting star actor
    shooting_star.draw()
   

def update():
    # Animate shooting star by moving it
    shooting_star.x +=2
    # now you deal with the y
  
    if shooting_star.x > WIDTH or shooting_star.y > HEIGHT:
        shooting_star.pos = (0, 0)  # Reset position

pgzrun.go()