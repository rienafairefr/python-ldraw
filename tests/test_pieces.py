from ldraw.geometry import Vector, Identity
from ldraw.library.colours import White
from ldraw.library.parts.others import Brick1X1
from ldraw.pieces import Piece, Group


def test_add_piece():
    group1 = Group()
    group2 = Group()
    piece = Piece(White, Vector(0,0,0), Identity(), Brick1X1, group=group1)

    assert piece in group1.pieces
    assert piece not in group2.pieces

    group2.add_piece(piece)

    assert piece in group2.pieces
    assert piece not in group1.pieces