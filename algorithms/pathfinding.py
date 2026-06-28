import heapq, random, math
from collections import deque
from config import (
    TILE_COST, WALL, ROWS, COLS, EMPTY, ADVERSARIAL_TURN_ENERGY,
    NOOBS_INITIAL_BELIEF_RADIUS,
)

NOOBS_ACTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
ACTION_LABELS = {
    (-1, 0): "Lên",
    (1, 0): "Xuống",
    (0, -1): "Trái",
    (0, 1): "Phải",
}

def _neighbors(r, c, grid):
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != WALL:
            yield nr, nc

def _cost(grid, r, c):
    return TILE_COST.get(grid[r][c], 1)

def _reconstruct(came, node):
    path = []
    while node in came:
        path.append(node)
        node = came[node]
    path.append(node)
    return list(reversed(path))

def _manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def _path_cost(grid, path):
    if not path:
        return float('inf')
    return sum(_cost(grid, r, c) for r, c in path[1:]) + len(path) - 1

def step_with_action(grid, pos, action):
    r, c = pos
    dr, dc = action
    nr, nc = r + dr, c + dc
    if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != WALL:
        return (nr, nc)
    return pos

def init_belief_state(grid, center=None, radius=NOOBS_INITIAL_BELIEF_RADIUS):
    if center is None:
        return frozenset(
            (r, c)
            for r in range(ROWS)
            for c in range(COLS)
            if grid[r][c] != WALL
        )
    cr, cc = center
    belief = {
        (r, c)
        for r in range(ROWS)
        for c in range(COLS)
        if grid[r][c] != WALL and abs(r - cr) + abs(c - cc) <= radius
    }
    if not belief:
        belief = {center}
    return frozenset(belief)

def apply_action_to_belief(grid, belief, action):
    return frozenset(step_with_action(grid, pos, action) for pos in belief)

def action_to_label(action):
    return ACTION_LABELS.get(action, "N/A")

def _andor_side_outcomes(pos, intended, grid):
    r, c = pos
    tr, tc = intended
    dr, dc = tr - r, tc - c
    if dr != 0:
        candidates = [(r, c - 1), (r, c + 1)]
    else:  
        candidates = [(r - 1, c), (r + 1, c)]
    outcomes = [intended]
    for nr, nc in candidates:
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != WALL:
            outcomes.append((nr, nc))
        else:
            outcomes.append(pos)  
    unique = []
    for state in outcomes:
        if state not in unique:
            unique.append(state)
    return unique

def and_or_next_step(grid, start, goal, avoid=None):
    avoid = avoid or set()
    candidates = [nb for nb in _neighbors(*start, grid)
                  if nb not in avoid or nb == goal]
    if not candidates:
        candidates = list(_neighbors(*start, grid))
    if not candidates:
        return None
    best_step = None
    best_score = None

    for intended in sorted(candidates, key=lambda nb: (_manhattan(nb, goal), _cost(grid, *nb))):
        outcomes = _andor_side_outcomes(start, intended, grid)
        future_paths = []
        valid = True
        for state in outcomes:
            tail = bfs(grid, state, goal)
            if tail is None:
                valid = False
                break
            future_paths.append(tail)
        if not valid:
            continue
        worst_case = max(len(p) for p in future_paths)
        avg_case   = sum(len(p) for p in future_paths) / len(future_paths)
        step_cost  = _cost(grid, *intended)
        score = (worst_case, avg_case, step_cost, _manhattan(intended, goal))
        if best_score is None or score < best_score:
            best_score = score
            best_step = intended
    if best_step is not None:
        return best_step
    fallback = astar(grid, start, goal)
    return fallback[1] if fallback and len(fallback) > 1 else None

def and_or_sample_outcome(grid, start, intended):
    outcomes = _andor_side_outcomes(start, intended, grid)
    if len(outcomes) == 1:
        return outcomes[0]
    if random.random() < 0.8:
        return intended
    return random.choice(outcomes[1:])

def bfs(grid, start, goal):
    queue = deque([start])
    came  = {}
    visited = {start}
    while queue:
        cur = queue.popleft()
        if cur == goal:
            return _reconstruct(came, goal)
        for nb in _neighbors(*cur, grid):
            if nb not in visited:
                visited.add(nb)
                came[nb] = cur
                queue.append(nb)
    return None

def ucs(grid, start, goal):
    heap  = [(0, start)]
    came  = {}
    g     = {start: 0}
    while heap:
        cost, cur = heapq.heappop(heap)
        if cur == goal:
            return _reconstruct(came, goal)
        if cost > g.get(cur, float('inf')):
            continue
        for nb in _neighbors(*cur, grid):
            nc = cost + _cost(grid, *nb)
            if nc < g.get(nb, float('inf')):
                g[nb]    = nc
                came[nb] = cur
                heapq.heappush(heap, (nc, nb))
    return None

def astar(grid, start, goal):
    heap  = [(0, start)]
    came  = {}
    g     = {start: 0}
    while heap:
        _, cur = heapq.heappop(heap)
        if cur == goal:
            return _reconstruct(came, goal)
        for nb in _neighbors(*cur, grid):
            ng = g[cur] + _cost(grid, *nb)
            if ng < g.get(nb, float('inf')):
                g[nb]    = ng
                came[nb] = cur
                f        = ng + _manhattan(nb, goal)
                heapq.heappush(heap, (f, nb))
    return None

def greedy(grid, start, goal):
    heap  = [(_manhattan(start, goal), start)]
    came  = {}
    visited = {start}
    while heap:
        _, cur = heapq.heappop(heap)
        if cur == goal:
            return _reconstruct(came, goal)
        for nb in _neighbors(*cur, grid):
            if nb not in visited:
                visited.add(nb)
                came[nb] = cur
                heapq.heappush(heap, (_manhattan(nb, goal), nb))
    return None

def hill_climbing(grid, start, goal):
    cur = start
    path = [cur]
    visited = {cur}
    while cur != goal:
        nbs = [nb for nb in _neighbors(*cur, grid) if nb not in visited]
        if not nbs:
            break
        cur_h = _manhattan(cur, goal)
        nxt = min(nbs, key=lambda nb: (_manhattan(nb, goal), _cost(grid, *nb)))
        nxt_h = _manhattan(nxt, goal)
        if nxt_h >= cur_h:
            break
        cur = nxt
        visited.add(cur)
        path.append(cur)
        if len(path) > ROWS * COLS:
            break
    return path

def simulated_annealing(grid, start, goal):
    best_path = None
    best_score = float('inf')
    for _ in range(24):          
        cur   = start
        path  = [cur]
        visited = {cur}
        T     = 7.5
        alpha = 0.985
        while cur != goal and T > 0.05:
            nbs = [nb for nb in _neighbors(*cur, grid) if nb not in visited]
            if not nbs:
                break
            weighted = sorted(
                nbs,
                key=lambda nb: (_manhattan(nb, goal), _cost(grid, *nb))
            )
            top_k = weighted[:min(3, len(weighted))]
            nxt = random.choice(top_k if random.random() < 0.75 else weighted)
            cur_energy = _manhattan(cur, goal)
            nxt_energy = _manhattan(nxt, goal) + (_cost(grid, *nxt) - 1) * 0.7
            delta = nxt_energy - cur_energy
            if delta < 0 or random.random() < math.exp(-delta / T):
                cur = nxt
                visited.add(cur)
                path.append(cur)
            T *= alpha
            if len(path) > ROWS * COLS:
                break
        if cur == goal:
            score = _path_cost(grid, path)
            if best_path is None or score < best_score:
                best_path = path
                best_score = score
    return best_path if best_path else astar(grid, start, goal)

def no_observation(grid, start, goal):
    acts, _ = no_observation_plan(grid, goal)
    if acts is None:
        belief = init_belief_state(grid, center=start)
        cur = start
        path = [start]
        for _ in range(ROWS * COLS):
            if cur == goal:
                return path
            action, belief = no_observation_next_action(grid, belief, goal)
            if action is None:
                break
            cur = step_with_action(grid, cur, action)
            path.append(cur)
        return path
    path = [start]
    cur = start
    for action in acts:
        cur = step_with_action(grid, cur, action)
        path.append(cur)
    return path

def no_observation_plan(grid, goal, init_belief=None, max_iter=250):
    init_belief = frozenset(init_belief) if init_belief is not None else init_belief_state(grid)
    if not init_belief:
        return None, frozenset()
    def is_goal(belief):
        return all(pos == goal for pos in belief)
    if is_goal(init_belief):
        return [], init_belief
    queue   = deque([(init_belief, [])])
    visited = {init_belief}
    for _ in range(max_iter):
        if not queue:
            break
        belief, acts = queue.popleft()
        for action in NOOBS_ACTIONS:
            nb = apply_action_to_belief(grid, belief, action)
            if nb in visited:
                continue
            visited.add(nb)
            new_acts = acts + [action]
            if is_goal(nb):
                return new_acts, nb
            queue.append((nb, new_acts))
    return None, init_belief

def no_observation_next_action(grid, belief, goal):
    belief = frozenset(belief)
    if not belief:
        return None, belief
    best_action = None
    best_belief = belief
    best_score = None
    for action in NOOBS_ACTIONS:
        nb = apply_action_to_belief(grid, belief, action)
        dists = [_manhattan(pos, goal) for pos in nb]
        goal_hits = sum(1 for pos in nb if pos == goal)
        stagnant = 1 if nb == belief else 0
        score = (
            max(dists),
            sum(dists) / max(len(dists), 1),
            len(nb),
            stagnant,
            -goal_hits,
        )
        if best_score is None or score < best_score:
            best_score = score
            best_action = action
            best_belief = nb
    return best_action, best_belief

def and_or_search(grid, start, goal):
    return [start]

def backtracking_search(grid, start, goal):
    best = [None]
    def bt(path, visited):
        cur = path[-1]
        if cur == goal:
            if best[0] is None or len(path) < len(best[0]):
                best[0] = path[:]
            return
        if len(path) > ROWS * COLS:
            return
        nbs = sorted(_neighbors(*cur, grid),
                     key=lambda nb: _manhattan(nb, goal))
        for nb in nbs:
            if nb not in visited:
                visited.add(nb)
                path.append(nb)
                bt(path, visited)
                path.pop()
                visited.remove(nb)
                if best[0] and len(best[0]) < ROWS * COLS // 2:
                    return
    bt([start], {start})
    return best[0] if best[0] else astar(grid, start, goal)

def ac3_search(grid, start, goal):
    reachable_from_start = _reachable(grid, start)
    reachable_to_goal    = _reachable(grid, goal)
    valid = reachable_from_start & reachable_to_goal
    if goal not in valid:
        return None
    pruned = [row[:] for row in grid]
    for r in range(ROWS):
        for c in range(COLS):
            if (r, c) not in valid and grid[r][c] != WALL:
                pruned[r][c] = WALL 
    return astar(pruned, start, goal)

def _reachable(grid, src):
    visited = {src}
    queue   = deque([src])
    while queue:
        r, c = queue.popleft()
        for nb in _neighbors(r, c, grid):
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return visited

def _adv_neighbors(pos, grid, blocked):
    r, c = pos
    for nb in _neighbors(r, c, grid):
        if nb not in blocked:
            yield nb

def _adv_astar_path(grid, start, goal, blocked):
    if start in blocked or goal in blocked:
        return None
    overlay = [row[:] for row in grid]
    for r, c in blocked:
        if (r, c) != start and (r, c) != goal:
            overlay[r][c] = WALL
    return astar(overlay, start, goal)

def _adv_candidate_blocks(grid, pos, goal, blocked, visited, max_blocks=3):
    if len(blocked) >= max_blocks:
        return [None]
    candidates = []
    shortest = _adv_astar_path(grid, pos, goal, blocked) or []
    for tile in shortest[1:5]:
        if tile not in candidates:
            candidates.append(tile)
    for nb in _neighbors(*pos, grid):
        if nb not in candidates:
            candidates.append(nb)
    filtered = []
    for tile in candidates:
        if tile in (pos, goal):
            continue
        r, c = tile
        if grid[r][c] != EMPTY:   
            continue
        if tile in blocked:
            continue
        if tile in visited:
            continue
        if _adv_astar_path(grid, pos, goal, blocked | {tile}) is None:
            continue
        filtered.append(tile)
    return filtered + [None]

def _adv_evaluate(grid, pos, goal, blocked, visited, energy_left):
    if pos == goal:
        return 12_000 + energy_left * 140 - len(blocked) * 40
    if energy_left <= 0:
        return -12_000
    shortest = _adv_astar_path(grid, pos, goal, blocked)
    if shortest is None:
        return -12_000
    dist = len(shortest) - 1
    survival_margin = energy_left - dist
    mobility = len(list(_adv_neighbors(pos, grid, blocked)))
    fresh_moves = len([nb for nb in _adv_neighbors(pos, grid, blocked)
                       if nb not in visited])
    pressure = len([nb for nb in _neighbors(*pos, grid) if nb in blocked])
    return (
        survival_margin * 320
        - dist * 28
        + mobility * 18
        + fresh_moves * 16
        - pressure * 25
        - len(blocked) * 12
    )

def _adv_order_moves(grid, pos, goal, blocked, visited):
    route = _adv_astar_path(grid, pos, goal, blocked)
    if route and len(route) > 1:
        return [route[1]]
    moves = [nb for nb in _adv_neighbors(pos, grid, blocked) if nb not in visited]
    if not moves:
        moves = list(_adv_neighbors(pos, grid, blocked))
    return sorted(
        moves,
        key=lambda nb: (
            _manhattan(nb, goal),
            _cost(grid, *nb),
        )
    )

def _adv_order_blocks(grid, pos, goal, blocked, visited):
    blocks = _adv_candidate_blocks(grid, pos, goal, blocked, visited)
    def block_key(tile):
        if tile is None:
            return (999, 999)
        future = _adv_astar_path(grid, pos, goal, blocked | {tile})
        return (len(future) if future else 999, _manhattan(tile, goal))
    return sorted(blocks, key=block_key)

def minimax_search(grid, start, goal):
    DEPTH = 4
    def minimax_value(pos, depth, is_max, blocked, visited, energy_left):
        if pos == goal or depth == 0 or energy_left <= 0:
            return _adv_evaluate(grid, pos, goal, blocked, visited, energy_left)
        if is_max:
            moves = _adv_order_moves(grid, pos, goal, blocked, visited)
            if not moves:
                return _adv_evaluate(grid, pos, goal, blocked, visited, energy_left)
            best_val = -float('inf')
            for move in moves:
                val = minimax_value(move, depth - 1, False,
                                    blocked, visited | {move}, energy_left - 1)
                best_val = max(best_val, val)
            return best_val
        return minimax_value(pos, depth - 1, True, blocked, visited, energy_left)
    def choose_enemy_move(pos, blocked, visited, energy_left):
        moves = _adv_order_moves(grid, pos, goal, blocked, visited)
        if not moves:
            return None
        best_move = moves[0]
        best_val = -float('inf')
        for move in moves:
            val = minimax_value(move, DEPTH - 1, False, blocked, visited | {move}, energy_left - 1)
            if val > best_val:
                best_val = val
                best_move = move
        return best_move
    def choose_player_block(pos, blocked, visited, energy_left):
        blocks = _adv_order_blocks(grid, pos, goal, blocked, visited)
        best_block = None
        best_val = float('inf')
        for block in blocks:
            new_blocked = blocked | ({block} if block is not None else set())
            val = minimax_value(pos, DEPTH - 1, True, new_blocked, visited, energy_left)
            if val < best_val:
                best_val = val
                best_block = block
        return best_block
    path = [start]
    cur = start
    blocked = set()
    visited = {start}
    energy_left = ADVERSARIAL_TURN_ENERGY
    for _ in range(ROWS * COLS):
        if cur == goal:
            return path
        nxt = choose_enemy_move(cur, blocked, visited, energy_left)
        if nxt is None:
            break
        path.append(nxt)
        cur = nxt
        visited.add(cur)
        energy_left -= 1
        if cur == goal:
            return path
    return path if cur == goal else astar(grid, start, goal)

def alpha_beta_search(grid, start, goal):
    DEPTH = 6
    def ab_value(pos, depth, is_max, blocked, visited, energy_left, alpha, beta):
        if pos == goal or depth == 0 or energy_left <= 0:
            return _adv_evaluate(grid, pos, goal, blocked, visited, energy_left)
        if is_max:
            moves = _adv_order_moves(grid, pos, goal, blocked, visited)
            if not moves:
                return _adv_evaluate(grid, pos, goal, blocked, visited, energy_left)
            val = -float('inf')
            for move in moves:
                val = max(
                    val,
                    ab_value(move, depth - 1, False, blocked,
                             visited | {move}, energy_left - 1, alpha, beta)
                )
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            return val
        return ab_value(pos, depth - 1, True, blocked, visited, energy_left, alpha, beta)
    def choose_enemy_move(pos, blocked, visited, energy_left):
        moves = _adv_order_moves(grid, pos, goal, blocked, visited)
        if not moves:
            return None
        best_move = moves[0]
        best_val = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        for move in moves:
            val = ab_value(move, DEPTH - 1, False, blocked,
                           visited | {move}, energy_left - 1, alpha, beta)
            if val > best_val:
                best_val = val
                best_move = move
            alpha = max(alpha, best_val)
        return best_move
    def choose_player_block(pos, blocked, visited, energy_left):
        blocks = _adv_order_blocks(grid, pos, goal, blocked, visited)
        best_block = None
        best_val = float('inf')
        alpha = -float('inf')
        beta = float('inf')
        for block in blocks:
            new_blocked = blocked | ({block} if block is not None else set())
            val = ab_value(pos, DEPTH - 1, True, new_blocked, visited, energy_left, alpha, beta)
            if val < best_val:
                best_val = val
                best_block = block
            beta = min(beta, best_val)
        return best_block
    path = [start]
    cur = start
    blocked = set()
    visited = {start}
    energy_left = ADVERSARIAL_TURN_ENERGY
    for _ in range(ROWS * COLS):
        if cur == goal:
            return path
        nxt = choose_enemy_move(cur, blocked, visited, energy_left)
        if nxt is None:
            break
        path.append(nxt)
        cur = nxt
        visited.add(cur)
        energy_left -= 1
        if cur == goal:
            return path
    return path if cur == goal else astar(grid, start, goal)

ALGO_FUNCS = {
    "BFS":             bfs,
    "UCS":             ucs,
    "A*":              astar,
    "Greedy":          greedy,
    "Hill Climbing":   hill_climbing,
    "Sim. Annealing":  simulated_annealing,
    "No Observation":  no_observation,
    "AND-OR":          and_or_search,
    "Backtracking":    backtracking_search,
    "AC-3":            ac3_search,
    "Minimax":         minimax_search,
    "Alpha-Beta":      alpha_beta_search,
}
