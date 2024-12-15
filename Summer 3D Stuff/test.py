vector = [0, 1, 2, 3, 4]

x, y, z, w = vector
if (-w <= x <= w) and (-w <= y <= w) and (0 <= z <= w) and (w != 0):
    print(x, y, z, w)