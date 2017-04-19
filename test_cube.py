import numpy
import cube


TWO = numpy.array([[0, 0, 0], [0, 0, 1]]).T


def test_unique():
    pass


def test_locations():
    locations = cube.locations(TWO, 2)
    assert len(locations) == 12
    locations = cube.locations(cube.R_CROSS, 4)
    assert len(locations) == 48


def test_orientations():
    orientations = cube.orientations(TWO)
    assert len(orientations)
    numpy.testing.assert_equal(orientations[0],
                               numpy.array([[0, 0, 0], [0, 0, 1]]).T)
    numpy.testing.assert_equal(orientations[1],
                               numpy.array([[0, 0, 0], [0, 1, 0]]).T)
    numpy.testing.assert_equal(orientations[2],
                               numpy.array([[0, 0, 0], [1, 0, 0]]).T)
