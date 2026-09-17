"""主游戏类：事件循环、状态管理、渲染调度"""
import sys
import pygame

from constants import (
    WINDOW_W, WINDOW_H, BOARD_TOP, BOARD_AREA, MAX_MISTAKES, FPS,
    COLOR_BG, COLOR_TEXT, COLOR_MUTED, COLOR_PANEL, COLOR_PANEL_EDGE,
    COLOR_HINT, COLOR_ARROW, COLOR_ARROW_EDGE, COLOR_BLOCK,
    COLOR_BLOCK_EDGE, COLOR_WIN, COLOR_LOSE, COLOR_CARD,
)
from levels import load_all_levels
from session import (
    GameSession, STATE_MENU, STATE_PLAYING, STATE_CLEAR,
    STATE_OVER, STATE_ALL_CLEAR,
)
from solver import solve
from animations import FlyOut, ShakeManager
from ui import (
    board_metrics, cell_center, cell_rect, pixel_to_cell,
    arrow_polygon, make_font, draw_button,
)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("一箭又一箭")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()
        self.running = True

        # 字体
        self.font_huge  = make_font(60, True)
        self.font_big   = make_font(44, True)
        self.font_mid   = make_font(24, True)
        self.font_norm  = make_font(18)
        self.font_small = make_font(16)

        # 关卡加载 + 可解性校验
        self.levels = load_all_levels()
        for i, b in enumerate(self.levels):
            if solve(b) is None:
                print("警告：第 %d 关无解，请检查布局" % (i + 1))

        self.session = GameSession(self.levels, MAX_MISTAKES)

        # 动画状态
        self.fly_outs = []
        self.shakes = ShakeManager()
        self.hint_text = ''
        self.hint_timer = 0.0
        self.hover_cell = None
        self.mouse_pos = (0, 0)

        # 按钮
        self.btn_start = pygame.Rect(0, 0, 280, 76)
        self.btn_start.center = (WINDOW_W // 2, 540)

        self.btn_restart = pygame.Rect(0, 0, 200, 56)
        self.btn_restart.center = (WINDOW_W // 2, WINDOW_H - 46)

        self.btn_overlay = pygame.Rect(0, 0, 260, 70)
        self.btn_overlay.center = (WINDOW_W // 2, 410)

    # ---------- 主循环 ----------
    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit(0)

    # ---------- 事件 ----------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            if self.session.state == STATE_PLAYING:
                self.hover_cell = pixel_to_cell(self.session.board, *event.pos)
            else:
                self.hover_cell = None
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self._on_key(event)

    def _on_key(self, event):
        st = self.session.state
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_r:
            if st == STATE_PLAYING:
                self.restart_level()
        elif event.key == pygame.K_SPACE:
            if st == STATE_MENU:
                self.session.start()
                self._reset_anims()
            elif st == STATE_CLEAR:
                self.session.next_level()
                self._reset_anims()
            elif st == STATE_OVER:
                self.restart_level()
            elif st == STATE_ALL_CLEAR:
                self.session.state = STATE_MENU
                self.session.load_level(0)
                self._reset_anims()

    def _on_click(self, pos):
        st = self.session.state
        if st == STATE_MENU:
            if self.btn_start.collidepoint(pos):
                self.session.start()
                self._reset_anims()
        elif st == STATE_PLAYING:
            if self.btn_restart.collidepoint(pos):
                self.restart_level()
                return
            cell = pixel_to_cell(self.session.board, *pos)
            if cell:
                self._click_cell(*cell)
        else:  # CLEAR / OVER / ALL_CLEAR
            if self.btn_overlay.collidepoint(pos):
                if st == STATE_CLEAR:
                    self.session.next_level()
                elif st == STATE_OVER:
                    self.restart_level()
                    return
                else:  # ALL_CLEAR
                    self.session.state = STATE_MENU
                    self.session.load_level(0)
                self._reset_anims()

    # ---------- 业务操作 ----------
    def restart_level(self):
        self.session.restart()
        self._reset_anims()

    def _reset_anims(self):
        self.fly_outs.clear()
        self.shakes.clear()
        self.hint_text = ''
        self.hint_timer = 0.0
        self.hover_cell = None

    def _click_cell(self, row, col):
        board = self.session.board
        arrow = board.arrow_at(row, col)
        if arrow is None:
            return
        result = self.session.click_cell(row, col)
        if result in ('blocked', 'over'):
            self.shakes.add(row, col)
            self.hint_text = '前方有箭头挡路！'
            self.hint_timer = 1.0
        elif result == 'flew':
            cell, ox, oy = board_metrics(board)
            self.fly_outs.append(FlyOut(arrow, cell, ox, oy))

    # ---------- 更新 ----------
    def update(self, dt):
        for f in self.fly_outs:
            f.update(dt)
        self.fly_outs = [f for f in self.fly_outs if not f.finished]

        self.shakes.update(dt)

        if self.hint_timer > 0:
            self.hint_timer = max(0.0, self.hint_timer - dt)

        # 飞出动画结束后再判定通关，避免动画被跳过
        if self.session.state == STATE_PLAYING and not self.fly_outs:
            self.session.finish_level()

    # ---------- 绘制 ----------
    def draw(self):
        self.screen.fill(COLOR_BG)
        if self.session.state == STATE_MENU:
            self._draw_menu()
        else:
            self._draw_game()
            self._draw_overlay()

    def _draw_menu(self):
        s = self.screen
        title = self.font_huge.render('一箭又一箭', True, COLOR_ARROW)
        s.blit(title, title.get_rect(center=(WINDOW_W // 2, 180)))

        sub = self.font_mid.render(
            '点击箭头，让它沿自己的方向飞出棋盘', True, COLOR_TEXT)
        s.blit(sub, sub.get_rect(center=(WINDOW_W // 2, 270)))

        lines = [
            '· 前方没有其他箭头阻挡 → 箭头飞出并消失',
            '· 前方有箭头阻挡 → 箭头弹回，失误次数 -1',
            '· 清空全部箭头即通关，失误用尽则失败',
        ]
        for i, line in enumerate(lines):
            t = self.font_norm.render(line, True, COLOR_MUTED)
            s.blit(t, t.get_rect(center=(WINDOW_W // 2, 340 + i * 40)))

        draw_button(s, self.btn_start, '开始游戏', self.font_mid, self.mouse_pos)

    def _draw_game(self):
        s = self.screen
        sess = self.session
        board = sess.board

        # 顶部信息
        level_t = self.font_mid.render(
            '关卡 %d / %d' % (sess.level_no, sess.total_levels), True, COLOR_TEXT)
        s.blit(level_t, (60, 40))

        arrow_t = self.font_mid.render(
            '剩余箭头：%d' % board.remaining, True, COLOR_TEXT)
        s.blit(arrow_t, arrow_t.get_rect(center=(WINDOW_W // 2, 52)))

        mk_color = COLOR_LOSE if sess.mistakes_left <= 1 else COLOR_TEXT
        mk_t = self.font_mid.render(
            '剩余失误：%d / %d' % (sess.mistakes_left, sess.max_mistakes),
            True, mk_color)
        s.blit(mk_t, mk_t.get_rect(topright=(WINDOW_W - 60, 40)))

        # 棋盘格子背景
        cell, ox, oy = board_metrics(board)
        for r in range(board.rows):
            for c in range(board.cols):
                rect = cell_rect(cell, ox, oy, r, c).inflate(-4, -4)
                pygame.draw.rect(s, COLOR_PANEL, rect, border_radius=10)
                pygame.draw.rect(s, COLOR_PANEL_EDGE, rect,
                                 width=2, border_radius=10)

        # 悬停高亮
        if sess.state == STATE_PLAYING and self.hover_cell:
            hr, hc = self.hover_cell
            if board.arrow_at(hr, hc):
                rect = cell_rect(cell, ox, oy, hr, hc).inflate(-6, -6)
                pygame.draw.rect(s, COLOR_HINT, rect, width=3, border_radius=10)

        # 箭头（含抖动偏移）
        for arrow in board.arrows:
            cx, cy = cell_center(cell, ox, oy, arrow.row, arrow.col)
            dx, dy = self.shakes.offset(arrow.row, arrow.col, arrow.direction)
            cx += dx
            cy += dy
            shake = self.shakes.get(arrow.row, arrow.col)
            pts = arrow_polygon(cx, cy, cell, arrow.direction)
            color = COLOR_BLOCK if shake > 0 else COLOR_ARROW
            edge = COLOR_BLOCK_EDGE if shake > 0 else COLOR_ARROW_EDGE
            pygame.draw.polygon(s, color, pts)
            pygame.draw.polygon(s, edge, pts, width=2)

        # 飞出动画
        for f in self.fly_outs:
            f.draw(s)

        # 提示文字
        if self.hint_timer > 0:
            alpha = min(1.0, self.hint_timer / 0.3)
            t = self.font_norm.render(self.hint_text, True, COLOR_LOSE)
            t.set_alpha(int(alpha * 255))
            s.blit(t, t.get_rect(
                center=(WINDOW_W // 2, BOARD_TOP + BOARD_AREA + 26)))

        # 重新开始按钮
        draw_button(s, self.btn_restart, '重新开始', self.font_norm, self.mouse_pos)

    def _draw_overlay(self):
        st = self.session.state
        if st not in (STATE_CLEAR, STATE_OVER, STATE_ALL_CLEAR):
            return
        s = self.screen

        # 半透明遮罩
        mask = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        mask.fill((22, 28, 40, 140))
        s.blit(mask, (0, 0))

        # 卡片
        card = pygame.Rect(0, 0, 460, 300)
        card.center = (WINDOW_W // 2, WINDOW_H // 2 - 20)
        pygame.draw.rect(s, COLOR_CARD, card, border_radius=24)

        if st == STATE_CLEAR:
            title, color = '本关通关！', COLOR_WIN
            sub, btn = '点击按钮进入下一关', '下一关'
        elif st == STATE_ALL_CLEAR:
            title, color = '全部通关！', COLOR_WIN
            sub, btn = '你已经完成了所有关卡', '返回主界面'
        else:
            title, color = '挑战失败', COLOR_LOSE
            sub, btn = '失误次数已经用完啦', '重试本关'

        t = self.font_big.render(title, True, color)
        s.blit(t, t.get_rect(center=(card.centerx, card.top + 70)))

        t2 = self.font_norm.render(sub, True, COLOR_MUTED)
        s.blit(t2, t2.get_rect(center=(card.centerx, card.top + 130)))

        draw_button(s, self.btn_overlay, btn, self.font_mid, self.mouse_pos)