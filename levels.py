"""关卡数据与解析"""
from arrow import Arrow
from board import Board
from constants import CHAR_TO_DIR

# 用字符画描述关卡：^ v < > 表示方向，. 表示空格
RAW_LEVELS = [
    [
        ".....",
        ">>>..",
        "^....",
        "....v",
        "..<<<",
    ],
    [
        "..^..",
        "..^..",
        ">>...",
        "...<<",
        "..v..",
    ],
    [
        "......",
        ".>>>..",
        ".^....",
        ".^..v.",
        "...<<<",
    ],
    [
        "..^...",
        "..^...",
        "......",
        ">>...v",
        ".....v",
        "..<<<.",
    ],
]


def parse_level(rows):
    """把字符画解析成 Board"""
    n_rows = len(rows)
    n_cols = max(len(r) for r in rows)
    arrows = []
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch in CHAR_TO_DIR:
                arrows.append(Arrow(r, c, CHAR_TO_DIR[ch]))
            elif ch != '.':
                raise ValueError('非法关卡字符: %r' % ch)
    return Board(n_rows, n_cols, arrows)


def load_all_levels():
    """解析全部关卡，返回 Board 列表"""
    return [parse_level(lv) for lv in RAW_LEVELS]