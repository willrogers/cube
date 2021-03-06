import numpy
import collections
import hashlib
import itertools
import logging as log
LOG_FORMAT = '%(levelname)s: %(message)s'
log.basicConfig(format=LOG_FORMAT, level=log.INFO)


# Define the pieces
Y_FOUR = numpy.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [1, 1, 1]]).T
Y_W = numpy.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0], [2, 2, 0]]).T
Y_SQUIG = numpy.array([[0, 0, 0], [0, 0, 1], [1, 0, 0], [2, 0, 0], [2, 1, 0]]).T
Y_L = numpy.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 1], [0, 1, 2]]).T
Y_T = numpy.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [1, 0, 1], [2, 0, 0]]).T

R_CROSS = numpy.array([[0, 1, 0], [1, 1, 0], [1, 0, 0], [2, 1, 0], [1, 2, 0]]).T
R_SQUIG = numpy.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0], [2, 1, 1]]).T
R_LS = numpy.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 2]]).T
R_Y = numpy.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [1, 1, 1], [2, 1, 0]]).T

B_T = numpy.array([[0, 0, 0], [1, 0, 0], [1, 0, 1], [2, 0, 0], [2, 1, 0]]).T
B_SQUIG = numpy.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [1, 1, 1], [2, 1, 1]]).T
B_T2 = numpy.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 0, 1], [1, 1, 1]]).T
B_L = numpy.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0], [1, 2, 0]]).T

PIECES = [Y_FOUR, Y_W, Y_SQUIG, Y_L, Y_T, R_CROSS, R_SQUIG, R_LS, R_Y, B_T,
          B_SQUIG, B_T2, B_L]


# Transformations
ROTATE_XY = numpy.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
ROTATE_XZ = numpy.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])
ROTATE_YZ = numpy.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])

TRANS_X = numpy.array([1, 0, 0]).reshape(3, 1)
TRANS_Y = numpy.array([0, 1, 0]).reshape(3, 1)
TRANS_Z = numpy.array([0, 0, 1]).reshape(3, 1)


def orientations(piece):
    # First get all six orientations as on a die.
    front = piece
    top = numpy.dot(ROTATE_YZ, piece)
    back = numpy.dot(ROTATE_YZ, numpy.dot(ROTATE_YZ, piece))
    # Inverse of rotation is transpose of the matrix.
    bottom = numpy.dot(ROTATE_YZ.T, piece)
    left = numpy.dot(ROTATE_XY, piece)
    right = numpy.dot(ROTATE_XY.T, piece)
    sides = (front, top, back, bottom, left, right)
    # For each side of the die, there four rotations.
    all_os = []
    for s in sides:
        all_os.append(s)
        for i in range(3):
            s = numpy.dot(ROTATE_XY, s)
            all_os.append(s)
    # Remove any duplicate orientations.
    unique_os = []
    for a in all_os:
        matched = False
        while numpy.any(a[0, :] < 0):
            a = a + TRANS_X
        while numpy.any(a[1, :] < 0):
            a = a + TRANS_Y
        while numpy.any(a[2, :] < 0):
            a = a + TRANS_Z
        a = a.T[numpy.lexsort(numpy.fliplr(a.T).T)]
        a = a.T

        for u in unique_os:
            if numpy.array_equal(a, u):
                matched = True
                break
        if not matched:
            unique_os.append(a)
    return unique_os


def locations(piece, grid_size):
    os = orientations(piece)
    locs = []
    for o in os:
        for i in range(grid_size):
            for j in range(grid_size):
                for k in range(grid_size):
                    p = o + i * TRANS_X + j * TRANS_Y + k * TRANS_Z
                    #log.debug('i, j, k: %s %s %s %s', i, j, k, p)
                    if numpy.all(p < grid_size):
                        locs.append(p)
    unique_os = []
    for a in locs:
        matched = False
        for u in unique_os:
            if numpy.array_equal(a, u):
                matched = True
                break
        if not matched:
            unique_os.append(a)
    return unique_os


def place(piece, grid):
    for s in piece:
        if grid[tuple(s)]:
            return False
    for s in piece:
        grid[tuple(s)] = True
    return True


def remove(piece, grid):
    for s in piece:
        if not grid[tuple(s)]:
            return False
    for s in piece:
        grid[tuple(s)] = False
    return True


def sort_by_grid(locs, grid_size):
    sorted_locs = collections.defaultdict(list)
    r = range(grid_size)
    for index in itertools.product(r, r, r):
        for piece in locs:
            for loc in locs[piece]:
                for x in range(loc.shape[1]):
                    if tuple(loc[:, x]) == index:
                        # Transpose locations for later use.
                        # Hash once per array to save doing it more often later.
                        sorted_locs[index].append((piece, loc.T, hsh(loc.T)))
                        continue
    return sorted_locs


def hsh(array):
    return hash(array.tostring())


def next_try(grid, slocs, used, tried):
    r = range(grid.shape[0])
    for index in itertools.product(r, r, r):
        if not grid[index]:
            #log.debug('looking for %s,%s,%s', i, j, k)
            for n, o, h in slocs[index]:
                if n not in used:
                    if not h in tried[len(used)]:
                        if place(o, grid):
                            used[n] = o
                            #log.debug('placed: %s', o)
                            #log.debug('placed: grid %s', grid)
                            break
                        else:
                            #log.debug('oops: %s', e)
                            continue
        if not grid[index]:
            #log.debug('failed to fill %s,%s,%s', i, j, k)
            #log.debug('stuck on %s', grid)
            #log.debug('used: %s', used.keys())
            _, last = used.popitem()
            remove(last, grid)
            tried[len(used) + 1] = []
            tried[len(used)].append(hsh(last))
            return False
    # If all squares are filled, we're done.
    return True


import cubex


if __name__ == '__main__':

    locs = {}
    for i, p in enumerate(cubex.PIECES):
        alocs = cubex.locations(p, 4)
        log.info('Piece %d has %s locations', i, len(alocs))
        locs[i] = alocs

    sorted_locs = cubex.sort_by_grid(locs, 4)
    for s in sorted(sorted_locs.keys()):
        log.info('Square %s: %s possible pieces', s, len(sorted_locs[s]))

    grid = numpy.zeros((4, 4, 4), dtype=numpy.bool)
    cubex.start(grid, locs, sorted_locs)
