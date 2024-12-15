def linear_x(vector_in, vector_out, minclip, maxclip):
    x, y, z, w = vector_in
    X, Y, Z, W = vector_out
    if X > maxclip:
        clip = maxclip
    elif minclip > X:
        clip = minclip
    else:
        return vector_out
    t = (clip - x) / (X - x)
    return [clip,
            y + (Y - y) * t,
            z + (Z - z) * t,
            w + (W - w) * t]

def linear_y(vector_in, vector_out, minclip, maxclip):
    x, y, z, w = vector_in
    X, Y, Z, W = vector_out
    minclip, maxclip
    if Y > maxclip:
        clip = maxclip
    elif minclip > Y:
        clip = minclip
    else:
        return vector_out
    t = (clip - y) / (Y - y)
    return [x + (X - x) * t,
            clip,
            z + (Z - z) * t,
            w + (W - w) * t]

def linear_z(vector_in, vector_out, minclip, maxclip):
    x, y, z, w = vector_in
    X, Y, Z, W = vector_out
    minclip, maxclip
    if Z > maxclip:
        clip = maxclip
    elif minclip > Z:
        clip = minclip
    else:
        return vector_out
    t = (clip - z) / (Z - z)
    return [x + (X - x) * t,
            y + (Y - y) * t,
            clip,
            w + (W - w) * t]

print(linear_z([0, 0, 0, 0], [1, 1, -1, 1], -1, 0))
print(linear_z([0, 0, 0, 0], linear_y([0, 0, 0, 0], linear_x([0, 0, 0, 0], [4, 5, -2, -1], -1, 1), -1, 1), -1, 0))