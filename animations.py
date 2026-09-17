"""飞出与抖动动画"""
import math
import pygame

from constants import DIRS, FLY_TIME, SHAKE_TIME, COLOR_ARROW, COLOR_ARROW_EDGE
from ui import arrow_polygon, cell_center


class FlyOut:
    """箭头飞出动画：按时间沿方向位移并逐渐缩小"""

    def __init__(self, arrow, cell, ox, oy):
        self.arrow = arrow
        self.cell = cell
        self.x, self.y = cell_center(cell, ox, oy, arrow.row, arrow.col)
        dr, dc, _ = DIRS[arrow.direction]
        speed = cell * 11
        self.vx = dc * speed
        self.vy = dr * speed
        self.t = 0.0

    @property
    def finished(self):
        return self.t >= FLY_TIME

    @property
    def scale(self):
        p = self.t / FLY_TIME
        if p < 0.35:
            return 1.0
        return max(0.0, 1.0 - (p - 0.35) / 0.65)

    def update(self, dt):
        self.t += dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface):
        s = self.scale
        if s <= 0.02:
            return
        pts = arrow_polygon(self.x, self.y, self.cell, self.arrow.direction, s)
        pygame.draw.polygon(surface, COLOR_ARROW, pts)
        pygame.draw.polygon(surface, COLOR_ARROW_EDGE, pts, width=2)


class ShakeManager:
    """管理每个格子的抖动动画（受击反馈）"""

    def __init__(self, duration=SHAKE_TIME):
        self.duration = duration
        self.shakes = {}       # (row, col) -> 剩余时间

    def add(self, row, col):
        self.shakes[(row, col)] = self.duration

    def get(self, row, col):
        return self.shakes.get((row, col), 0.0)

    def offset(self, row, col, direction):
        """返回该格子当前的抖动偏移量 (dx, dy)"""
        shake = self.get(row, col)
        if shake <= 0:
            return 0.0, 0.0
        progress = 1.0 - shake / self.duration
        amp = 10.0 * math.sin(progress * math.pi * 3) * (1.0 - progress)
        dr, dc, _ = DIRS[direction]
        return -dc * amp, -dr * amp

    def update(self, dt):
        for key in list(self.shakes):
            self.shakes[key] -= dt
            if self.shakes[key] <= 0:
                del self.shakes[key]

    def clear(self):
        self.shakes.clear()