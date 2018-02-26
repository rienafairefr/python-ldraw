from ldraw.parts import Parts, Part


def test_load_parts():
    p = Parts('tests/test_ldraw/parts.lst')
    assert len(p.parts) == 1
    assert list(p.parts.values())[0] == '3001'
    assert list(p.parts.keys())[0] == 'Brick  2 x  4'

    part = p.part(code='3001')

    assert part.path == 'tests/test_ldraw/parts/3001.dat'

