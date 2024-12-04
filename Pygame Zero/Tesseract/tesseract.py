import pgzrun, os
import numpy as np
from math import sin, cos, sqrt, pi

os.environ['SDL_VIDEO_CENTERED'] = '1'
WIDTH, HEIGHT = 1280, 1024

# Rotation settings
axis = (1, 1, 1)
theta = 0

points = [
    [-1, -1, -1],
    [-1, -1, 1],
    [-1, 1, -1],
    [-1, 1, 1],
    [1, -1, -1],
    [1, -1, 1],
    [1, 1, -1],
    [1, 1, 1]
]

'''
000
001
010
011
100
101
110
111
'''


lines = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)]

def rot(pos, axis, theta):
    # normalize
    abs = sqrt(axis[0] ** 2 + axis[1] ** 2 + axis[2] ** 2)
    w = [i / abs for i in axis]
    # trig
    s, c, ic = sin(theta), cos(theta), 1 - cos(theta)
    matrix = [
        [c + w[0] ** 2 * ic, w[0] * w[1] * ic - w[2] * s, w[1] * s + w[0] * w[2] * ic],
        [w[2] * s + w[0] * w[1] * ic, c + w[1] ** 2 * ic, -w[0] * s + w[1] * w[2] * ic],
        [-w[1] * s + w[0] * w[2] * ic, w[0] * s + w[1] * w[2] * ic, c + w[2] ** 2 * ic]
    ]
    result = [matrix[0][0] * pos[0] + matrix[0][1] * pos[1] + matrix[0][2] * pos[2],
              matrix[1][0] * pos[0] + matrix[1][1] * pos[1] + matrix[1][2] * pos[2],
              matrix[2][0] * pos[0] + matrix[2][1] * pos[1] + matrix[2][2] * pos[2]]
    return WIDTH / 2 + result[0] * 100, HEIGHT / 2 + result[1] * 100 # result[2]

def rotate(theta):
    new_points = []
    for point in points:
        rotated = rot(point, axis, theta)
        new_points.append(rotated)
    return new_points

def update():
    pass

def draw():
    screen.clear()
    global theta
    new_points = rotate(theta)
    theta += 2 * pi / 360

    global lines
    for line in lines:
        start = new_points[line[0]]
        end = new_points[line[1]]
        screen.draw.line(start, end, 'white')

pgzrun.go()