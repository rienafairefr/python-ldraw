from tests.utils import with_mocked_parts_lst


@with_mocked_parts_lst
def test_dynamic_colours_parts_1():
    import ldraw
    from ldraw.library.colours import Black
    from ldraw.library.parts.others import Brick1X1


@with_mocked_parts_lst
def test_dynamic_colours_parts_2():
    import ldraw.library
    from ldraw.library.colours import Black
    from ldraw.library.parts.others import Brick1X1


@with_mocked_parts_lst
def test_dynamic_colours_parts_3():
    from ldraw import library
    from ldraw.library.colours import Black
    from ldraw.library.parts.others import Brick1X1