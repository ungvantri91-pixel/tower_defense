import math
import pygame
from config import *

class Renderer:
    def __init__(self, surf):
        self.surf = surf
        self.font = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 12)
        self.font_lg = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_xl = pygame.font.SysFont("consolas", 50, bold=True)
        self._menu_button_rects = {}
        self._level_card_rects = []
        self._win_button_rects = {}
        self._gameover_button_rects = {}
    def draw_main_menu(self, hover_key=None):
        self._draw_gradient_background((16, 20, 32), (34, 44, 68))
        self._menu_button_rects = {}
        glow = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        pygame.draw.circle(glow, (80, 120, 255, 40), (SCREEN_W // 2, 110), 180)
        pygame.draw.circle(glow, (80, 220, 180, 24), (SCREEN_W - 180, 340), 200)
        self.surf.blit(glow, (0, 0))
        title = self.font_xl.render("TOWER DEFENSE", True, C_WHITE)
        self.surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 42))
        sub = self.font_md.render("AI PATH OF LEGENDS", True, C_ACCENT)
        self.surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 102))
        left_x = 84
        panel_y = 170
        labels = [
            ("new_game", "NEW GAME", C_ACCENT),
            ("level", "LEVEL", (84, 110, 156)),
            ("exit", "EXIT", (126, 72, 72)),
        ]
        for i, (key, label, color) in enumerate(labels):
            rect = pygame.Rect(left_x, panel_y + i * 84, 230, 54)
            self._menu_button_rects[key] = rect
            hovered = hover_key == key
            fill = _lerp_color(color, C_WHITE, 0.16) if hovered else color
            pygame.draw.rect(self.surf, fill, rect, border_radius=12)
            pygame.draw.rect(self.surf, C_WHITE, rect, 2, border_radius=12)
            txt = self.font_md.render(label, True, C_WHITE)
            self.surf.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
        tip = self.font_sm.render("Main Menu  ->  New Game vào thẳng Level 1 | Level để chọn map", True, C_GRAY)
        self.surf.blit(tip, (58, SCREEN_H - 42))
        art_rect = pygame.Rect(SCREEN_W - 520, 150, 450, 330)
        pygame.draw.rect(self.surf, (22, 28, 42), art_rect, border_radius=18)
        pygame.draw.rect(self.surf, (98, 132, 190), art_rect, 2, border_radius=18)
        self._draw_menu_illustration(art_rect)
    def main_menu_button_at(self, pos):
        for key, rect in self._menu_button_rects.items():
            if rect.collidepoint(pos):
                return key
        return None
    def draw_level_select(self, hover_idx=-1):
        self._draw_gradient_background((20, 22, 30), (34, 38, 50))
        title = self.font_xl.render("SELECT LEVEL", True, C_WHITE)
        self.surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 30))
        sub = self.font_sm.render("Chọn 1 trong 3 map rộng hơn, nhiều đường đi hơn", True, C_GRAY)
        self.surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 88))
        self._level_card_rects = []
        card_w, card_h, gap = 330, 360, 24
        total_w = len(LEVELS) * card_w + (len(LEVELS) - 1) * gap
        start_x = SCREEN_W // 2 - total_w // 2
        y = 130
        for i, lvl in enumerate(LEVELS):
            rect = pygame.Rect(start_x + i * (card_w + gap), y, card_w, card_h)
            self._level_card_rects.append((rect, i))
            hovered = i == hover_idx
            border = C_ACCENT if hovered else (90, 96, 112)
            pygame.draw.rect(self.surf, (28, 31, 42), rect, border_radius=16)
            pygame.draw.rect(self.surf, border, rect, 3 if hovered else 1, border_radius=16)
            preview = pygame.Rect(rect.x + 16, rect.y + 16, rect.w - 32, 182)
            self._draw_map_thumbnail(lvl, preview)
            num = self.font_sm.render(f"[{i + 1}]", True, C_ACCENT)
            self.surf.blit(num, (rect.x + 18, rect.y + 210))
            name = self.font_lg.render(lvl["name"], True, C_WHITE)
            self.surf.blit(name, (rect.centerx - name.get_width() // 2, rect.y + 226))
            subt = self.font_sm.render(lvl["subtitle"], True, C_GRAY)
            self.surf.blit(subt, (rect.centerx - subt.get_width() // 2, rect.y + 266))
            diff_col = {"Dễ": (90, 220, 110), "Trung bình": (230, 190, 60), "Khó": (230, 100, 100)}.get(lvl["difficulty"], C_WHITE)
            info = [
                (f"Độ khó: {lvl['difficulty']}", diff_col),
                (f"Waves: {lvl['waves_to_win']}   Lives: {lvl['lives']}", C_GRAY),
                ("Map lớn, nhiều lối rẽ để đặt tower", C_GRAY),
            ]
            yy = rect.y + 292
            for txt, color in info:
                surf_txt = self.font_sm.render(txt, True, color)
                self.surf.blit(surf_txt, (rect.centerx - surf_txt.get_width() // 2, yy))
                yy += 18
            btn = pygame.Rect(rect.x + 42, rect.bottom - 46, rect.w - 84, 30)
            pygame.draw.rect(self.surf, C_ACCENT if hovered else (72, 78, 98), btn, border_radius=8)
            txt = self.font_sm.render("CHƠI LEVEL", True, C_WHITE)
            self.surf.blit(txt, (btn.centerx - txt.get_width() // 2, btn.centery - txt.get_height() // 2))
        hint = self.font_sm.render("Nhấn 1 / 2 / 3 để vào nhanh, hoặc Esc để quay lại Main Menu", True, C_GRAY)
        self.surf.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 32))
    def _draw_map_thumbnail(self, lvl, rect):
        grid = lvl["map"]
        rows, cols = len(grid), len(grid[0])
        tw = rect.w / cols
        th = rect.h / rows
        pygame.draw.rect(self.surf, lvl["theme_bg"], rect, border_radius=12)
        for r, row in enumerate(grid):
            for c, val in enumerate(row):
                cell = pygame.Rect(rect.x + c * tw, rect.y + r * th, tw + 1, th + 1)
                if val == WALL:
                    pygame.draw.circle(self.surf, lvl["theme_wall"], cell.center, max(2, int(min(tw, th) * 0.55)))
                    pygame.draw.circle(self.surf, _lerp_color(lvl["theme_wall"], C_WHITE, 0.15), (cell.centerx, cell.centery - 1), max(1, int(min(tw, th) * 0.35)))
                else:
                    self._draw_thumbnail_road_tile(grid, r, c, cell, lvl["theme_path"])
                    if val == SPAWN:
                        pygame.draw.circle(self.surf, C_SPAWN, cell.center, max(2, int(min(tw, th) * 0.42)))
                        pygame.draw.circle(self.surf, C_WHITE, cell.center, max(1, int(min(tw, th) * 0.26)), 1)
                    elif val == GOAL:
                        keep = pygame.Rect(cell.centerx - tw * 0.25, cell.centery - th * 0.2, tw * 0.5, th * 0.45)
                        pygame.draw.rect(self.surf, C_GOAL, keep)
        pygame.draw.rect(self.surf, C_WHITE, rect, 1, border_radius=12)
    def level_card_at(self, pos):
        for rect, idx in self._level_card_rects:
            if rect.collidepoint(pos):
                return idx
        return None
    def draw_map(self, gs):
        theme_bg = gs.level.get("theme_bg", C_EMPTY)
        theme_wall = gs.level.get("theme_wall", C_WALL)
        theme_path = gs.level.get("theme_path", (150, 120, 84))
        theme_deco = gs.level.get("theme_deco", theme_wall)
        max_heat = max(gs.heatmap.values()) if gs.heatmap else 1
        pygame.draw.rect(self.surf, theme_bg, (0, 0, COLS * TILE_SIZE, ROWS * TILE_SIZE))
        for r, row in enumerate(gs.grid):
            for c, val in enumerate(row):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                self._draw_grass_tile(rect, theme_bg, theme_deco, r, c)
        for r, row in enumerate(gs.grid):
            for c, val in enumerate(row):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if val != WALL:
                    road_color = theme_path
                    if gs.show_heatmap and (r, c) in gs.heatmap:
                        t = gs.heatmap[(r, c)] / max_heat
                        heat = _lerp_color(C_HEATMAP_HI, C_HEATMAP_LO, t)
                        road_color = _lerp_color(theme_path, heat, 0.28)
                    self._draw_road_tile(gs.grid, r, c, rect, road_color)
        for r, row in enumerate(gs.grid):
            for c, val in enumerate(row):
                if val == WALL:
                    rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    self._draw_tree_tile(rect, theme_wall, theme_deco, r, c)
        for r, row in enumerate(gs.grid):
            for c, val in enumerate(row):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if val == SPAWN:
                    self._draw_spawn_portal(rect)
                elif val == GOAL:
                    self._draw_goal_castle(rect)
        for e in gs.enemies:
            if e.alive and e.algo_name == "No Observation" and e.belief_state:
                self._draw_belief_state(e)
        if gs.show_paths:
            for e in gs.enemies:
                if e.alive and len(e.path) > 1:
                    self._draw_fancy_path(e)
    def _draw_grass_tile(self, rect, grass_color, deco_color, row, col):
        tint = ((row * 17 + col * 29) % 9) - 4
        grass = tuple(max(0, min(255, ch + tint)) for ch in grass_color)
        pygame.draw.rect(self.surf, grass, rect)
        for i in range(2):
            sx = rect.x + 6 + ((row * 11 + col * 7 + i * 13) % max(8, TILE_SIZE - 12))
            sy = rect.y + 6 + ((row * 5 + col * 17 + i * 19) % max(8, TILE_SIZE - 12))
            blade = _lerp_color(deco_color, C_WHITE, 0.1)
            pygame.draw.line(self.surf, blade, (sx, sy + 3), (sx + 1, sy - 2), 1)
            pygame.draw.line(self.surf, blade, (sx + 2, sy + 4), (sx + 3, sy), 1)
        if (row * 13 + col * 31) % 23 == 0:
            rock = _lerp_color(grass_color, (120, 120, 120), 0.45)
            pygame.draw.circle(self.surf, rock, (rect.x + TILE_SIZE // 2, rect.y + TILE_SIZE // 2 + 2), 3)
    def _draw_road_tile(self, grid, row, col, rect, road_color):
        up = self._is_walkable(grid, row - 1, col)
        down = self._is_walkable(grid, row + 1, col)
        left = self._is_walkable(grid, row, col - 1)
        right = self._is_walkable(grid, row, col + 1)
        border = _lerp_color(road_color, (98, 78, 58), 0.42)
        fill = _lerp_color(road_color, C_WHITE, 0.08)
        self._draw_connected_blob(rect, up, down, left, right, border, 4, 8)
        self._draw_connected_blob(rect, up, down, left, right, fill, 7, 7)
        line = _lerp_color(fill, (140, 110, 78), 0.35)
        pygame.draw.line(self.surf, line, (rect.x + 9, rect.centery + 2), (rect.right - 9, rect.centery - 1), 1)
    def _draw_connected_blob(self, rect, up, down, left, right, color, pad, radius):
        cx = pygame.Rect(rect.x + pad, rect.y + pad, rect.w - pad * 2, rect.h - pad * 2)
        pygame.draw.rect(self.surf, color, cx, border_radius=radius)
        if up:
            pygame.draw.rect(self.surf, color, (cx.x, rect.y, cx.w, rect.centery - rect.y), border_radius=radius)
        if down:
            pygame.draw.rect(self.surf, color, (cx.x, rect.centery, cx.w, rect.bottom - rect.centery), border_radius=radius)
        if left:
            pygame.draw.rect(self.surf, color, (rect.x, cx.y, rect.centerx - rect.x, cx.h), border_radius=radius)
        if right:
            pygame.draw.rect(self.surf, color, (rect.centerx, cx.y, rect.right - rect.centerx, cx.h), border_radius=radius)
    def _draw_tree_tile(self, rect, tree_color, deco_color, row, col):
        trunk = _lerp_color(tree_color, C_WOOD, 0.45)
        dark = _lerp_color(tree_color, (18, 52, 28), 0.36)
        light = _lerp_color(tree_color, C_WHITE, 0.18)
        pygame.draw.rect(self.surf, trunk, (rect.centerx - 3, rect.bottom - 10, 6, 8), border_radius=2)
        pygame.draw.circle(self.surf, dark, (rect.centerx, rect.centery + 1), 13)
        pygame.draw.circle(self.surf, tree_color, (rect.centerx - 7, rect.centery), 10)
        pygame.draw.circle(self.surf, tree_color, (rect.centerx + 7, rect.centery), 10)
        pygame.draw.circle(self.surf, light, (rect.centerx - 4, rect.centery - 5), 6)
        if (row + col) % 3 == 0:
            pygame.draw.circle(self.surf, _lerp_color(deco_color, C_WHITE, 0.2), (rect.x + 9, rect.y + 10), 3)
    def _draw_spawn_portal(self, rect):
        glow = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2), pygame.SRCALPHA)
        center = (glow.get_width() // 2, glow.get_height() // 2)
        pygame.draw.circle(glow, (60, 150, 255, 35), center, 28)
        pygame.draw.circle(glow, (60, 200, 255, 55), center, 20)
        self.surf.blit(glow, (rect.centerx - glow.get_width() // 2, rect.centery - glow.get_height() // 2))
        pygame.draw.ellipse(self.surf, (45, 85, 140), (rect.centerx - 10, rect.centery - 15, 20, 30))
        pygame.draw.ellipse(self.surf, (80, 210, 255), (rect.centerx - 8, rect.centery - 13, 16, 26))
        pygame.draw.ellipse(self.surf, (200, 245, 255), (rect.centerx - 5, rect.centery - 8, 10, 16), 2)
        pygame.draw.arc(self.surf, (220, 250, 255), (rect.centerx - 11, rect.centery - 16, 22, 32), 0.7, 2.5, 2)
        pygame.draw.arc(self.surf, (220, 250, 255), (rect.centerx - 11, rect.centery - 16, 22, 32), 3.7, 5.5, 2)
    def _draw_goal_castle(self, rect):
        base = pygame.Rect(rect.centerx - 11, rect.centery - 6, 22, 18)
        tower_l = pygame.Rect(rect.centerx - 15, rect.centery - 16, 8, 26)
        tower_r = pygame.Rect(rect.centerx + 7, rect.centery - 16, 8, 26)
        stone = (132, 140, 154)
        dark = (90, 96, 112)
        light = (186, 194, 205)
        for tower in [tower_l, tower_r]:
            pygame.draw.rect(self.surf, dark, tower.move(0, 2), border_radius=2)
            pygame.draw.rect(self.surf, stone, tower, border_radius=2)
            for i in range(3):
                crenel = pygame.Rect(tower.x + i * 3, tower.y - 3, 2, 5)
                pygame.draw.rect(self.surf, stone, crenel)
        pygame.draw.rect(self.surf, dark, base.move(0, 2), border_radius=3)
        pygame.draw.rect(self.surf, stone, base, border_radius=3)
        pygame.draw.rect(self.surf, light, (base.x + 2, base.y + 2, base.w - 4, 4), border_radius=2)
        gate = pygame.Rect(rect.centerx - 4, rect.centery + 1, 8, 11)
        pygame.draw.rect(self.surf, dark, gate, border_radius=4)
        pygame.draw.line(self.surf, (210, 70, 70), (tower_r.centerx, tower_r.y - 4), (tower_r.centerx, tower_r.y - 12), 2)
        pygame.draw.polygon(self.surf, (230, 90, 90), [(tower_r.centerx, tower_r.y - 12), (tower_r.centerx + 8, tower_r.y - 9), (tower_r.centerx, tower_r.y - 6)])
    def _draw_thumbnail_road_tile(self, grid, row, col, rect, road_color):
        up = self._is_walkable(grid, row - 1, col)
        down = self._is_walkable(grid, row + 1, col)
        left = self._is_walkable(grid, row, col - 1)
        right = self._is_walkable(grid, row, col + 1)
        border = _lerp_color(road_color, (98, 78, 58), 0.42)
        fill = _lerp_color(road_color, C_WHITE, 0.08)
        self._draw_connected_blob(rect, up, down, left, right, border, 1, 3)
        self._draw_connected_blob(rect, up, down, left, right, fill, 2, 2)
    def _is_walkable(self, grid, row, col):
        return 0 <= row < len(grid) and 0 <= col < len(grid[0]) and grid[row][col] != WALL
    def _draw_fancy_path(self, enemy):
        path = enemy.path
        color = enemy.color
        overlay = pygame.Surface((COLS * TILE_SIZE, ROWS * TILE_SIZE), pygame.SRCALPHA)
        for i in range(len(path) - 1):
            x0, y0 = _tile_center(*path[i])
            x1, y1 = _tile_center(*path[i + 1])
            dx, dy = x1 - x0, y1 - y0
            dist = math.hypot(dx, dy)
            if dist <= 0:
                continue
            ux, uy = dx / dist, dy / dist
            d = 8
            while d < dist - 3:
                px, py = int(x0 + ux * d), int(y0 + uy * d)
                alpha = int(190 - (i / max(len(path) - 1, 1)) * 90)
                pygame.draw.circle(overlay, (*color[:3], alpha), (px, py), 3)
                d += 9
        for i, tile in enumerate(path):
            px, py = _tile_center(*tile)
            if i == 0:
                pygame.draw.circle(overlay, (*color[:3], 220), (px, py), 6)
                pygame.draw.circle(overlay, (255, 255, 255, 180), (px, py), 6, 2)
            elif i == len(path) - 1:
                pygame.draw.circle(overlay, (*color[:3], 200), (px, py), 5)
        mid = len(path) // 2
        if mid > 0:
            _draw_arrow(overlay, color, _tile_center(*path[mid - 1]), _tile_center(*path[mid]), size=7)
        self.surf.blit(overlay, (0, 0))
    def draw_entities(self, gs):
        for t in gs.towers:
            t.draw(self.surf)
        for e in gs.enemies:
            e.draw(self.surf, self.font_sm)
        for e in gs.enemies:
            if e.alive:
                self._draw_runtime_cues(e)
    def draw_panel(self, gs):
        px = COLS * TILE_SIZE
        pygame.draw.rect(self.surf, C_PANEL, (px, 0, PANEL_W, SCREEN_H))
        pygame.draw.line(self.surf, (88, 92, 110), (px, 0), (px, SCREEN_H), 2)
        y = 12
        self._text(self.font_md, "TOWER DEFENSE", C_ACCENT, px + 12, y)
        y += 24
        self._text(self.font_sm, f"Level {gs.level_index + 1}: {gs.level['name']}", C_WHITE, px + 12, y)
        y += 20
        self._hline(px, y)
        y += 10
        stats = [
            (f"Wave   : {gs.wave}/{gs.waves_to_win}", C_WHITE),
            (f"Score  : {gs.score}", C_ACCENT),
            (f"Lives  : {gs.lives}", _hp_color(gs.lives)),
            (f"Blocks : {len(gs.towers)}", C_WHITE),
            (f"Enemies: {len(gs.enemies)}", C_GRAY),
        ]
        for txt, color in stats:
            self._text(self.font, txt, color, px + 12, y)
            y += 18
        if gs.enemies:
            lead = gs.enemies[0]
            self._text(self.font, f"Energy : {lead.energy:5.1f}", C_ENERGY, px + 12, y)
            y += 18
            if lead.algo_name == "AND-OR":
                self._text(self.font_sm, f"Intent: {lead.intended_tile}", GROUP_COLORS["Complex"], px + 12, y)
                y += 15
            if lead.algo_name == "No Observation":
                belief = len(lead.belief_state) if lead.belief_state else 0
                self._text(self.font_sm, f"Belief: {belief}", C_BELIEF, px + 12, y)
                y += 15
        if gs.paused:
            self._text(self.font, "State  : Paused", C_ACCENT, px + 12, y)
            y += 18
        y += 2
        self._hline(px, y)
        y += 10
        self._text(self.font, "Algorithms:", C_WHITE, px + 12, y)
        y += 18
        key_labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="]
        for i, (name, group) in enumerate(ALGORITHMS):
            gc = GROUP_COLORS.get(group, C_WHITE)
            row_rect = pygame.Rect(px + 8, y - 2, PANEL_W - 16, 15)
            selected = i == gs.selected_algo
            active = any(e.algo_name == name for e in gs.enemies if e.alive)
            if selected:
                pygame.draw.rect(self.surf, (*gc[:3], 70), row_rect)
                pygame.draw.rect(self.surf, gc, row_rect, 1)
            elif active:
                pygame.draw.rect(self.surf, (*gc[:3], 35), row_rect)
            self._text(self.font_sm, f"[{key_labels[i]}]", C_ACCENT if selected else C_GRAY, px + 10, y)
            prefix = "►" if selected else ("●" if active else "○")
            self._text(self.font_sm, f"{prefix} {name:<14} [{group[:3]}]", C_WHITE if selected else gc if active else C_GRAY, px + 36, y)
            y += 15
        y += 6
        self._hline(px, y)
        y += 10
        controls = [
            "[Enter] Thả 1 quái",
            "[LClick] Đặt vật cản",
            "[RClick] Dỡ vật cản",
            "[↑ / ↓] Đổi thuật toán",
            "[1-9,0,-,=] Chọn nhanh",
            "[H / P] Heatmap / Path",
            "[Space] Pause",
            "[R / Esc] Restart / Level Select",
        ]
        for line in controls:
            self._text(self.font_sm, line, C_GRAY, px + 12, y)
            y += 14
        y += 6
        self._hline(px, y)
        y += 10
        self._text(self.font, "Vật cản:", C_WHITE, px + 12, y)
        y += 18
        self._text(self.font_sm, "Chức năng: chặn đường quái", C_GRAY, px + 12, y)
        y += 14
        self._text(self.font_sm, "Không bắn ra mũi tên", C_GRAY, px + 12, y)
    def draw_game_over(self, gs):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 172))
        self.surf.blit(overlay, (0, 0))
        title = self.font_lg.render("GAME OVER", True, (230, 92, 92))
        self.surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 92))
        sub = self.font.render(f"{gs.level['name']}  |  Wave {gs.wave}/{gs.waves_to_win}  |  Score {gs.score}", True, C_WHITE)
        self.surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 - 50))
        self._gameover_button_rects = {}
        btn_w, btn_h, gap = 170, 42, 20
        bx = SCREEN_W // 2 - (btn_w * 2 + gap) // 2
        by = SCREEN_H // 2 + 6
        retry = pygame.Rect(bx, by, btn_w, btn_h)
        levels = pygame.Rect(bx + btn_w + gap, by, btn_w, btn_h)
        self._gameover_button_rects["retry"] = retry
        self._gameover_button_rects["levels"] = levels
        self._draw_button(retry, "Thử lại", C_ACCENT)
        self._draw_button(levels, "Chọn Level", (86, 92, 114))
    def gameover_button_at(self, pos):
        for name, rect in self._gameover_button_rects.items():
            if rect.collidepoint(pos):
                return name
        return None
    def draw_paused(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 132))
        self.surf.blit(overlay, (0, 0))
        title = self.font_lg.render("PAUSED", True, (255, 220, 120))
        self.surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 22))
        sub = self.font.render("Nhấn Space để tiếp tục", True, C_WHITE)
        self.surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 + 24))
    def draw_win(self, gs, is_last_level):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 172))
        self.surf.blit(overlay, (0, 0))
        title = self.font_lg.render("HOÀN THÀNH LEVEL!", True, (88, 220, 126))
        self.surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 112))
        sub = self.font.render(f"{gs.level['name']}  |  Score {gs.score}  |  Lives còn {gs.lives}", True, C_WHITE)
        self.surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 - 72))
        self._win_button_rects = {}
        labels = []
        if not is_last_level:
            labels.append(("next", "Level Tiếp", C_ACCENT))
        labels.append(("retry", "Chơi lại", (86, 92, 114)))
        labels.append(("levels", "Chọn Level", (86, 92, 114)))
        btn_w, btn_h, gap = 180, 42, 18
        total_w = len(labels) * btn_w + (len(labels) - 1) * gap
        bx = SCREEN_W // 2 - total_w // 2
        by = SCREEN_H // 2 - 6
        for i, (key, label, color) in enumerate(labels):
            rect = pygame.Rect(bx + i * (btn_w + gap), by, btn_w, btn_h)
            self._win_button_rects[key] = rect
            self._draw_button(rect, label, color)
        if is_last_level:
            msg = self.font.render("Bạn đã hoàn thành cả 3 map.", True, (255, 220, 120))
            self.surf.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, by + btn_h + 22))
    def win_button_at(self, pos):
        for name, rect in self._win_button_rects.items():
            if rect.collidepoint(pos):
                return name
        return None
    def _draw_button(self, rect, label, color):
        pygame.draw.rect(self.surf, color, rect, border_radius=10)
        pygame.draw.rect(self.surf, C_WHITE, rect, 2, border_radius=10)
        txt = self.font.render(label, True, C_WHITE)
        self.surf.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
    def draw_hover(self, row, col, valid):
        if row < 0 or col < 0 or row >= ROWS or col >= COLS:
            return
        color = (100, 220, 180, 90) if valid else (220, 80, 80, 90)
        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (0, 0, TILE_SIZE, TILE_SIZE), border_radius=6)
        self.surf.blit(s, (col * TILE_SIZE, row * TILE_SIZE))
    def _draw_belief_state(self, enemy):
        overlay = pygame.Surface((COLS * TILE_SIZE, ROWS * TILE_SIZE), pygame.SRCALPHA)
        for r, c in enemy.belief_state:
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(overlay, (*C_BELIEF, 42), rect, border_radius=6)
            pygame.draw.rect(overlay, (*C_BELIEF, 96), rect, 1, border_radius=6)
            pygame.draw.circle(overlay, (*C_BELIEF, 148), rect.center, 4)
        self.surf.blit(overlay, (0, 0))
    def _draw_runtime_cues(self, enemy):
        if enemy.intended_tile is None:
            return
        cur_tile = enemy.path[enemy.path_idx] if enemy.path else None
        if cur_tile is None or cur_tile == enemy.intended_tile:
            return
        cue = pygame.Surface((COLS * TILE_SIZE, ROWS * TILE_SIZE), pygame.SRCALPHA)
        p_from = _tile_center(*cur_tile)
        p_to = _tile_center(*enemy.intended_tile)
        color = C_BELIEF if enemy.algo_name == "No Observation" else GROUP_COLORS["Complex"]
        pygame.draw.line(cue, (*color[:3], 140), p_from, p_to, 2)
        _draw_arrow(cue, color, p_from, p_to, size=8)
        self.surf.blit(cue, (0, 0))
    def _draw_menu_illustration(self, rect):
        sky = pygame.Rect(rect.x + 16, rect.y + 16, rect.w - 32, rect.h - 32)
        pygame.draw.rect(self.surf, (38, 54, 86), sky, border_radius=14)
        pygame.draw.circle(self.surf, (88, 120, 200), (sky.right - 70, sky.y + 60), 28)
        ground = pygame.Rect(sky.x + 12, sky.bottom - 90, sky.w - 24, 64)
        pygame.draw.rect(self.surf, (102, 182, 92), ground, border_radius=18)
        path = [(ground.x + 22, ground.y + 10), (ground.x + 120, ground.y + 22), (ground.x + 230, ground.y + 6), (ground.right - 24, ground.y + 28)]
        pygame.draw.lines(self.surf, (174, 142, 92), False, path, 18)
        pygame.draw.lines(self.surf, (210, 182, 132), False, path, 8)
        tower_x, tower_y = rect.x + 126, rect.y + 204
        pygame.draw.rect(self.surf, (62, 74, 94), (tower_x - 24, tower_y + 12, 48, 18), border_radius=10)
        pygame.draw.rect(self.surf, (112, 126, 148), (tower_x - 12, tower_y - 16, 24, 32), border_radius=6)
        roof = [(tower_x - 18, tower_y - 12), (tower_x, tower_y - 32), (tower_x + 18, tower_y - 12)]
        pygame.draw.polygon(self.surf, (84, 108, 152), roof)
        pygame.draw.line(self.surf, C_WOOD, (tower_x - 16, tower_y - 6), (tower_x + 16, tower_y + 18), 4)
        pygame.draw.line(self.surf, C_WOOD, (tower_x - 16, tower_y + 18), (tower_x + 16, tower_y - 6), 4)
        px, py = rect.x + 82, rect.y + 212
        pygame.draw.circle(self.surf, (60, 150, 255), (px, py), 12)
        pygame.draw.circle(self.surf, (190, 240, 255), (px, py), 8, 2)
        pygame.draw.circle(self.surf, (60, 150, 255, 60), (px, py), 20)
        sx, sy = rect.x + 330, rect.y + 212
        stone = (132, 140, 154)
        pygame.draw.rect(self.surf, stone, (sx - 18, sy - 2, 36, 24), border_radius=4)
        pygame.draw.rect(self.surf, stone, (sx - 24, sy - 14, 10, 30), border_radius=3)
        pygame.draw.rect(self.surf, stone, (sx + 14, sy - 14, 10, 30), border_radius=3)
        pygame.draw.rect(self.surf, (88, 96, 112), (sx - 5, sy + 4, 10, 16), border_radius=4)
        pygame.draw.line(self.surf, (210, 70, 70), (sx + 19, sy - 18), (sx + 19, sy - 30), 2)
        pygame.draw.polygon(self.surf, (230, 90, 90), [(sx + 19, sy - 30), (sx + 28, sy - 27), (sx + 19, sy - 23)])
        txt = self.font_sm.render("Portal xanh  •  Castle goal  •  Vật cản chặn đường", True, C_WHITE)
        self.surf.blit(txt, (rect.centerx - txt.get_width() // 2, rect.bottom - 36))
    def _draw_gradient_background(self, top, bottom):
        for y in range(SCREEN_H):
            t = y / max(SCREEN_H - 1, 1)
            col = _lerp_color(top, bottom, t)
            pygame.draw.line(self.surf, col, (0, y), (SCREEN_W, y))
    def _text(self, font, txt, color, x, y):
        self.surf.blit(font.render(txt, True, color), (x, y))
    def _center_text(self, font, txt, color, rect):
        s = font.render(txt, True, color)
        self.surf.blit(s, (rect.centerx - s.get_width() // 2, rect.centery - s.get_height() // 2))
    def _hline(self, px, y):
        pygame.draw.line(self.surf, C_GRAY, (px + 8, y), (px + PANEL_W - 8, y), 1)

def _tile_center(r, c):
    return (c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2)

def _draw_arrow(surf, color, p_from, p_to, size=7):
    dx = p_to[0] - p_from[0]
    dy = p_to[1] - p_from[1]
    dist = math.hypot(dx, dy)
    if dist < 1:
        return
    ux, uy = dx / dist, dy / dist
    mx, my = (p_from[0] + p_to[0]) // 2, (p_from[1] + p_to[1]) // 2
    tip = (int(mx + ux * size), int(my + uy * size))
    perp_x, perp_y = -uy, ux
    wing = size * 0.55
    w1 = (int(mx - ux * size + perp_x * wing), int(my - uy * size + perp_y * wing))
    w2 = (int(mx - ux * size - perp_x * wing), int(my - uy * size - perp_y * wing))
    pygame.draw.polygon(surf, (*color[:3], 200), [tip, w1, w2])

def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def _hp_color(lives):
    if lives > 10:
        return (60, 220, 80)
    if lives > 5:
        return (220, 180, 40)
    return (220, 60, 60)
