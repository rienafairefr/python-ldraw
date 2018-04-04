from ldraw.colour import Colour

def test_colour_equality():

    c1 = Colour(code=12)
    c2 = Colour(code=12)

    assert c1 == c2
    assert c1 == 12
    assert c2 == 12
    assert 12 == c1
    assert 12 == c2


def test_colour_hash():
    c1 = Colour(code=12)
    c2 = Colour(code=12)

    assert len({c1,c2}) == 1