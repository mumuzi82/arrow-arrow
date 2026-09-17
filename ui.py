"""渲染工具函数"""
import math
import pygame

from constants import (
    BOARD_AREA, BOARD_LEFT, BOARD_TOP, BASE_TRI, DIRS,
    COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_SHADOW,
)


# ---------- 几何工具 ----------

def rotate_point(x, y, deg):
    rad = math.radians(deg)
    c, s = math.cos(rad), math.sin(rad)
    return x * c - y * s, x * s + y * c


def arrow_polygon(cx, cy, cell, direction, scale=1.0):
    """生成箭头三角形的三个顶点"""
    angle = DIRS[direction][2]
    r = cell * 0.34 * scale
    pts = []
    for bx, by in BASE_TRI:
        x, y = rotate_point(bx * r, by * r, angle)
        pts.append((cx + x, cy + y))
    return pts


def board_metrics(board):
    cell = BOARD_AREA // max(board.rows, board.cols)
    w = cell * board.cols
    h = cell * board.rows
    ox = (BOARD_AREA - w) // 2
    oy = (BOARD_AREA - h) // 2
    return cell, ox, oy


def cell_center(cell, ox, oy, row, col):
    return (BOARD_LEFT + ox + col * cell + cell / 2,
            BOARD_TOP + oy + row * cell + cell / 2)


def cell_rect(cell, ox, oy, row, col):
    return pygame.Rect(BOARD_LEFT + ox + col * cell,
                       BOARD_TOP + oy + row * cell,
                       cell, cell)


def pixel_to_cell(board, px, py):
    """像素坐标 → (row, col)；若在棋盘外返回 None"""
    cell, ox, oy = board_metrics(board)
    x0 = BOARD_LEFT + ox
    y0 = BOARD_TOP + oy
    if px < x0 or px >= x0 + cell * board.cols:
        return None
    if py < y0 or py >= y0 + cell * board.rows:
        return None
    return int((py - y0) // cell), int((px - x0) // cell)


# ---------- 字体与按钮 ----------

def make_font(size, bold=False):
    """优先匹配系统中文字体，找不到则退回默认字体"""
    candidates = ['microsoftyahei', 'msyh', 'simhei', 'simsun',
                  'pingfangsc', 'hiraginosansgb', 'notosanscjksc',
                  'wenquanyimicrohei', 'arialunicode']
    available = set(pygame.font.get_fonts())
    for name in candidates:
        if name in available:
            path = pygame.font.match_font(name)
            if path:
                f = pygame.font.Font(path, size)
                f.set_bold(bold)
                return f
    f = pygame.font.Font(None, size)
    f.set_bold(bold)
    return f


def draw_button(screen, rect, text, font, mouse_pos):
    """绘制带阴影和悬停效果的按钮"""
    hover = rect.collidepoint(mouse_pos)
    color = COLOR_BTN_HOVER if hover else COLOR_BTN
    shadow_rect = rect.move(0, 4)
    pygame.draw.rect(screen, COLOR_BTN_SHADOW, shadow_rect, border_radius=16)
    pygame.draw.rect(screen, color, rect, border_radius=16)
    t = font.render(text, True, (255, 255, 255))
    screen.blit(t, t.get_rect(center=rect.center))