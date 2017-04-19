import numpy
import cube


ONE = numpy.array([[0, 0, 0]]).T
TWO = numpy.array([[0, 0, 0], [0, 0, 1]]).T


def test_unique():
    pass


def test_locations():
    locations = cube.locations(TWO, 2)
    assert len(locations) == 12
    locations = cube.locations(cube.R_CROSS, 4)
    assert len(locations) == 48


def test_orientations_for_1x1_cube():
    orientations = cube.orientations(ONE)
    assert len(orientations) == 1
    numpy.testing.assert_equal(orientations[0], ONE)


def test_orientations_for_2x1():
    orientations = cube.orientations(TWO)
    assert len(orientations) == 3
    numpy.testing.assert_equal(orientations[0],
                               numpy.array([[0, 0, 0], [0, 0, 1]]).T)
    numpy.testing.assert_equal(orientations[1],
                               numpy.array([[0, 0, 0], [0, 1, 0]]).T)
    numpy.testing.assert_equal(orientations[2],
                               numpy.array([[0, 0, 0], [1, 0, 0]]).T)


def test_orientations_for_R_CROSS():
    orientations = cube.orientations(cube.R_CROSS)
    assert len(orientations) == 3
