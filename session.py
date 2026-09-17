"""游戏会话状态机"""

# 游戏状态
STATE_MENU      = 'menu'
STATE_PLAYING   = 'playing'
STATE_CLEAR     = 'clear'
STATE_OVER      = 'over'
STATE_ALL_CLEAR = 'all_clear'


class GameSession:
    def __init__(self, levels, max_mistakes=5):
        self.levels = levels
        self.max_mistakes = max_mistakes
        self.state = STATE_MENU
        self.level_index = 0
        self.mistakes_used = 0
        self.board = levels[0].clone()

    @property
    def mistakes_left(self):
        return self.max_mistakes - self.mistakes_used

    @property
    def level_no(self):
        return self.level_index + 1

    @property
    def total_levels(self):
        return len(self.levels)

    def start(self):
        self.load_level(0)
        self.state = STATE_PLAYING

    def load_level(self, index):
        self.level_index = index
        self.board = self.levels[index].clone()
        self.mistakes_used = 0

    def restart(self):
        self.load_level(self.level_index)
        self.state = STATE_PLAYING

    def next_level(self):
        if self.level_index + 1 >= len(self.levels):
            self.state = STATE_ALL_CLEAR
            return False
        self.load_level(self.level_index + 1)
        self.state = STATE_PLAYING
        return True

    def click_cell(self, row, col):
        """返回 'ignored' / 'blocked' / 'over' / 'flew'"""
        if self.state != STATE_PLAYING:
            return 'ignored'
        arrow = self.board.arrow_at(row, col)
        if arrow is None:
            return 'ignored'
        if self.board.is_blocked(arrow):
            self.mistakes_used += 1
            if self.mistakes_left <= 0:
                self.state = STATE_OVER
                return 'over'
            return 'blocked'
        self.board.remove(arrow)
        return 'flew'

    def finish_level(self):
        """箭头飞出动画播完后调用；棋盘清空则切换状态"""
        if self.state != STATE_PLAYING:
            return False
        if self.board.remaining > 0:
            return False
        if self.level_index + 1 >= len(self.levels):
            self.state = STATE_ALL_CLEAR
        else:
            self.state = STATE_CLEAR
        return True