"""棋盘与路径检测"""
from arrow import Arrow
from constants import DIRS


class Board:
    """棋盘：用二维列表存储箭头，空格为 None"""

    def __init__(self, rows, cols, arrows=None):
        self.rows = rows
        self.cols = cols
        self.grid = [[None] * cols for _ in range(rows)]
        if arrows:
            for a in arrows:
                self.grid[a.row][a.col] = a

    @property
    def arrows(self):
        return [a for row in self.grid for a in row if a is not None]

    @property
    def remaining(self):
        return sum(1 for row in self.grid for a in row if a is not None)

    def arrow_at(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def is_blocked(self, arrow):
        """沿箭头方向逐格扫描，遇到其他箭头即被阻挡"""
        dr, dc, _ = DIRS[arrow.direction]
        r = arrow.row + dr
        c = arrow.col + dc
        while 0 <= r < self.rows and 0 <= c < self.cols:
            if self.grid[r][c] is not None:
                return True
            r += dr
            c += dc
        return False

    def remove(self, arrow):
        if self.arrow_at(arrow.row, arrow.col) is arrow:
            self.grid[arrow.row][arrow.col] = None
            return True
        return False

    def clone(self):
        return Board(self.rows, self.cols,
                     [Arrow(a.row, a.col, a.direction) for a in self.arrows])