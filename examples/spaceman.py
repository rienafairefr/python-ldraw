from __future__ import print_function
import random

from ldraw.geometry import Identity, XAxis, YAxis, ZAxis, Vector
from ldraw.figure import Person

from ldraw.library.colours import Yellow, Light_Green, Blue, Red, Green
from ldraw.library.parts.minifig.torsos import TorsoWithClassicSpacePattern


random.seed(12345)

for x in range(-100, 200, 100):
    for z in range(-100, 200, 100):
        orientation = Identity()
        orientation = orientation.rotate(random.randrange(0, 360), XAxis)
        orientation = orientation.rotate(random.randrange(0, 360), YAxis)
        orientation = orientation.rotate(random.randrange(0, 360), ZAxis)
        figure = Person(Vector(x, 0, z), orientation)
        print(figure.head(Yellow))
        print(figure.torso(Light_Green, TorsoWithClassicSpacePattern))
        print(figure.hips(Blue))
        angle = random.randrange(-90, 60)
        print(figure.left_leg(Red, angle))
        angle = random.randrange(-90, 60)
        print(figure.right_leg(Green, angle))
        angle = random.randrange(-120, 60)
        print(figure.left_arm(Red, angle))
        angle = random.randrange(-90, 90)
        print(figure.left_hand(Yellow, angle))
        angle = random.randrange(-120, 60)
        print(figure.right_arm(Green, angle))
        angle = random.randrange(-90, 90)
        print(figure.right_hand(Yellow, angle))
