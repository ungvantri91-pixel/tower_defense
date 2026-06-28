from config import *
from core.entities import Enemy, Tower
from algorithms.pathfinding import ALGO_FUNCS
from config import ALGORITHMS

class GameState:
    def __init__(self, level_index=0):
        self.level_index   = level_index
        self.level         = LEVELS[level_index]
        self.grid          = [row[:] for row in self.level["map"]]
        self.base_grid     = [row[:] for row in self.level["map"]]
        self.towers        = []
        self.enemies       = []
        self.score         = 0
        self.lives         = self.level["lives"]
        self.wave          = 0
        self.waves_to_win  = self.level["waves_to_win"]
        self.total_spawned = 0
        self.frame         = 0
        self.game_over     = False
        self.win           = False
        self.heatmap       = {}
        self.show_heatmap  = False
        self.show_paths    = True
        self.paused        = False
        self.selected_algo = 0   
        self.spawn = self._find_tile(SPAWN)
        self.goal  = self._find_tile(GOAL)
        self._compute_heatmap()
    def _find_tile(self, tile_type):
        for r, row in enumerate(self.grid):
            for c, v in enumerate(row):
                if v == tile_type:
                    return (r, c)
        return (1, 1)
    def _compute_heatmap(self):
        from collections import deque
        dist = {}
        q    = deque([self.goal])
        dist[self.goal] = 0
        while q:
            r, c = q.popleft()
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if (0 <= nr < ROWS and 0 <= nc < COLS
                        and self.grid[nr][nc] != WALL
                        and (nr,nc) not in dist):
                    dist[(nr,nc)] = dist[(r,c)] + 1
                    q.append((nr,nc))
        self.heatmap = dist
    def place_tower(self, row, col):
        if self.grid[row][col] != EMPTY:
            return False
        self.grid[row][col] = WALL
        from algorithms.pathfinding import bfs
        if bfs(self.grid, self.spawn, self.goal) is None:
            self.grid[row][col] = EMPTY
            return False
        self.towers.append(Tower(row, col))
        self._compute_heatmap()
        return True
    def remove_tower(self, row, col):
        has_tower = any(t.row == row and t.col == col for t in self.towers)
        if not has_tower:
            return False
        self.grid[row][col] = self.base_grid[row][col]
        self.towers = [t for t in self.towers
                       if not (t.row == row and t.col == col)]
        self._compute_heatmap()
        return True
    def spawn_enemy(self):
        if self.total_spawned >= self.waves_to_win:
            return False
        if any(e.alive for e in self.enemies):
            return False
        algo_name, group = ALGORITHMS[self.selected_algo]
        func = ALGO_FUNCS[algo_name]
        is_boss = (self.total_spawned % 5 == 4)
        energy_mult = self.level.get("energy_mult", 1.0)
        if algo_name == "AND-OR":
            path = [self.spawn]
            e = Enemy(path, algo_name, is_boss, goal=self.goal, energy_mult=energy_mult)
        elif algo_name == "No Observation":
            from algorithms.pathfinding import init_belief_state, no_observation_plan
            path = [self.spawn]
            belief_state = init_belief_state(self.grid, center=self.spawn)
            plan_actions = no_observation_plan(self.grid, self.goal, init_belief=belief_state)[0] or []
            e = Enemy(
                path,
                algo_name,
                is_boss,
                goal=self.goal,
                belief_state=belief_state,
                plan_actions=plan_actions,
                energy_mult=energy_mult,
            )
        else:
            path = func(self.grid, self.spawn, self.goal)
            if path is None:
                path = [self.spawn]
            e = Enemy(path, algo_name, is_boss, goal=self.goal, energy_mult=energy_mult)
        self.enemies.append(e)
        self.total_spawned += 1
        self.wave = self.total_spawned
        return True
    def select_algo(self, idx):
        self.selected_algo = idx % len(ALGORITHMS)
    def next_algo(self):
        self.selected_algo = (self.selected_algo + 1) % len(ALGORITHMS)
    def prev_algo(self):
        self.selected_algo = (self.selected_algo - 1) % len(ALGORITHMS)
    def update(self):
        if self.game_over or self.win or self.paused:
            return
        self.frame += 1
        for e in self.enemies:
            e.update(self.grid)
            if e.reached:
                self.lives -= 1
                e.alive = False
                if self.lives <= 0:
                    self.game_over = True
        for t in self.towers:
            t.update(self.enemies)
        defeated = len([e for e in self.enemies if (not e.alive) and (not e.reached)])
        self.enemies = [e for e in self.enemies if e.alive]
        self.score += defeated * 10
        if (not self.game_over and self.total_spawned >= self.waves_to_win
                and len(self.enemies) == 0):
            self.win = True
    def toggle_heatmap(self):
        self.show_heatmap = not self.show_heatmap
    def toggle_paths(self):
        self.show_paths = not self.show_paths
    def toggle_pause(self):
        self.paused = not self.paused
