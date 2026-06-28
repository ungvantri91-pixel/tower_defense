import math
import pygame
from config import *

class Enemy:
    def __init__(self, path, algo_name, is_boss=False, goal=None,
                 belief_state=None, plan_actions=None, energy_mult=1.0):
        self.path = path
        self.path_idx = 0
        self.algo_name = algo_name
        self.is_boss = is_boss
        if algo_name in {"AND-OR", "No Observation"}:
            self.speed = VISUAL_BOSS_SPEED if is_boss else VISUAL_ENEMY_SPEED
        else:
            self.speed = 1.48 if not is_boss else 0.84
        self.color = C_ENEMY2 if is_boss else C_ENEMY
        self.size = 15 if not is_boss else 19
        self.alive = True
        self.reached = False
        self.max_energy = (BOSS_ENERGY if is_boss else ENEMY_ENERGY) * energy_mult
        self.energy = self.max_energy
        self.stuck = False
        self.intended_tile = None
        self.current_action = None
        self.current_action_label = ""
        self.slip_timer = 0
        self.belief_state = set(belief_state) if belief_state is not None else None
        self.plan_actions = list(plan_actions) if plan_actions else []
        self._goal = goal if goal is not None else (path[-1] if path else (0, 0))
        self.anim = 0.0
        if path:
            r, c = path[0]
            self.x = c * TILE_SIZE + TILE_SIZE // 2
            self.y = r * TILE_SIZE + TILE_SIZE // 2
        else:
            self.x = self.y = 0
    def hit(self, damage, energy_damage=None):
        if not self.alive or self.reached:
            return False
        drain = energy_damage if energy_damage is not None else damage
        self.energy = max(0.0, self.energy - drain)
        if self.energy <= 0:
            self.alive = False
        return True
    def update(self, grid):
        if not self.alive or self.reached:
            return
        self.anim += 0.18
        if self.slip_timer > 0:
            self.slip_timer -= 1
        self.energy = max(0.0, self.energy - ENERGY_DRAIN_PER_FRAME)
        if self.energy <= 0:
            self.alive = False
            return
        if self.stuck:
            return
        if self.path_idx >= len(self.path) - 1:
            cur_tile = self.path[self.path_idx]
            if cur_tile == self._goal:
                self.reached = True
                return
            if self.algo_name == "Hill Climbing":
                self.stuck = True
                return
            if self.algo_name == "AND-OR":
                self._advance_and_or(grid)
                return
            if self.algo_name == "No Observation":
                self._advance_no_observation(grid)
                return
            self.reached = True
            return
        next_r, next_c = self.path[self.path_idx + 1]
        if grid[next_r][next_c] == WALL:
            cur_r, cur_c = self.path[self.path_idx]
            from algorithms.pathfinding import ALGO_FUNCS, bfs, no_observation_plan
            if self.algo_name == "AND-OR":
                self.path = self.path[:self.path_idx + 1]
                self._advance_and_or(grid)
                return
            if self.algo_name == "No Observation":
                self.path = self.path[:self.path_idx + 1]
                self.intended_tile = None
                plan = no_observation_plan(grid, self._goal, init_belief=self.belief_state)[0]
                self.plan_actions = list(plan) if plan else []
                if plan is None:
                    self.stuck = True
                return
            replanner = ALGO_FUNCS.get(self.algo_name, bfs)
            new_path = replanner(grid, (cur_r, cur_c), self._goal)
            if new_path is None:
                new_path = bfs(grid, (cur_r, cur_c), self._goal)
            if new_path:
                self.path = self.path[:self.path_idx + 1] + new_path[1:]
            return
        tx = next_c * TILE_SIZE + TILE_SIZE // 2
        ty = next_r * TILE_SIZE + TILE_SIZE // 2
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.x, self.y = tx, ty
            self.path_idx += 1
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed
    def _advance_and_or(self, grid):
        from algorithms.pathfinding import and_or_next_step, and_or_sample_outcome, bfs
        cur_tile = self.path[self.path_idx]
        recent = set(self.path[max(0, self.path_idx - 6):self.path_idx + 1])
        intended = and_or_next_step(grid, cur_tile, self._goal, avoid=recent)
        if intended is None:
            fallback = bfs(grid, cur_tile, self._goal)
            if fallback and len(fallback) > 1:
                intended = fallback[1]
            else:
                self.stuck = True
                self.intended_tile = None
                return
        actual = and_or_sample_outcome(grid, cur_tile, intended)
        self.intended_tile = intended
        self.current_action = None
        self.current_action_label = "Trượt" if actual != intended else "Ổn"
        if actual != intended:
            self.slip_timer = 24
        self.path = self.path[:self.path_idx + 1] + [actual]
    def _advance_no_observation(self, grid):
        from algorithms.pathfinding import (
            no_observation_plan,
            no_observation_next_action,
            step_with_action,
            apply_action_to_belief,
            action_to_label,
        )
        cur_tile = self.path[self.path_idx]
        if self.belief_state is None:
            self.belief_state = {cur_tile}
        if not self.plan_actions:
            plan, _ = no_observation_plan(grid, self._goal, init_belief=self.belief_state)
            if plan is not None:
                self.plan_actions = list(plan)
        if self.plan_actions:
            action = self.plan_actions.pop(0)
            new_belief = set(apply_action_to_belief(grid, self.belief_state, action))
        else:
            action, new_belief = no_observation_next_action(grid, self.belief_state, self._goal)
            if action is None:
                self.stuck = True
                self.current_action = None
                self.current_action_label = "Không có action"
                self.intended_tile = None
                return
        self.current_action = action
        self.current_action_label = action_to_label(action)
        self.belief_state = set(new_belief)
        actual = step_with_action(grid, cur_tile, action)
        self.intended_tile = actual
        self.path = self.path[:self.path_idx + 1] + [actual]
    def draw(self, surf, font_small):
        if not self.alive:
            return
        cx, cy = int(self.x), int(self.y)
        bob = math.sin(self.anim) * 1.6
        cy_bob = cy + bob
        skull_r = 7 if not self.is_boss else 9
        torso_h = 12 if not self.is_boss else 15
        bone = (236, 236, 230)
        outline = (64, 64, 74)
        cloak = (72, 76, 102) if not self.is_boss else (120, 92, 46)
        sword = (198, 210, 225)
        pygame.draw.line(surf, bone, (cx, cy_bob - 1), (cx, cy_bob + torso_h), 3)
        pygame.draw.line(surf, bone, (cx - 8, cy_bob + 4), (cx + 8, cy_bob + 2), 3)
        pygame.draw.line(surf, bone, (cx - 2, cy_bob + torso_h), (cx - 8, cy_bob + torso_h + 10), 3)
        pygame.draw.line(surf, bone, (cx + 2, cy_bob + torso_h), (cx + 8, cy_bob + torso_h + 10), 3)
        pygame.draw.line(surf, bone, (cx + 5, cy_bob + 3), (cx + 14, cy_bob + 10), 3)
        pygame.draw.line(surf, sword, (cx + 14, cy_bob + 10), (cx + 20, cy_bob - 1), 3)
        pygame.draw.line(surf, C_WOOD, (cx + 12, cy_bob + 11), (cx + 18, cy_bob + 0), 2)
        pygame.draw.line(surf, sword, (cx + 11, cy_bob + 6), (cx + 17, cy_bob + 6), 2)
        pygame.draw.line(surf, bone, (cx - 5, cy_bob + 3), (cx - 12, cy_bob + 12), 3)
        pygame.draw.polygon(
            surf, cloak,
            [(cx - 7, cy_bob + 3), (cx + 7, cy_bob + 3), (cx + 10, cy_bob + 15), (cx - 10, cy_bob + 15)]
        )
        pygame.draw.circle(surf, bone, (cx, int(cy_bob - 8)), skull_r)
        pygame.draw.circle(surf, outline, (cx - 3, int(cy_bob - 9)), 2)
        pygame.draw.circle(surf, outline, (cx + 3, int(cy_bob - 9)), 2)
        pygame.draw.line(surf, outline, (cx - 3, cy_bob - 3), (cx + 3, cy_bob - 3), 1)
        pygame.draw.rect(surf, outline, (cx - 4, cy_bob - 1, 8, 2))
        pygame.draw.circle(surf, outline, (cx, int(cy_bob - 8)), skull_r, 2)
        bar_w = self.size * 2 + 6
        bar_x = cx - bar_w // 2
        bar_y = int(cy_bob - self.size - 13)
        fill_w = int(bar_w * self.energy / self.max_energy) if self.max_energy > 0 else 0
        pygame.draw.rect(surf, (28, 34, 44), (bar_x, bar_y, bar_w, 6), border_radius=3)
        pygame.draw.rect(surf, C_ENERGY, (bar_x, bar_y, fill_w, 6), border_radius=3)
        label = font_small.render(self.algo_name[:4], True, C_WHITE)
        surf.blit(label, (cx - label.get_width() // 2, cy - label.get_height() // 2 + 2))
        if self.slip_timer > 0:
            slip = font_small.render("SLIP", True, (255, 220, 120))
            surf.blit(slip, (cx - slip.get_width() // 2, cy - self.size - 24))

class Tower:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = row * TILE_SIZE + TILE_SIZE // 2
    def update(self, enemies):
        return None
    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        tile_rect = pygame.Rect(self.col * TILE_SIZE + 3, self.row * TILE_SIZE + 3, TILE_SIZE - 6, TILE_SIZE - 6)
        pygame.draw.rect(surf, (74, 64, 52), tile_rect, border_radius=8)
        pygame.draw.rect(surf, (170, 146, 108), tile_rect, 2, border_radius=8)
        pygame.draw.line(surf, C_WOOD, (tile_rect.left + 5, tile_rect.top + 8), (tile_rect.right - 5, tile_rect.bottom - 8), 4)
        pygame.draw.line(surf, C_WOOD, (tile_rect.left + 5, tile_rect.bottom - 8), (tile_rect.right - 5, tile_rect.top + 8), 4)
        band = pygame.Rect(cx - 10, cy - 4, 20, 8)
        pygame.draw.rect(surf, (118, 126, 138), band, border_radius=4)
        pygame.draw.rect(surf, C_WHITE, band, 1, border_radius=4)
