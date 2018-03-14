import math
import pytest
import random

from ldraw.geometry import Identity, Vector, MatrixError, Matrix, XAxis, YAxis, ZAxis


def test_matrix_rmul():
    m = Identity().scale(1, 2, 3)
    v = Vector(3, 2, 1)

    mul = m * v
    assert mul == Vector(3, 4, 3)


def test_mulothers():
    m = Identity()
    pytest.raises(MatrixError, lambda: m * 2)
    pytest.raises(MatrixError, lambda: 2 * m)


random.seed(12345)


def row():
    return [random.random() for i in range(3)]


@pytest.fixture
def random_matrix():
    yield Matrix(rows=[row(), row(), row()])


def test_copy(random_matrix):
    assert random_matrix.copy() == random_matrix


@pytest.mark.parametrize('axis', [XAxis, YAxis, ZAxis])
def test_rotate_radians(random_matrix, axis):
    original = random_matrix.copy()
    random_matrix.rotate(45, axis=axis)

    random_matrix.rotate(3*math.pi, axis= axis)
    assert original == random_matrix


def test_rotate_wrong_axis(random_matrix):
    pytest.raises(MatrixError, lambda: random_matrix.rotate(444, axis=None))
