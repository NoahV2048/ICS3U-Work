import random
import pgzrun

# Screen dimensions (WIDTH , HEIGHT)
WIDTH, HEIGHT = 1280, 1024

# Create shooting star Actor
shooting_star = 'star'    # make sure you’ve saved the star.png file
# give it a starting position of (0,0)

# Generate random stars (the ones that don’t move)
# You will need a for loop to create 20 stars and append them to a list

stars = [] # empty list

for i in range (20): # 20 stars
    starx  = random.randint(0, WIDTH)  # generate a random x value using randint
    stary  = random.randint(0, HEIGHT)  # a random y value - make sure the star is in the sky
    mystar = (starx, stary) # you may copy this
    stars.append(mystar)  #you may copy this


def draw():
    screen.clear()
    
    # Draw sky 
    

    
    # Draw ground ensure it’s on the bottom half of the screen only
   
    
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
    



    # Draw stars you can copy this line
  
    for x, y in stars:
        screen.draw.filled_circle((x, y), 3, "yellow")
    
    # Draw bush using filled circles and / or triangles
        
    # Draw shooting star actor
   

def update():
    # Animate shooting star by moving it
    shooting_star.x +=2
    # now you deal with the y
  
    if shooting_star.x > WIDTH or shooting_star.y > HEIGHT:
        shooting_star.pos = (0, 0)  # Reset position

pgzrun.go()