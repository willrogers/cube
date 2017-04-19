import numpy
import collections
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
    front = piece
    top = numpy.dot(ROTATE_YZ, piece)
    back = numpy.dot(ROTATE_YZ, numpy.dot(ROTATE_YZ, piece))
    bottom = numpy.dot(ROTATE_YZ,
                       numpy.dot(ROTATE_YZ,
                                 numpy.dot(ROTATE_YZ, piece)))
    left = numpy.dot(ROTATE_XY, piece)
    right = numpy.dot(ROTATE_XY,
                      numpy.dot(ROTATE_XY,
                                numpy.dot(ROTATE_XY, piece)))
    sides = (front, top, back, bottom, left, right)
    all_os = []
    for s in sides:
        all_os.append(s)
        for i in range(3):
            s = numpy.dot(ROTATE_XY, s)
            all_os.append(s)
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
                    log.debug('i, j, k: %s %s %s %s', i, j, k, p)
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
    for i in range(piece.shape[1]):
        if grid[tuple(piece[:, i])] == True:
            raise Exception('piece already here')
    for i in range(piece.shape[1]):
        grid[tuple(piece[:, i])] = True


def remove(piece, grid):
    for i in range(piece.shape[1]):
        if grid[tuple(piece[:, i])] == False:
            raise Exception('piece not already here')
    for i in range(piece.shape[1]):
        grid[tuple(piece[:, i])] = False


def sort_by_grid(locs, grid_size):
    sorted_locs = collections.defaultdict(list)
    for i in range(grid_size):
        for j in range(grid_size):
            for k in range(grid_size):
                for p in locs:
                    for l in locs[p]:
                        for x in range(l.shape[1]):
                            if tuple(l[:, x]) == (i, j, k):
                                sorted_locs[(i, j, k)].append((p, l))
    return sorted_locs


def array_in(array, arrays):
    for a in arrays:
        if numpy.array_equal(array, a):
            return True
    return False


def restart(grid, slocs, used, tried):
    for i in range(4):
        for j in range(4):
            for k in range(4):
                if not grid[i, j, k]:
                    log.debug('looking for %s,%s,%s', i, j, k)
                    for n, o in slocs[(i, j, k)]:
                        if n not in used:
                            if not array_in(o, tried[len(used)]):
                                try:
                                    place(o, grid)
                                    used[n] = o
                                    log.debug('placed: %s', o)
                                    log.debug('placed: grid %s', grid)
                                    break
                                except Exception as e:
                                    log.debug('oops: %s', e)
                                    continue
                if numpy.all(grid):
                    print('done')
                    for u, o in used.iteritems():
                        print(u)
                        print(o)
                    import sys
                    sys.exit()
                if not grid[i, j, k]:
                    log.debug('failed to fill %s,%s,%s', i, j, k)
                    log.debug('stuck on %s', grid)
                    log.debug('used: %s', used.keys())
                    _, last = used.popitem()
                    remove(last, grid)
                    tried[len(used) + 1] = []
                    tried[len(used)].append(last)
                    return


def one_try(grid, slocs):
    used = collections.OrderedDict()
    tried = collections.defaultdict(list)
    x = 0
    while x < 1000000:
        if x % 1000 == 1:
            log.info('iteration %s', x)
            log.info('used: %s', used.keys())
        x = x + 1
        restart(grid, slocs, used, tried)


if __name__ == '__main__':

    locs = {}
    for i, p in enumerate(PIECES):
        alocs = locations(p, 4)
        log.info('%s', len(alocs))
        locs[i] = alocs

    slocs = sort_by_grid(locs, 4)
    for s in sorted(slocs.keys()):
        log.info('%s: %s', s, len(slocs[s]))
    for i, o in slocs[(0, 0, 0)]:
        log.info('%s: %s', i, o)

    grid = numpy.zeros((4, 4, 4), dtype=numpy.bool)
    one_try(grid, slocs)
