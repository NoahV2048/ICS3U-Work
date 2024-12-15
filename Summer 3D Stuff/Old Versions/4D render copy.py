import math as m, pygame
from sys import exit

pygame.init()

# Setup
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('ND Render')
clock = pygame.time.Clock()

dimension_number, dist, depth, stereo_dist = 3, 300, True, 2.5
player_coords = []
measure = 100

# Functions setup

def vecmatrix(vector, matrix):
    matrix_product = []
    for i in range(0, len(matrix)):
        row_sum = 0
        for j in range(0, min(len(matrix), dimension_number)):
            row_sum += vector[j]*matrix[i][j]
        matrix_product.append(row_sum)
    return matrix_product

def project(vector):
    for i in rotation_matrices:
        vector = vecmatrix(vector, i)
    while len(vector) > 3:
        temp_vector = vector
        try:
            stereo_factor = measure * stereo_dist / (measure * stereo_dist + vector[len(vector) - 1])
        except:
            stereo_factor = 1
        vector = []
        for i in range (0, len(temp_vector) - 1):
            vector.append(stereo_factor * temp_vector[i])

    while len(vector) < 3:
        vector.append(0)
    
    if depth:
        try:
            depth_factor = (100 / (dist+vector[2]))
        except:
            depth_factor = 1
    else:
        depth_factor = 1

    return (640+(depth_factor) * (vector[0]),
            360+(depth_factor) * (vector[1]))

def getmatrices():
    rotation_matrices = []
    
    for i in range(0, len(theta)):
        temp_matrix = []
        for j in range(0, dimension_number):
            temp_row = []
            for k in range(0, dimension_number):
                if j in matrix_reference[i] and k in matrix_reference[i]:
                    if j == k:
                        temp_row.append(m.cos(theta[i]))
                    elif j > k:
                        temp_row.append(-m.sin(theta[i]))
                    elif j < k:
                        temp_row.append(m.sin(theta[i]))
                elif j == k:
                    temp_row.append(1)
                else:
                    temp_row.append(0)
            temp_matrix.append(temp_row)
        rotation_matrices.append(temp_matrix)


def dimension_init():
    theta, coords, matrix_reference = [], [], []
    for i in range (0, m.comb(dimension_number, 2)):
        theta.append(0)

    for i in range(0, 2**dimension_number):
        coord = []
        for j in range(0, dimension_number):
            coord.insert(0, ((i >> j) % 2) * 2 * measure - measure)
        coords.append(coord)

    for i in range(0, dimension_number):
        for j in range(i + 1, dimension_number):
            matrix_reference.append([i, j])
    
    return [theta, coords, matrix_reference, 1]

theta, coords, matrix_reference, graycode_value = dimension_init()

# Main
# Loop

while True:
    screen.fill((0, 0, 0))

    rotation_matrices = getmatrices()

    for i in range(0, len(theta)):
        if i > m.pi * 2:
            theta[i] += -m.pi * 2
        theta[i] += m.pi / 360
    
    pcoords = []
    for i in range(0, len(coords)):
        pcoords.append(project(coords[i]))

    for i in range(0, len(coords)):
        for j in range(i, len(coords)):
                dif = []
                for k in range(0, len(coords[0])):
                    dif.append(coords[j][k]-coords[i][k])
                if dif.count(0) == len(coords[0])-graycode_value:
                    pygame.draw.line(screen, (255, 255, 255), pcoords[i], pcoords[j], 3)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        dist += -1
    elif keys[pygame.K_s]:
        dist += 1

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                if graycode_value < dimension_number:
                    graycode_value += 1
            if event.key == pygame.K_h:
                if graycode_value > 0:
                    graycode_value -= 1
            if event.key == pygame.K_f:
                if depth:
                    depth = False
                else:
                    depth = True
            if event.key == pygame.K_q:
                stereo_dist += -0.5
            if event.key == pygame.K_e:
                stereo_dist += 0.5
            if event.key == pygame.K_UP:
                dimension_number += 1
                theta, coords, matrix_reference, graycode_value = dimension_init()
            if event.key == pygame.K_DOWN:
                if dimension_number != 0:
                    dimension_number += -1
                    theta, coords, matrix_reference, graycode_value = dimension_init()
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            if event.key == pygame.K_i:
                print(f"\nDEBUG:\n\nAngles: {theta}\n\nMatrices: {rotation_matrices}")

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pygame.display.update()
    clock.tick(60)