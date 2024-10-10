"""
Contains all components that can be used to build your entities (follows the ECS pattern)
"""
from . import glvars
from .glvars import pyv, ecs


class Speed:
    def __init__(self, vx=0.0, vy=0.0):
        self.vx = vx
        self.vy = vy


class Controls:
    def __init__(self):
        self.right = self.left = False


class BlockSig:
    free_b_id = 0

    def __init__(self):
        self.bid = self.__class__.free_b_id
        self.__class__.free_b_id += 1


class Body:
    def __init__(self, x, y, w, h):
        self._x, self._y, self.w, self.h = x, y, w, h
        self._cached_rect = pyv.new_rect_obj(self.x, self.y, self.w, self.h)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = val
        self._cached_rect = pyv.new_rect_obj(self._x, self._y, self.w, self.h)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self._x = val
        self._cached_rect = pyv.new_rect_obj(self._x, self._y, self.w, self.h)

    def to_rect(self):
        return self._cached_rect

    def commit(self):
        # use the cached rect (has been modified) to update other values
        self._x, self.y = self._cached_rect.topleft
