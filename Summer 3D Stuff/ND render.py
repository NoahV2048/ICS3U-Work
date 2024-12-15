import math as m, numpy as np, pygame as pg, functools
from sys import exit

# Setup

# my 3d renderer is cleaner should I share that

pg.init()
screenxy = [1920, 1080]
scalevalue = 50
screen = pg.display.set_mode((screenxy[0], screenxy[1]))
pg.display.set_caption('ND Render')
clock = pg.time.Clock()

dimension_number, dist, depth, stereo_dist = 3, 300, True, 3
player_coords = []
measure = 100

# Functions setup

def stereo(vector):
    try:
        vector = np.matmul(vector, matrix)
    except:
        pass
    while len(vector) > 3:
        temp_vector = vector
        try:
            stereo_factor = measure * stereo_dist / (measure * stereo_dist - vector[len(vector) - 1])
        except:
            stereo_factor = 1
        vector = []
        for i in range (0, len(temp_vector) - 1):
            vector.append(stereo_factor * temp_vector[i])

    while len(vector) < 3:
        vector = np.append(vector, 0)

    vector[2] = dist - vector[2]

    return vector

def project(vector):
    if depth and vector[2] > 0:
     #   if vector[2] == 0:
      #      vector[2] = 0.01
        depth_factor = scalevalue / vector[2]
    else:
        depth_factor = 1

    return (screenxy[0] / 2 + (depth_factor) * (vector[0]),
            screenxy[1] / 2 + (depth_factor) * (vector[1]))

def linear_at_z0(v1, v2):
    return [v1[0] + (v2[0] - v1[0] * (v2[2] - v1[2]) * (1 - v1[2])),
            v1[0] + (v2[1] - v1[1] * (v2[2] - v1[2]) * (1 - v1[2])),
            1]

def draw_edges():
    projcoords = [project(i) for i in coords3D]

    for i in range(0, len(projcoords)):
        for j in range(i, len(projcoords)):
            if not ((coords3D[i][2]) < 1 and (coords3D[j][2] < 1)):
                if coords3D[i][2] < 1:
                    projcoords[i] = project(linear_at_z0(coords3D[j], coords3D[i]))
                elif coords3D[j][2] < 1:
                    projcoords[j] = project(linear_at_z0(coords3D[i], coords3D[j]))
                dif = [(coords[j][k]-coords[i][k]) for k in range(0, len(coords[0]))]
                if dif.count(0) == len(coords[0]) - graycode_value:
                    pg.draw.line(screen, (255, 255, 255), projcoords[i], projcoords[j], 3)
    return

def getmatrices() -> list:
    rotation_matrices = []
    for n, i in enumerate(theta):
        temp_matrix = []
        for j in range(0, dimension_number):
            temp_row = []
            for k in range(0, dimension_number):
                if j in matrix_reference[n] and k in matrix_reference[n]:
                    if j == k:
                        temp_row.append(m.cos(i))
                    elif j > k:
                        temp_row.append(-m.sin(i))
                    elif j < k:
                        temp_row.append(m.sin(i))
                elif j == k:
                    temp_row.append(1)
                else:
                    temp_row.append(0)
            temp_matrix.append(temp_row)
        rotation_matrices.append(temp_matrix)
    try:
        return functools.reduce(np.dot, np.array(rotation_matrices))
    except:
        return

def dimension_init():
    theta, coords, matrix_reference = [], [], []
    for i in range (0, m.comb(dimension_number, 2)):
        theta.append(float(0))

    for i in range(0, 2**dimension_number):
        coord = []
        for j in range(0, dimension_number):
            coord.insert(0, ((i >> j) % 2) * 2 * measure - measure)
        coords.append(coord)

    for i in range(0, dimension_number):
        for j in range(i + 1, dimension_number):
            matrix_reference.append([i, j])
    
    return [np.array(theta), coords, matrix_reference, 1]

theta, coords, matrix_reference, graycode_value = dimension_init()

# Main
# Loop

while True:
    screen.fill((0, 0, 0))

    matrix = getmatrices()
    theta += m.pi / 360
    
    coords3D = [stereo(i) for i in coords]
    draw_edges()

    keys = pg.key.get_pressed()
    if depth:
        if keys[pg.K_w]:
            dist += -1
        elif keys[pg.K_s]:
            dist += 1

    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_g:
                if graycode_value < dimension_number:
                    graycode_value += 1
            elif event.key == pg.K_h:
                if graycode_value > 0:
                    graycode_value -= 1
            elif event.key == pg.K_f:
                if depth:
                    depth = False
                else:
                    depth = True
            elif event.key == pg.K_q:
                stereo_dist += -0.5
            elif event.key == pg.K_e:
                stereo_dist += 0.5
            elif event.key == pg.K_UP:
                dimension_number += 1
                theta, coords, matrix_reference, graycode_value = dimension_init()
            elif event.key == pg.K_DOWN:
                if dimension_number != 0:
                    dimension_number += -1
                    theta, coords, matrix_reference, graycode_value = dimension_init()
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
            elif event.key == pg.K_i:
                print(f"\nDEBUG:\n\nAngles: {theta}\n\nMatrices: {matrix}")

        if event.type == pg.QUIT:
            pg.quit()
            exit()

    pg.display.update()
    clock.tick(60)