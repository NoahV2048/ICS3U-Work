import math as m, pygame
from sys import exit

pygame.init()

# Game setup
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('3D Render')
clock = pygame.time.Clock()

# Math setup

theta_xz, theta_yz, theta_wy = 0, 0, 0
dist, fourD = 500, 300
graycode_value = 1

# Functions setup

def vecmatrix(vector, matrix):
    matrix_product = []
    for index in range(0, len(matrix)):
        row = 0
        for i in range(0, len(matrix[0])):
            row += vector[i]*matrix[index][i]
        matrix_product.append(row)
    return matrix_product

def rotate(vector):
    return vecmatrix(vecmatrix(vector, MXZ), MYZ)

def project(vector):
    depth_factor = dist/(dist+rotate(vector)[2])
    
    return (640+(depth_factor)*(rotate(vector)[0]),
            360+(depth_factor)*(rotate(vector)[1]))

coords = [[100, 100, 100, 100],
          [100, 100, 100, -100],
          [100, 100, -100, 100],
          [100, 100, -100, -100],
          [100, -100, 100, 100],
          [100, -100, 100, -100],
          [100, -100, -100, 100],
          [100, -100, -100, -100],
          [-100, 100, 100, 100],
          [-100, 100, 100, -100],
          [-100, 100, -100, 100],
          [-100, 100, -100, -100],
          [-100, -100, 100, 100],
          [-100, -100, 100, -100],
          [-100, -100, -100, 100],
          [-100, -100, -100, -100]]

while True:
    screen.fill((0, 0, 0))

    MXZ = [[m.cos(theta_xz), 0, m.sin(theta_xz), 0],
        [0, 1, 0, 0],
        [-m.sin(theta_xz), 0, m.cos(theta_xz), 0],
        [0, 0, 0, 1]]

    MYZ = [[1, 0, 0, 0],
        [0, m.cos(theta_yz), -m.sin(theta_yz), 0],
        [0, m.sin(theta_yz), m.cos(theta_yz), 0],
        [0, 0, 0, 1]]
    
    MWY = [[1, 0, 0, 0],
        [0, m.cos(theta_wy), 0, m.sin(theta_wy)],
        [0, 0, 1, 0],
        [0, -m.sin(theta_wy), 0, m.cos(theta_wy)]]

    theta_xz += m.pi/360
    theta_yz = m.pi/6
    theta_wy += m.pi/360
    pcoords = []

    for index in range(0, len(coords)):
        pcoords.append(project(coords[index]))

    for index in range(0, len(coords)):
        for entry in range(0, len(coords)):
                dif = []
                for num in range(0, len(coords[0])):
                    dif.append(coords[entry][num]-coords[index][num])
                if dif.count(0) == len(coords[0])-graycode_value:
                    pygame.draw.line(screen, (255, 255, 255), pcoords[index], pcoords[entry], 3)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pygame.display.update()
    clock.tick(60)