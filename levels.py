"""关卡数据与解析"""
from arrow import Arrow
from board import Board
from constants import CHAR_TO_DIR

# 用紧凑字符画描述关卡：^ v < > 表示方向，. 表示空格
# 注意：不要用空格排版，否则会被算成额外的列！
# 箭头数量：第1关5个，第2关8个，第3关12个，第4关16个，第5关20个
RAW_LEVELS = [
    # 第 1 关：5 个箭头（4×4）
    [
        ">..v",
        ".v..",
        "....",
        "<..>",
    ],
    # 第 2 关：8 个箭头（5×5）
    [
        ">...v",
        ".^...",
        "<.v..",
        "...<.",
        ">...>",
    ],
    # 第 3 关：12 个箭头（6×6）
    [
        ">....^",
        ".^...v",
        "..v..v",
        "<..>..",
        ".>..>.",
        ">....v",
    ],
    # 第 4 关：16 个箭头（6×6）
    [
        ">....^",
        ".^..^.",
        "..v.<v",
        "<.v>..",
        ".>.v^.",
        ">.v..v",
    ],
    # 第 5 关：20 个箭头（6×6）
    [
        ">....^",
        ".^.<.<",
        ".<v.<v",
        "<.v>..",
        ".<.v^<",
        ">.v.^v",
    ],
]


def parse_level(rows):
    """把字符画解析成 Board

    - 方向字符 ^ v < > 表示箭头；
    - '.' 表示空格；
    - 不要用空格排版，否则列数会被算多。
    """
    n_rows = len(rows)
    n_cols = max(len(r) for r in rows)
    arrows = []
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch in CHAR_TO_DIR:
                arrows.append(Arrow(r, c, CHAR_TO_DIR[ch]))
            elif ch == '.':
                continue
            else:
                raise ValueError(
                    '非法关卡字符: %r （行 %d, 列 %d）' % (ch, r, c))
    return Board(n_rows, n_cols, arrows)


def load_all_levels():
    """解析全部关卡，返回 Board 列表"""
    return [parse_level(lv) for lv in RAW_LEVELS]
