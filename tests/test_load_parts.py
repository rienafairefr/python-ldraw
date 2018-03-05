from ldraw.parts import Parts


def test_load_parts():
    p = Parts('tests/test_ldraw/parts.lst')
    assert len(p.parts_by_description) == 1
    assert list(p.parts_by_description.values())[0] == '3001'
    assert list(p.parts_by_description.keys())[0] == 'Brick  2 x  4'

    part = p.part(code='3001')

    assert part.path == '../parts/3001.dat'
