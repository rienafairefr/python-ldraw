""" Some tools to convert ldr to other formats"""
import argparse

import sys

from ldraw.config import get_config
from ldraw.parts import Part, Parts, PartError
from ldraw.geometry import Vector, CoordinateSystem


def widthxheight(input_str):
    """ a type for a widthxheight image size """
    image_dimensions = input_str.split("x")
    if len(image_dimensions) != 2:
        raise argparse.ArgumentTypeError("Expecting widthxheight")
    return list(map(int, image_dimensions))


def vector_position(input_str):
    """ a type for comma separated vector """
    position = input_str.split(",")
    if len(position) != 3:
        raise argparse.ArgumentTypeError("Expecting comma-separated elements for the position")
    return Vector(*map(float, position))


def get_model(ldraw_path):
    """" get model from ldraw path """
    config = get_config()
    parts = Parts(config['parts.lst'])
    try:
        model = Part(ldraw_path)
    except PartError:
        sys.stderr.write("Failed to read LDraw file: %s\n" % ldraw_path)
        sys.exit(1)
    return model, parts


UP_DIRECTION = Vector(0, -1.0, 0)


def get_coordinate_system(camera_position, look_at_position):
    """" get coordinate system of the view """
    system = CoordinateSystem()
    system.z = (camera_position - look_at_position)
    system.z.norm()
    system.x = UP_DIRECTION.cross(system.z)
    if abs(system.x) == 0.0:
        system.x = system.z.cross(Vector(1.0, 0, 0))
    system.x.norm()
    system.y = system.z.cross(system.x)
    return system


def verify_camera_look_at(camera_position, look_at_position):
    """ verify that the camera and look_at positions are valid """
    if camera_position == look_at_position:
        sys.stderr.write("Camera and look-at positions are the same.\n")
        sys.exit(1)
