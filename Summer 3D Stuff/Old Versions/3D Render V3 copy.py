import math as m, numpy as np, pygame as pg
from sys import exit

# Pygame Setup

pg.init()
screenx, screeny = 1536, 864
screen = pg.display.set_mode((screenx, screeny))
pg.display.set_caption('3D Render')
clock = pg.time.Clock()
font = pg.font.SysFont("Comic Sans MS", 15)

# Mouse setup

pg.mouse.set_visible(False)
pg.event.set_grab(True)
pg.mouse.set_pos(screenx / 2, screeny / 2)

# 3D Setup

player_coords, altaz = np.array([0., 0., 0.]), [0., 0.]
width, height, fov = screenx, screeny, (60) * m.pi / 180

projection_matrix = np.array([
    [1 / m.tan(fov / 2), 0, 0, 0],
    [0, (height / width) / m.tan(fov / 2), 0, 0],
    [0, 0, -1, -2 * 0],
    [0, 0, -1, 0]
])

def transformationmatrix():
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
    return projection_matrix @ pitch_matrix @ yaw_matrix @ translation_matrix

def project(vector):
    if len(vector) < 4:
        vector.append(1)
    vector = transformationmatrix() @ vector
    w = vector[3]
    NDC = (vector / w).tolist()
    # if (-w <= vector[0] <= w) and (-w <= vector[1] <= w) and (0 < vector[2] <= w):
    #     return (screenx * (NDC[0] + 1) / 2, screeny * (-NDC[1] + 1) / 2)
    # else:
    #     return (screenx * (NDC[0] + 1) / 2, screeny * (-NDC[1] + 1) / 2)
    if 0 < vector[2] <= w:
        return (screenx * (NDC[0] + 1) / 2, screeny * (-NDC[1] + 1) / 2)
    else:
        return 0

def connect(polyhedron):
    proj_vertices = []
    for vertex in polyhedron.vertices:
        proj_vertices.append(project(vertex))
    for edge in polyhedron.edges:
        e1, e2 = proj_vertices[edge[0]], proj_vertices[edge[1]]
        if type(e1) == tuple and type(e2) == tuple:
            pg.draw.line(screen, (255, 255, 255), e1, e2, 3)
        elif type(e1) == tuple:
            pg.draw.line(screen, (255, 255, 255), e1, linear_at_z1(polyhedron.vertices[edge[0]], polyhedron.vertices[edge[1]]), 3)
        elif type(e2) == tuple:
            pg.draw.line(screen, (255, 255, 255), linear_at_z1(polyhedron.vertices[edge[0]], polyhedron.vertices[edge[1]]), e2, 3)

def linear_at_z1(v1, v2):
    if project([v1[0] + (v2[0] - v1[0] * (v2[2] - v1[2]) * (-1 - v1[2])),
            v1[0] + (v2[1] - v1[1] * (v2[2] - v1[2]) * (-1 - v1[2])),
            -1]) == 0:
        print("oops")
    return project([v1[0] + (v2[0] - v1[0] * (v2[2] - v1[2]) * (-1 - v1[2])),
            v1[0] + (v2[1] - v1[1] * (v2[2] - v1[2]) * (-1 - v1[2])),
            -1])

# Polyhedra

polyhedra = []

class Polyhedron:
    def __init__(self, vertices, edges, faces):
        self.vertices, self.edges, self.faces = vertices, edges, faces
        polyhedra.append(self)

pyramid = Polyhedron([[5, 0, -5], [-5, 0, -5], [0, 0, -10], [0, 10, -7]],
                     [[0,1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]],
                     [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])

# cube = Polyhedron([[10, 0, -10], [9, 0, -9], [10, 0, -9], [-5, 10, -5]],
#                     [[0, 1], [1, 2], [3, 0], [3, 0]],
#                     [])

# Pygame loop

while True:
    # Display setup
    screen.fill((0, 0, 0))
    text_surface = font.render(f"{player_coords}", True, (255, 255, 255))
    screen.blit(text_surface, (0, screeny - 20))

    # Wireframe projections

    for polyhedron in polyhedra:
        connect(polyhedron)

    # Key events

    keys = pg.key.get_pressed()
    if keys[pg.K_w]:
        player_coords += np.array([m.sin(altaz[1]), 0, -m.cos(altaz[1])]) / 60
    elif keys[pg.K_s]:
        player_coords += np.array([-m.sin(altaz[1]), 0, m.cos(altaz[1])]) / 60
    if keys[pg.K_a]:
        player_coords += np.array([-m.cos(altaz[1]), 0, -m.sin(altaz[1])]) / 60
    elif keys[pg.K_d]:
        player_coords += np.array([m.cos(altaz[1]), 0, m.sin(altaz[1])]) / 60
    if keys[pg.K_SPACE]:
        player_coords += np.array([0, 1, 0]) / 60
    elif keys[pg.K_c]:
        player_coords += np.array([0, -1, 0]) / 60

    # Mouse events

    mouse_pos = pg.mouse.get_pos()
    if (mouse_pos[0] in [0, screenx - 1]) or (mouse_pos[1] in [0, screeny - 1]):
        pg.mouse.set_pos(screenx / 2, screeny / 2)

    mouse_movement = pg.mouse.get_rel()
    if (mouse_movement[1] < 1 and altaz[0] <= m.pi / 2) or (mouse_movement[1] > 1 and altaz[0] >= -m.pi / 2):
        altaz[0] += mouse_movement[1] * m.pi / 3600
    altaz[1] += mouse_movement[0] * m.pi / 3600

    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
            elif event.key == pg.K_q:
                print(f"\nDEBUG:\n\nALT: {altaz[0]}\nAzimuth: {altaz[1]}\nCoords: {player_coords}\nALSO: {pyramid.vertices[(pyramid.edges[0])[0]]}")

        if event.type == pg.QUIT:
            pg.quit()
            exit()

    pg.display.update()
    clock.tick(60)