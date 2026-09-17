"""箭头数据模型"""


class Arrow:
    __slots__ = ('row', 'col', 'direction')

    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction

    def __repr__(self):
        return f'Arrow({self.row},{self.col},{self.direction})'