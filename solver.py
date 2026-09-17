"""关卡可解性验证：贪心求解器"""


def solve(board):
    """不断移除当前无阻挡的箭头，若能清空则返回移除顺序，否则返回 None。
    移除只会让其他箭头更自由，所以贪心策略是安全的。"""
    work = board.clone()
    order = []
    guard = 0
    while guard < 10000:
        guard += 1
        free = [a for a in work.arrows if not work.is_blocked(a)]
        if not free:
            break
        for a in free:
            work.remove(a)
            order.append((a.row, a.col, a.direction))
    return order if work.remaining == 0 else None