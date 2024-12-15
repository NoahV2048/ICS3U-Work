import numpy as np, math as m, random

player_coords = [0, 0, 0]
width, height, near, far, fov = 1920, 1080, 1, 0, m.pi / 2

point = [1, 16/9, -234]

projection_matrix = np.array([
    [1 / m.tan(fov / 2), 0, 0, 0],
    [0, (height / width) / m.tan(fov / 2), 0, 0],
    [0, 0, -1, -2 * near],
    [0, 0, -1, 0]
])

translation_matrix = np.array([
        [1, 0, 0, -player_coords[0]],
        [0, 1, 0, -player_coords[1]],
        [0, 0, 1, -player_coords[2]],
        [0, 0, 0, 1]
    ])

PV_matrix = projection_matrix @ translation_matrix

def project(cartesian):
    cartesian.append(1)
    homogeneous = cartesian
    homogeneous = projection_matrix @ translation_matrix @ homogeneous
    w = homogeneous[3]
    print(f"The homogeneous coordinates are: {homogeneous}")
    if -w <= homogeneous[0] <= w and -w <= homogeneous[1] <= w and 0 < homogeneous[2] <= w:
        return np.delete(homogeneous, [2, 3]) / homogeneous[3]
    else:
        return 0

print(f"{point} maps to {project(point)}")