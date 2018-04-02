import math
import pytest
import random

from ldraw.geometry import Identity, Vector, MatrixError, Matrix, XAxis, YAxis, ZAxis, _rows_multiplication, Radians


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
    return Matrix(rows=[row(), row(), row()])


def test_copy(random_matrix):
    assert random_matrix.copy() == random_matrix


@pytest.mark.parametrize('axis', [XAxis, YAxis, ZAxis])
def test_rotate_radians(random_matrix, axis):
    original = random_matrix.copy()
    rotated = original.rotate(90, axis=axis)

    rotated = rotated.rotate(3 * math.pi / 2, axis=axis, units=Radians)
    assert str(original) == str(rotated)


def test_rotate_wrong_axis(random_matrix):
    pytest.raises(MatrixError, lambda: random_matrix.rotate(444, axis=None))


def test_mul_matrix():
    m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    m2 = Matrix([[10, 11, 12], [13, 14, 15], [16, 17, 18]])
    m12 = m1 * m2
    assert m12.rows == [[84, 90, 96], [201, 216, 231], [318, 342, 366]]


def test_mul_matrix_vector():
    m = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    v = Vector(42, 1, 0)
    v2 = m * v
    assert v2 == Vector(44, 173, 302)