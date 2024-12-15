import math as m, pygame as pg, numpy as np
from sys import exit

# MAIN SETTINGS:
x_sensitivity, y_sensitivity = 4, 4
walking_speed = 3
framerate = 120
screenx, screeny = 1536, 864
farinf, fov = False, 60


# Pygame Setup:
pg.init()
screen = pg.display.set_mode((screenx, screeny))
pg.display.set_caption('3D Render')
clock = pg.time.Clock()
font = pg.font.SysFont("Comic Sans MS", 15)

# Mouse setup:
pg.mouse.set_visible(False)
pg.event.set_grab(True)
pg.mouse.set_pos(screenx / 2, screeny / 2)

# 3D Setup:
near, far = 0.1, 100
player_coords, altaz = np.array([0., 0., 0.]), [0., 0.]
movement_speed, aspect_ratio = walking_speed / framerate, screenx / screeny
scale_factor, zrow = 1 / m.tan(fov * 0.5 * m.pi / 180), -(far / (far - near)) ** int(farinf == True)


# Litrally The Matrix:
projection_matrix = np.array([
    [scale_factor, 0, 0, 0],
    [0, aspect_ratio * scale_factor, 0, 0],
    [0, 0, zrow, zrow * near],
    [0, 0, -1, 0]
])

def objecttoworld(PYR, translation):
    pitch_matrix = np.array([
        [1, 0, 0, 0],
        [0, m.cos(PYR[0]), -m.sin(PYR[0]), 0],
        [0, m.sin(PYR[0]), m.cos(PYR[0]), 0],
        [0, 0, 0, 1]
    ])
    yaw_matrix = np.array([
        [m.cos(PYR[1]), 0, m.sin(PYR[1]), 0],
        [0, 1, 0, 0],
        [-m.sin(PYR[1]), 0, m.cos(PYR[1]), 0],
        [0, 0, 0, 1]
    ])
    roll_matrix = np.array([
        [m.cos(PYR[2]), -m.sin(PYR[2]), 0, 0],
        [m.sin(PYR[2]), m.cos(PYR[2]), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    translation_matrix = np.array([
        [1, 0, 0, translation[0]],
        [0, 1, 0, translation[1]],
        [0, 0, 1, translation[2]],
        [0, 0, 0, 1]
    ])
    return translation_matrix @ roll_matrix @ yaw_matrix @ pitch_matrix

def worldtocamera():
    translation_matrix = np.array([
        [1, 0, 0, -player_coords[0]],
        [0, 1, 0, -player_coords[1]],
        [0, 0, 1, -player_coords[2]],
        [0, 0, 0, 1]
    ])
    yaw_matrix = np.array([
        [m.cos(altaz[1]), 0, m.sin(altaz[1]), 0],
        [0, 1, 0, 0],
        [-m.sin(altaz[1]), 0, m.cos(altaz[1]), 0],
        [0, 0, 0, 1]
    ])
    pitch_matrix = np.array([
        [1, 0, 0, 0],
        [0, m.cos(altaz[0]), -m.sin(altaz[0]), 0],
        [0, m.sin(altaz[0]), m.cos(altaz[0]), 0],
        [0, 0, 0, 1]
    ])
    return pitch_matrix @ yaw_matrix @ translation_matrix

# Functions:
def clipspace(vector):
    while len(vector) < 4:
        vector.append(1)
    vector = projection_matrix @ worldtocamera() @ objecttoworld([0, 0, 0], [0, 0, 0]) @ vector
    return vector

def raster(vector) -> tuple:
    x, y = vector[0] / vector[3], vector[1] / vector[3]
    return (screenx * (x + 1) * 0.5,
            screeny * (1 - (y + 1) * 0.5))

def visible(vectors) -> bool:
    for vector in vectors:
        x, y, z, w = vector
        if (-w <= x <= w) and (-w <= y <= w) and (0 <= z <= w) and (w != 0):
            return True
    return False

# Clipping:
def linear_x(v1, v2, pass1, pass2):
    x, y, z, w = v1
    X, Y, Z, W = v2
    minclip, maxclip = -W, W
    if X > maxclip:
        clip = maxclip
    elif minclip > X:
        clip = minclip
    t = (clip - x) / (X - x)
    return [clip,
            y + (Y - y) * t,
            z + (Z - z) * t,
            w + (W - w) * t]

def linear_y(v1, v2):
    x, y, z, w = v1
    X, Y, Z, W = v2
    minclip, maxclip = -W, W
    if X > maxclip:
        clip = maxclip
    elif minclip > X:
        clip = minclip
    else:
        clip = 0
    t = (clip - y) / (Y - y)
    return [x + (X - x) * t,
            clip,
            z + (Z - z) * t,
            w + (W - w) * t]

def linear_z(v1, v2):
    if v2[0] > v2[3]:
        [v1[0] + (v2[0] - v1[0] * (v2[2] - v1[2]) * (-near - v1[2])),
                v1[0] + (v2[1] - v1[1] * (v2[2] - v1[2]) * (-near - v1[2])),
                -near]
    elif -v2[3] > v2[0]:
        pass

# Polyhedron Functions:
def clip_polygon(vectors):

    # x clipping
    vectors.append(vectors[0])
    temp_vectors, filtermap = [], [bool(-vector[3] <= vector[0] <= vector[3]) for vector in vectors]
    for i in range(0, len(vectors) - 1):
        if filtermap[i] and filtermap[i + 1]:
            temp_vectors.append(vectors[i])
        elif filtermap[i] and not filtermap[i + 1]:
            temp_vectors.append(vectors[i])
            temp_vectors.append(linear_x(vectors[i], vectors[i + 1], 0, 0))
        elif filtermap[i + 1] and not filtermap[i]:
            temp_vectors.append(linear_x(vectors[i + 1], vectors[i], 0, 0))
    vectors = temp_vectors

    # y clipping
    vectors.append(vectors[0])
    temp_vectors, filtermap = [], [bool(-vector[3] <= vector[1] <= vector[3]) for vector in vectors]
    for i in range(0, len(vectors) - 1):
        if filtermap[i] and filtermap[i + 1]:
            temp_vectors.append(vectors[i])
        elif filtermap[i] and not filtermap[i + 1]:
            temp_vectors.append(vectors[i])
            temp_vectors.append(linear_y(vectors[i], vectors[i + 1]))
        elif filtermap[i + 1] and not filtermap[i]:
            temp_vectors.append(linear_y(vectors[i + 1], vectors[i]))
    vectors = temp_vectors

    return vectors

    # if (-w <= x <= w) and (-W <= X <= W):
    #     temp_vectors.append(vectors[i])
    # elif (-w <= x <= w) and (not (-W <= X <= W)):
    #     temp_vectors.append(vectors[i])
    #     temp_vectors.append(linearx(vectors[i], vectors[i + 1]))
    # elif (not (-w <= x <= w)) and (-W <= X <= W):
    #     temp_vectors.append(linearx(vectors[i + 1], vectors[i]))
    


    
    x, y, z, w = vectors[i]
    X, Y, Z, W = vectors[i + 1]
    
    if (-w <= x <= w) and (-w <= y <= w) and (0 <= z <= w) and (w != 0):
        pass

def display_polyhedron(polyhedron):
    ready_to_clip = [clipspace(vertex) for vertex in polyhedron.vertices]
    for face in polyhedron.faces:
        face_vertices = [ready_to_clip[i] for i in face]
        if visible(face_vertices):
            clipped = clip_polygon(face_vertices)
            rastered = [raster(vertex) for vertex in clipped]
            pg.draw.lines(screen, (255, 255, 255), True, rastered, 3)
            # width not customizable? # lines draw and not polygon? # no colour fill?

# Line Functions:
def clip_line(vector):
    return vector
    x, y, z, w = vector
    if (-w <= x <= w) and (-w <= y <= w) and (0 < z <= w) and (w != 0):
        return (screenx * (NDC[0] + 1) / 2, screeny * (-NDC[1] + 1) / 2)
    else:
        return (screenx * (NDC[0] + 1) / 2, screeny * (-NDC[1] + 1) / 2)
    
    ###
    return clipspace([v1[0] + (v2[0] - v1[0] * (v2[2] - v1[2]) * (-near - v1[2])),
            v1[0] + (v2[1] - v1[1] * (v2[2] - v1[2]) * (-near - v1[2])),
            -near])


def display_line(line):
    ready_to_clip = [clipspace(vertex) for vertex in line.vertices]
    ready_to_raster = [clip_line(vertex) for vertex in ready_to_clip]
    rastered = [raster(vertex) for vertex in ready_to_raster]
    pg.draw.lines(screen, (255, 255, 255), line.closed, rastered, 1)
    # width not customizable?

# Class Init

polyhedra, lines = [], []

class Polyhedron:
    def __init__(self, vertices: list, faces: list):
        self.vertices, self.faces = vertices, faces
        polyhedra.append(self)

class Line:
    def __init__(self, vertices: list, closed: bool):
        self.vertices, self.closed = vertices, closed
        lines.append(self)

pyramid = Polyhedron([[5, 0, -5], [-5, 0, -5], [0, 0, -10], [0, 5, -7]],
                     [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])

cube = Polyhedron([[9, 0, -9], [10, 0, -9], [9, 0, -10], [10, 0, -10], [9, 1, -9], [10, 1, -9], [9, 1, -10], [10, 1, -10]],
                  [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]])

square = Line([[-3, 1, 3], [-2, 1, 3], [-2, 2, 3], [-3, 2, 3]], True)

# Pygame loop

while True:
    # Display setup
    screen.fill((0, 0, 0))
    text_surface = font.render(f"{player_coords}", True, (255, 255, 255))
    screen.blit(text_surface, (0, screeny - 20))

    for polyhedron in polyhedra:
        display_polyhedron(polyhedron)
    for line in lines:
        display_line(line)
    
    # Key events

    keys = pg.key.get_pressed()
    if keys[pg.K_w]:
        player_coords += np.array([m.sin(altaz[1]), 0, -m.cos(altaz[1])]) * movement_speed
    elif keys[pg.K_s]:
        player_coords += np.array([-m.sin(altaz[1]), 0, m.cos(altaz[1])]) * movement_speed
    if keys[pg.K_a]:
        player_coords += np.array([-m.cos(altaz[1]), 0, -m.sin(altaz[1])]) * movement_speed
    elif keys[pg.K_d]:
        player_coords += np.array([m.cos(altaz[1]), 0, m.sin(altaz[1])]) * movement_speed
    if keys[pg.K_SPACE]:
        player_coords += np.array([0, 1, 0]) * movement_speed
    elif keys[pg.K_c]:
        player_coords += np.array([0, -1, 0]) * movement_speed

    # Mouse events

    mouse_pos = pg.mouse.get_pos()
    if (mouse_pos[0] in [0, screenx - 1]) or (mouse_pos[1] in [0, screeny - 1]):
        pg.mouse.set_pos(screenx / 2, screeny / 2)

    mouse_movement = pg.mouse.get_rel()
    altaz[0] += mouse_movement[1] * y_sensitivity * m.pi / 7200
    if altaz[0] > m.pi / 2:
        altaz[0] = m.pi / 2
    elif altaz[0] < -m.pi / 2:
        altaz[0] = -m.pi / 2

    altaz[1] += mouse_movement[0] * x_sensitivity * m.pi / 7200
    altaz[1] = altaz[1] % (m.tau)

    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
            elif event.key == pg.K_LSHIFT:
                if movement_speed == 1 / framerate:
                    movement_speed = 3 / framerate
                else:
                    movement_speed = 1 / framerate
            elif event.key == pg.K_q:
                print(f"\nDEBUG:\n\nALT: {altaz[0]}\nAzimuth: {altaz[1]}\nCoords: {player_coords}\nALSO: {pyramid.vertices[(pyramid.edges[0])[0]]}")

        if event.type == pg.QUIT:
            pg.quit()
            exit()

    pg.display.update()
    clock.tick(framerate)