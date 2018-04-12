from ldraw.utils import clean
import random

def test_clean():
    assert clean('%unclean') == '_unclean'
    assert clean('Brick 1   x 3') == 'Brick_1x3'
    assert clean('Brick 1x3') == 'Brick_1x3'
    assert clean('Brick 1x   3') == 'Brick_1x_3'

    assert clean('Brick%%%%1') == 'Brick_1'
