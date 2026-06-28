TILE_SIZE   = 36
COLS        = 26
ROWS        = 16
PANEL_W     = 300

SCREEN_W    = COLS * TILE_SIZE + PANEL_W
SCREEN_H    = ROWS * TILE_SIZE

FPS         = 60
ENEMY_SPAWN_INTERVAL = 90  

NOOBS_INITIAL_BELIEF_RADIUS = 3
VISUAL_ENEMY_SPEED          = 0.9
VISUAL_BOSS_SPEED           = 0.55

ENEMY_ENERGY            = 135.0
BOSS_ENERGY             = 205.0
ENERGY_DRAIN_PER_FRAME  = 0.11
ADVERSARIAL_TURN_ENERGY = 30

EMPTY    = 0
WALL     = 1
SPAWN    = 2
GOAL     = 3

C_BG         = (24,  26,  34)
C_EMPTY      = (55,  55,  70)
C_WALL       = (90,  80, 110)
C_SPAWN      = (74, 170, 255)
C_GOAL       = (130, 140, 160)
C_GRID       = (34,  36,  50)
C_PANEL      = (18,  20,  30)
C_WHITE      = (240, 240, 240)
C_GRAY       = (140, 140, 160)
C_ACCENT     = (100, 170, 255)
C_ENEMY      = (215, 218, 228)
C_ENEMY2     = (255, 215, 120)
C_TOWER      = (110, 150, 210)
C_BULLET     = (195, 140, 70)
C_WOOD       = (128, 86, 48)
C_HEATMAP_HI = (220,  60,  60)
C_HEATMAP_LO = ( 40, 100, 200)
C_BELIEF     = (180, 100, 255)
C_ENERGY     = (100, 210, 255)

TILE_COST = {
    EMPTY:  1,
    SPAWN:  1,
    GOAL:   1,
    WALL:   999,
}

def _parse_map(rows):
    legend = {"#": WALL, ".": EMPTY, "S": SPAWN, "G": GOAL}
    parsed = [[legend[ch] for ch in row] for row in rows]
    assert len(parsed) == ROWS and all(len(row) == COLS for row in parsed)
    return parsed


LEVEL1_MAP = _parse_map([
    "##########################",
    "#S.....##........##......#",
    "#......##........##......#",
    "#......#####..#####......#",
    "###....................###",
    "###..######....######..###",
    "#........##....##........#",
    "#........##....##........#",
    "#..########....########..#",
    "#..##................##..#",
    "#..##..######..######....#",
    "#......##........##......#",
    "#......##........##......#",
    "#......................G.#",
    "#........................#",
    "##########################",
])

LEVEL2_MAP = _parse_map([
    "##########################",
    "####....##........##....G#",
    "###.....##........##.....#",
    "##..########..########..##",
    "#....##..............##..#",
    "#....##..##########..##..#",
    "#..........######........#",
    "###..##....######....##..#",
    "#....##..............##..#",
    "#....########..########..#",
    "#..............##........#",
    "#..##########..##..####..#",
    "#..##..............##....#",
    "#S.##..##############....#",
    "#........................#",
    "##########################",
])

LEVEL3_MAP = _parse_map([
    "##########################",
    "#S...######......######..#",
    "#....##..............##..#",
    "###..##..##########..##..#",
    "#....##..##......##..##..#",
    "#........##.####.##......#",
    "#..########.####.######..#",
    "#..##................##..#",
    "#..##..######..######....#",
    "#......##..........##....#",
    "####...##..######..##..###",
    "#......##..##..##..##....#",
    "#..##########..########..#",
    "#..............##........#",
    "#..##############..###.G.#",
    "##########################",
])

LEVELS = [
    {
        "id": 0,
        "name": "Đồng Cỏ",
        "subtitle": "Meadow Trail",
        "map": LEVEL1_MAP,
        "difficulty": "Dễ",
        "theme_bg":    (126, 208,  96),
        "theme_path":  (226, 190, 146),
        "theme_wall":  (42, 138,  72),
        "theme_deco":  (82, 168,  88),
        "waves_to_win": 8,
        "lives": 25,
        "spawn_interval": 95,
        "energy_mult": 1.12,
    },
    {
        "id": 1,
        "name": "Sa Mạc",
        "subtitle": "Desert Dunes",
        "map": LEVEL2_MAP,
        "difficulty": "Trung bình",
        "theme_bg":    (188, 170, 104),
        "theme_path":  (230, 198, 152),
        "theme_wall":  (110, 124,  62),
        "theme_deco":  (164, 154,  86),
        "waves_to_win": 12,
        "lives": 20,
        "spawn_interval": 80,
        "energy_mult": 1.0,
    },
    {
        "id": 2,
        "name": "Băng Tuyết",
        "subtitle": "Frostlands",
        "map": LEVEL3_MAP,
        "difficulty": "Khó",
        "theme_bg":    (156, 196, 210),
        "theme_path":  (232, 236, 240),
        "theme_wall":  (88, 132, 154),
        "theme_deco":  (128, 170, 188),
        "waves_to_win": 16,
        "lives": 15,
        "spawn_interval": 65,
        "energy_mult": 0.92,
    },
]

DEFAULT_MAP = LEVEL1_MAP

ALGORITHMS = [
    ("BFS",               "Uninformed"),
    ("UCS",               "Uninformed"),
    ("A*",                "Informed"),
    ("Greedy",            "Informed"),
    ("Hill Climbing",     "Local"),
    ("Sim. Annealing",    "Local"),
    ("No Observation",    "Complex"),
    ("AND-OR",            "Complex"),
    ("Backtracking",      "CSP"),
    ("AC-3",              "CSP"),
    ("Minimax",           "Adversarial"),
    ("Alpha-Beta",        "Adversarial"),
]

GROUP_COLORS = {
    "Uninformed":  (100, 160, 255),
    "Informed":    (160, 100, 255),
    "Local":       ( 60, 200, 160),
    "Complex":     (220, 160,  40),
    "CSP":         (220,  80,  80),
    "Adversarial": (200,  80, 180),
}
