import pytest
from mock import patch

import ldraw
from ldraw.parts import Parts, PartError


def test_load_parts():
    p = Parts('tests/test_ldraw/parts.lst')
    assert len(p.parts_by_name) == 1
    assert len(p.parts_by_code) == 1
    assert list(p.parts_by_name.values())[0] == '3001'
    assert list(p.parts_by_name.keys())[0] == 'Brick  2 x  4'
    assert list(p.parts_by_code.keys())[0] == '3001'
    assert list(p.parts_by_code.values())[0] == 'Brick  2 x  4'

    part = p.part(code='3001')

    assert part.path == 'tests/test_ldraw/parts/3001.dat'


def test_load_primitives():
    p = Parts('tests/test_ldraw/parts.lst')
    assert len(p.primitives_by_name) == 4
    assert len(p.primitives_by_code) == 4
    assert 'Box with 5 Faces and All Edges','box5' in p.primitives_by_name.items()
    assert 'box5', 'Box with 5 Faces and All Edges' in p.primitives_by_code.items()

    part = p.part(code='box5')

    assert part.path == 'tests/test_ldraw/p/box5.dat'


def new_try_load(path):
    raise IOError()


@patch.object(ldraw.parts.Parts, 'try_load', side_effect=new_try_load)
def test_cantreadpartslst(mocked):
    pytest.raises(PartError, lambda: Parts('tests/test_ldraw/parts.lst') )