"""全局常量与配置"""

# 窗口与棋盘尺寸
WINDOW_W, WINDOW_H = 960, 720
BOARD_AREA = 480
BOARD_LEFT = (WINDOW_W - BOARD_AREA) // 2
BOARD_TOP = 110

# 游戏规则参数
MAX_MISTAKES = 5
FPS = 60
FLY_TIME = 0.55          # 飞出动画时长（秒）
SHAKE_TIME = 0.45        # 抖动动画时长（秒）

# 颜色
COLOR_BG          = (247, 249, 252)
COLOR_PANEL       = (238, 242, 248)
COLOR_PANEL_EDGE  = (219, 227, 240)
COLOR_ARROW       = (58, 92, 168)
COLOR_ARROW_EDGE  = (40, 64, 120)
COLOR_BLOCK       = (214, 69, 69)
COLOR_BLOCK_EDGE  = (168, 46, 46)
COLOR_TEXT        = (38, 48, 62)
COLOR_MUTED       = (140, 150, 168)
COLOR_BTN         = (58, 92, 168)
COLOR_BTN_HOVER   = (86, 132, 224)
COLOR_BTN_SHADOW  = (40, 64, 120)
COLOR_WIN         = (46, 160, 96)
COLOR_LOSE        = (214, 69, 69)
COLOR_CARD        = (255, 255, 255)
COLOR_HINT        = (150, 185, 245)

# 方向 -> (行增量, 列增量, 旋转角度)
DIRS = {
    'up':    (-1, 0, 270),
    'down':  (1, 0, 90),
    'left':  (0, -1, 180),
    'right': (0, 1, 0),
}
CHAR_TO_DIR = {'^': 'up', 'v': 'down', '<': 'left', '>': 'right'}

# 指向 +x 方向的基础三角形（局部坐标）
BASE_TRI = [(1.0, 0.0), (-0.72, -0.78), (-0.72, 0.78)]