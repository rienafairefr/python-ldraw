import argparse

from ldraw.geometry import Vector


def widthxheight(input_str):
    """ a type for a widthxheight image size """
    image_dimensions = input_str.split("x")
    if len(image_dimensions) != 2:
        raise argparse.ArgumentTypeError("Expecting widthxheight")
    return list(map(int, image_dimensions))


def vector_position(input_str):
    position = input_str.split(",")
    if len(position) != 3:
        raise argparse.ArgumentTypeError("Expecting comma-separated elements for the position")
    return Vector(*map(float, position))
