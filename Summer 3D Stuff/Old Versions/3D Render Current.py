import math as m, numpy as np, pygame as pg
from sys import exit

# Pygame Setup

pg.init()
screenx, screeny = 1920, 1080
screen = pg.display.set_mode((screenx, screeny))
pg.display.set_caption('3D Render')
clock = pg.time.Clock()

# 3D Setup

depth = True
player_coords, altaz = np.array([0.00, 0.00, 0.00]), [0.00, 0.00]

width, height, near, fov = screenx, screeny, 0, m.pi / 2

projection_matrix = np.array([
    [1 / m.tan(fov / 2), 0, 0, 0],
    [0, (height / width) / m.tan(fov / 2), 0, 0],
    [0, 0, -1, -2 * near],
    [0, 0, -1, 0]
])

def transformation_matrix():
    return np.array([
        [1, 0, 0, - player_coords[0]],
        [0, 1, 0, - player_coords[1]],
        [0, 0, 1, - player_coords[2]],
        [0, 0, 0, 1]
    ]), np.array([
        [m.cos(altaz[1]), 0, m.sin(altaz[1]), 0],
        [0, 1, 0, 0],
        [-m.sin(altaz[1]), 0, m.cos(altaz[1]), 0],
        [0, 0, 0, 1]
    ]), np.array([
        [1, 0, 0, 0],
        [0, m.cos(altaz[0]), -m.sin(altaz[0]), 0],
        [0, m.sin(altaz[0]), m.cos(altaz[0]), 0],
        [0, 0, 0, 1]
    ])

# Polyhedra

polyhedra = []

class Polyhedron:
    def __init__(self, vertices, edges, faces):
        self.vertices, self.edges, self.faces = vertices, edges, faces
        polyhedra.append(self)

pyramid = Polyhedron([[60, 0, 60], [60, 0, -60], [90, 0, 0], [75, 90, 0]],
                     [[0,1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]],
                     [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])
square = Polyhedron([[360, 0, 360], [-360, 0, 360], [360, 720, 360], [-360, 720, 360]], 0, 0)

# Functions setup

def connect(polyhedron):
    proj_vertices = project(verticesyuppp)
    for edge in polyhedron.edges:
        pg.draw.line(screen, (255, 255, 255), edge[0], edge[1], 3)

def project(polyhedron):
    for vertex in polyhedron.vertices:
        vector = np.matmul(matrix, vertex)

    if depth:
        try:
            depth_factor = (100 / (dist - vector[2]))
        except:
            depth_factor = 1
    else:
        depth_factor = 1

    return (screenx / 2 +(depth_factor) * (vector[0]),
            screeny / 2 +(depth_factor) * (vector[1]))

def matrix_update(theta_xy, theta_xz, theta_yz):
    mxy, mxz, myz = (np.identity(3), ) * 3
    mxy[0][0], mxy[1][1] = (m.cos(theta_xy), ) * 2
    mxz[0][0], mxz[2][2] = (m.cos(theta_xz), ) * 2
    myz[1][1], myz[2][2] = (m.cos(theta_yz), ) * 2
    mxy[0][1], mxy[1][0] = -m.sin(theta_xy), m.sin(theta_xy)
    mxz[2][0], mxz[0][2] = -m.sin(theta_xz), m.sin(theta_xz)
    myz[1][2], myz[2][1] = -m.sin(theta_yz), m.sin(theta_yz)
    return np.matmul(myz, mxz)

theta = []

# Mouse setup

pg.mouse.set_visible(True) # Make false
pg.event.set_grab(True)

# Main
# Loop

while True:
    screen.fill((0, 0, 0))
    pg.mouse.set_pos(screenx / 2, screeny / 2)

    np.draw.rect(screen, (255, 255, 255), (newmatrix([60, 60, 60]), (3, 3)))

    matrix = matrix_update(0, altaz[0], altaz[1])

    project(square)

    for polyhedron in polyhedra:
        project(polyhedron)

    keys = pg.key.get_pressed()
    if keys[pg.K_w]:
        player_coords += np.array([m.sin(altaz[1]), 0, m.cos(altaz[1])])
    elif keys[pg.K_s]:
        player_coords += np.array([-m.sin(altaz[1]), 0, -m.cos(altaz[1])])
    elif keys[pg.K_a]:
        player_coords += np.array([m.cos(altaz[1]), 0, -m.sin(altaz[1])])
    elif keys[pg.K_d]:
        player_coords += np.array([-m.cos(altaz[1]), 0, m.sin(altaz[1])])

    mouse_movement = pg.mouse.get_rel()
    if (mouse_movement[1] < 1 and altaz[0] <= m.pi / 2) or (mouse_movement[1] > 1 and altaz[0] >= -m.pi / 2):
        altaz[0] += mouse_movement[1] * m.pi / 360
    altaz[1] += mouse_movement[0] * m.pi / 360

    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_e:
                depth = not depth
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
            elif event.key == pg.K_q:
                print(f"\nDEBUG:\n\nALT: {altaz[0]}\nAzimuth: {altaz[1]}\nCoords: {player_coords}")

        if event.type == pg.QUIT:
            pg.quit()
            exit()

    pg.display.update()
    clock.tick(60)