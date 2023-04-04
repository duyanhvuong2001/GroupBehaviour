from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform

class Obstacle(object):
    def __init__(self, world=None):
        self.radius = randrange(30,80)
        self.pos = Vector2D(randrange(0,world.cx-self.radius),randrange(0,world.cy-self.radius))
    def render(self):
        egi.white_pen()
        egi.circle(self.pos, self.radius)



