# Tower Defense — AI Path of Legends

Một game **Tower Defense** viết bằng Python + Pygame, nhưng thay vì tháp bắn quái, người chơi đặt **vật cản (chướng ngại vật)** để buộc quái phải đi đường vòng. Điểm đặc biệt: mỗi con quái di chuyển theo **một trong 12 thuật toán tìm đường AI** khác nhau (BFS, A*, Minimax, AC-3, Simulated Annealing...), cho phép người chơi trực quan hoá và so sánh cách các thuật toán AI kinh điển phản ứng với cùng một mê cung.

Giao diện game bằng tiếng Việt (menu, panel, thông báo thắng/thua).

---

## Mục lục

1. [Ý tưởng cốt lõi](#ý-tưởng-cốt-lõi)
2. [Tính năng](#tính-năng)
3. [Yêu cầu & Cài đặt](#yêu-cầu--cài-đặt)
4. [Cách chạy](#cách-chạy)
5. [Cách chơi & Điều khiển](#cách-chơi--điều-khiển)
6. [12 thuật toán AI](#12-thuật-toán-ai)
7. [Cơ chế trò chơi chi tiết](#cơ-chế-trò-chơi-chi-tiết)
8. [Các màn chơi (Levels)](#các-màn-chơi-levels)
9. [Cấu trúc mã nguồn](#cấu-trúc-mã-nguồn)
10. [Chi tiết từng module](#chi-tiết-từng-module)

---

## Ý tưởng cốt lõi

- Người chơi **đặt "vật cản"** (biểu tượng gỗ chéo hình chữ X) lên các ô trống trên bản đồ.
- Vật cản **không tấn công** — chức năng duy nhất là biến ô đó thành tường (`WALL`), buộc quái phải **tính lại đường đi**.
- Quái vẫn tự mất máu (năng lượng) dần theo thời gian, nên việc **kéo dài quãng đường** quái phải đi (bằng mê cung vật cản) chính là "vũ khí" duy nhất của người chơi.
- Mỗi đợt (wave) quái đi theo **thuật toán AI mà người chơi chọn trước khi bấm Enter để spawn**, giúp so sánh trực quan: BFS đi đường ngắn nhất theo số bước, Hill Climbing dễ bị kẹt cục bộ, Minimax/Alpha-Beta "né" vật cản một cách có chiến lược, v.v.

---

## Tính năng

- 🎮 Menu chính, màn hình chọn cấp độ, panel thông tin bên phải theo thời gian thực.
- 🗺️ 3 bản đồ (level) với theme màu riêng: Đồng Cỏ, Sa Mạc, Băng Tuyết.
- 🧠 12 thuật toán AI tìm đường/định hướng khác nhau, chia theo 6 nhóm theo chương trình học AI cổ điển (Uninformed, Informed, Local Search, Complex/POMDP-like, CSP, Adversarial).
- 🔥 Heatmap khoảng cách BFS từ mọi ô tới đích (bật/tắt bằng phím `H`).
- 🧭 Hiển thị đường đi hiện tại của quái (bật/tắt bằng phím `P`).
- ⚡ Hệ thống năng lượng (energy) cho quái: quái tự "kiệt sức" nếu đi đường quá dài/quá lâu.
- 🧩 Đặt/gỡ vật cản với kiểm tra hợp lệ bằng BFS (không cho chặn kín đường đi).
- 👑 Boss xuất hiện định kỳ (mỗi con thứ 5 trong wave) với năng lượng và kích thước lớn hơn.
- ⏸️ Tạm dừng, phục hồi (Retry), chuyển màn khi thắng.
- 🎨 Toàn bộ đồ hoạ vẽ bằng `pygame.draw` thủ công (không dùng file ảnh/sprite ngoài) — cổng, lâu đài, cây, quái xương, vật cản gỗ đều là hình học vector.

---

## Yêu cầu & Cài đặt

### Yêu cầu
- Python 3.10 trở lên (đã kiểm tra tương thích với bytecode cache cho cả 3.10 và 3.12)
- Thư viện [`pygame`](https://www.pygame.org/)

### Cài đặt

```bash
# (Khuyến nghị) tạo virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Cài pygame
pip install pygame
```

> Dự án chưa có sẵn file `requirements.txt`. Bạn có thể tự tạo bằng:
> ```bash
> echo "pygame" > requirements.txt
> ```

---

## Cách chạy

Chạy trực tiếp từ thư mục gốc của dự án:

```bash
cd tower_defense
python3 main.py
```

Cửa sổ game sẽ mở với kích thước `COLS * TILE_SIZE + PANEL_W` × `ROWS * TILE_SIZE` = **1236 × 576** pixel (26 cột, 16 hàng, tile 36px, panel thông tin rộng 300px).

---

## Cách chơi & Điều khiển

### Màn hình chính (Main Menu)
| Phím / Chuột | Hành động |
|---|---|
| `Enter` hoặc `N` | Bắt đầu ván mới ở Level 1 |
| `L` hoặc `Space` | Vào màn hình chọn Level |
| `X`, `Q` hoặc `Esc` | Thoát game |
| Click chuột vào nút | Tương ứng với hành động trên |

### Màn hình chọn Level
| Phím / Chuột | Hành động |
|---|---|
| `1` / `2` / `3` | Chọn nhanh Level 1/2/3 |
| `Esc` | Quay lại Main Menu |
| Click vào thẻ level | Vào chơi level đó |

### Trong khi chơi (Playing)
| Phím | Hành động |
|---|---|
| `Enter` | Cho quái tiếp theo xuất hiện (spawn) theo thuật toán đang chọn |
| `↑` / `↓` | Duyệt qua danh sách 12 thuật toán |
| `1`-`9`, `0`, `-`, `=` | Chọn nhanh thuật toán số 1–12 |
| `Space` | Tạm dừng / tiếp tục |
| `H` | Bật/tắt hiển thị heatmap khoảng cách tới đích |
| `P` | Bật/tắt hiển thị đường đi của quái |
| `R` | Chơi lại level hiện tại (reset) |
| `Esc` | Quay lại màn hình chọn Level |
| Click chuột trái vào ô trống | Đặt vật cản (nếu không chặn kín đường) |
| Click chuột phải vào vật cản | Gỡ vật cản |

**Lưu ý:** chỉ có thể spawn quái mới khi **không còn quái nào đang sống** trên bản đồ (xem `spawn_enemy()` trong `game_state.py`) — nghĩa là chế độ chơi hiện tại là "từng con một", không phải spawn theo wave tự động liên tục.

---

## 12 thuật toán AI

Định nghĩa tại `config.py` (`ALGORITHMS`), cài đặt tại `algorithms/pathfinding.py` (`ALGO_FUNCS`). Mỗi thuật toán được gắn màu nhóm riêng để hiển thị trên panel (`GROUP_COLORS`):

| # | Thuật toán | Nhóm | Mô tả ngắn |
|---|---|---|---|
| 1 | **BFS** (Breadth-First Search) | Uninformed | Duyệt theo lớp, đảm bảo đường đi ít bước nhất (không tính trọng số). |
| 2 | **UCS** (Uniform-Cost Search) | Uninformed | Dijkstra cơ bản, chọn theo tổng chi phí thấp nhất (dùng `TILE_COST`). |
| 3 | **A\*** | Informed | UCS + heuristic Manhattan để tìm đường tối ưu nhanh hơn. |
| 4 | **Greedy Best-First** | Informed | Chỉ dùng heuristic Manhattan, không quan tâm chi phí đã đi — nhanh nhưng không tối ưu. |
| 5 | **Hill Climbing** | Local Search | Luôn chọn ô hàng xóm gần đích hơn hiện tại; dừng lại (kẹt) nếu không có ô nào tốt hơn — dễ bị "stuck" ở cực tiểu địa phương. |
| 6 | **Simulated Annealing** | Local Search | Thử 24 lần chạy ngẫu nhiên có kiểm soát nhiệt độ (`T`, hệ số nguội `alpha=0.985`), có xác suất chấp nhận bước "tệ hơn" để thoát cực trị địa phương, rồi chọn kết quả tốt nhất. |
| 7 | **No Observation** (tìm kiếm không quan sát / belief-state search) | Complex | Quái không biết chính xác vị trí của mình (duy trì một **belief state** — tập hợp các vị trí khả dĩ trong phạm vi bán kính 3 ô), tìm chuỗi hành động đưa *toàn bộ* belief state hội tụ về đích, giống bài toán "sensorless problem" trong AI. |
| 8 | **AND-OR Search** | Complex | Xử lý môi trường không tất định: khi đi theo hướng dự định có thể "trượt" (slip) sang ô bên cạnh; thuật toán chọn bước đi tối ưu hoá trường hợp xấu nhất (worst-case) trong số các kết quả có thể xảy ra. |
| 9 | **Backtracking** | CSP | Duyệt đệ quy toàn bộ các đường đi khả dĩ (có nhánh cụt/quay lui), ưu tiên nhánh gần đích hơn, chọn đường ngắn nhất tìm được. |
| 10 | **AC-3** (Arc Consistency 3) | CSP | Thu hẹp miền giá trị hợp lệ bằng cách chỉ giữ lại các ô vừa **liên thông với điểm xuất phát** vừa **liên thông với đích** (giao của hai tập BFS reachability), sau đó chạy A\* trên bản đồ đã "prune". |
| 11 | **Minimax** | Adversarial | Mô phỏng trò chơi 2 người: quái (max) cố đi tới đích trong khi "đối thủ ảo" (min) chọn cách đặt tối đa 3 vật cản để cản đường; tìm kiếm độ sâu 4, dùng hàm lượng giá `_adv_evaluate` (dựa trên năng lượng còn lại, khoảng cách, độ linh hoạt di chuyển...). |
| 12 | **Alpha-Beta Pruning** | Adversarial | Giống Minimax nhưng cắt tỉa nhánh bằng alpha-beta, độ sâu tìm kiếm 6 (sâu hơn Minimax nhờ cắt tỉa hiệu quả hơn). |

### Cơ chế đặc biệt theo từng nhóm thuật toán

- **AND-OR & No Observation**: đây là 2 thuật toán duy nhất khiến quái **đi lại (replan) từng bước một** trong lúc di chuyển thực tế (xem `Enemy._advance_and_or` và `Enemy._advance_no_observation` trong `core/entities.py`), thay vì tính sẵn toàn bộ đường đi một lần như các thuật toán còn lại. Vì vậy 2 loại quái này chạy chậm hơn về mặt hoạt ảnh (`VISUAL_ENEMY_SPEED`/`VISUAL_BOSS_SPEED`) so với các thuật toán khác (tốc độ `1.48`/`0.84`).
- **AND-OR**: có xác suất 80% đi đúng hướng dự định, 20% "trượt" sang ô vuông góc (`and_or_sample_outcome`), hiển thị chữ "SLIP" phía trên đầu quái khi trượt.
- **No Observation**: quái duy trì một tập `belief_state` (các ô có thể đang đứng), hiển thị trên panel; khi bị chặn đường sẽ tính lại kế hoạch hành động mới từ belief state hiện tại.
- **Hill Climbing**: nếu quái bị "stuck" (kẹt tại cực tiểu địa phương), nó sẽ đứng yên tại chỗ mãi mãi cho tới khi hết năng lượng — đây là hành vi minh hoạ nhược điểm kinh điển của thuật toán leo đồi.

---

## Cơ chế trò chơi chi tiết

### Bản đồ & Ô
- Lưới `ROWS=16 × COLS=26`, mỗi ô `TILE_SIZE=36px`.
- 4 loại ô: `EMPTY` (trống, đặt được vật cản), `WALL` (tường cố định của bản đồ), `SPAWN` (điểm quái xuất hiện, ký hiệu `S`), `GOAL` (đích, ký hiệu `G`).
- Bản đồ được định nghĩa bằng ASCII-art trong `config.py` qua hàm `_parse_map` (`#`=tường, `.`=trống, `S`=spawn, `G`=goal).

### Vật cản (Tower)
- Đặt bằng chuột trái vào ô trống; hệ thống sẽ **tạm đặt tường rồi chạy BFS kiểm tra** xem đường từ spawn đến goal còn tồn tại không — nếu bị chặn kín, việc đặt sẽ bị huỷ (không cho bí đường quái hoàn toàn).
- Gỡ bằng chuột phải, trả ô về loại gốc trong `base_grid`.
- Vật cản **không gây sát thương**, không có phạm vi/tầm bắn — thuần tuý là chướng ngại hình học.
- Sau mỗi lần đặt/gỡ, heatmap khoảng cách được tính lại (`_compute_heatmap`, BFS ngược từ goal).

### Enemy (Quái)
- Mỗi quái mang theo: đường đi (`path`), thuật toán đang dùng, cờ boss, năng lượng, belief state (nếu có).
- Năng lượng khởi điểm: `ENEMY_ENERGY=135` (quái thường) hoặc `BOSS_ENERGY=205` (boss), nhân thêm hệ số `energy_mult` theo từng level.
- Mỗi frame mất `ENERGY_DRAIN_PER_FRAME=0.11` năng lượng — quái chết (hết máu) nếu năng lượng về 0 trước khi tới đích.
- Boss xuất hiện ở **quái thứ 5, 10, 15...** trong wave (`total_spawned % 5 == 4`), to hơn, chậm hơn, nhiều năng lượng hơn.
- Nếu đường đi phía trước bị chặn bởi vật cản mới đặt, quái sẽ **tính lại đường** bằng chính thuật toán ban đầu của nó (`ALGO_FUNCS[self.algo_name]`), hoặc fallback sang BFS nếu không tìm được đường.
- Quái tới đích (`reached=True`) sẽ trừ 1 mạng (`lives`) của người chơi.

### Điểm số & Thắng/Thua
- Tiêu diệt 1 quái (hết năng lượng giữa đường): +10 điểm.
- Thua (`game_over=True`) khi `lives <= 0`.
- Thắng level (`win=True`) khi đã spawn đủ `waves_to_win` quái **và** không còn quái nào sống trên bản đồ.
- Màn thắng cuối cùng (level 3) hiển thị thông báo hoàn thành toàn bộ game.

### Heatmap
- `H` để bật/tắt — hiển thị khoảng cách BFS (tính bằng số bước) từ mỗi ô còn đi được tới đích, tô màu gradient từ `C_HEATMAP_LO` (xanh, gần) đến `C_HEATMAP_HI` (đỏ, xa).

---

## Các màn chơi (Levels)

| Level | Tên | Độ khó | Waves để thắng | Mạng (lives) | Spawn interval | Hệ số năng lượng |
|---|---|---|---|---|---|---|
| 1 | **Đồng Cỏ** (Meadow Trail) | Dễ | 8 | 25 | 95 | 1.12 |
| 2 | **Sa Mạc** (Desert Dunes) | Trung bình | 12 | 20 | 80 | 1.00 |
| 3 | **Băng Tuyết** (Frostlands) | Khó | 16 | 15 | 65 | 0.92 |

Mỗi level có bảng màu theme riêng (`theme_bg`, `theme_path`, `theme_wall`, `theme_deco`) dùng khi vẽ bản đồ, tạo cảm giác đồng cỏ xanh / sa mạc vàng / băng tuyết trắng xanh khác biệt. Bản đồ được vẽ thủ công bằng ASCII trong `config.py`, mỗi bản đồ có cấu trúc mê cung riêng để test hành vi thuật toán ở độ phức tạp tăng dần.

> Lưu ý: các biến `spawn_interval`/`ENEMY_SPAWN_INTERVAL` được định nghĩa trong config nhưng việc spawn quái trong `main.py` hiện được kích hoạt **thủ công bằng phím Enter**, không tự động đếm giờ.

---

## Cấu trúc mã nguồn

```
tower_defense/
├── main.py                    # Điểm khởi chạy: vòng lặp game, xử lý input, state machine (menu/level-select/playing)
├── config.py                  # Hằng số cấu hình: kích thước, màu sắc, bản đồ 3 level, danh sách 12 thuật toán
├── algorithms/
│   ├── __init__.py
│   └── pathfinding.py         # Toàn bộ cài đặt 12 thuật toán tìm đường/định hướng AI
├── core/
│   ├── __init__.py
│   ├── entities.py            # Lớp Enemy (quái) và Tower (vật cản), logic di chuyển & vẽ
│   └── game_state.py          # Lớp GameState: quản lý toàn bộ trạng thái ván chơi (grid, towers, enemies, điểm, thắng/thua)
└── ui/
    ├── __init__.py
    └── renderer.py            # Toàn bộ logic vẽ: menu, chọn level, bản đồ, panel, hiệu ứng, màn thắng/thua
```

---

## Chi tiết từng module

### `config.py`
- Định nghĩa toàn bộ hằng số kích thước màn hình, tile, FPS.
- Bảng màu (`C_*`) dùng xuyên suốt UI.
- `TILE_COST`: chi phí di chuyển qua từng loại ô (dùng cho UCS/A*); tường có chi phí `999` (coi như không đi được).
- `_parse_map()`: chuyển ASCII-art thành ma trận số, có `assert` kiểm tra đúng kích thước `ROWS × COLS`.
- 3 bản đồ (`LEVEL1_MAP`, `LEVEL2_MAP`, `LEVEL3_MAP`) và danh sách `LEVELS` (metadata từng level).
- `ALGORITHMS`: danh sách 12 tuple `(tên, nhóm)` theo đúng thứ tự phím tắt 1-9,0,-,=.
- `GROUP_COLORS`: màu cho từng nhóm thuật toán (6 nhóm).

### `algorithms/pathfinding.py`
- Các hàm tiện ích chung: `_neighbors`, `_cost`, `_reconstruct`, `_manhattan`, `_path_cost`.
- Cài đặt riêng biệt cho từng thuật toán: `bfs`, `ucs`, `astar`, `greedy`, `hill_climbing`, `simulated_annealing`.
- Nhóm "Complex" (không tất định/không quan sát):
  - `init_belief_state`, `apply_action_to_belief`, `no_observation_plan`, `no_observation_next_action`, `no_observation` — tìm kiếm trong không gian belief-state (tập hợp vị trí khả dĩ), dùng BFS trên đồ thị belief state để tìm chuỗi hành động đưa toàn bộ belief về đích.
  - `and_or_next_step`, `and_or_sample_outcome`, `_andor_side_outcomes`, `and_or_search` — tìm kiếm AND-OR cho môi trường không tất định (có xác suất trượt hướng).
- Nhóm CSP: `backtracking_search` (quay lui đệ quy), `ac3_search` + `_reachable` (rút gọn miền giá trị bằng giao 2 tập liên thông rồi chạy A*).
- Nhóm Adversarial: `minimax_search`, `alpha_beta_search`, cùng các hàm phụ trợ `_adv_neighbors`, `_adv_astar_path`, `_adv_candidate_blocks`, `_adv_evaluate` (hàm lượng giá trạng thái), `_adv_order_moves`, `_adv_order_blocks` (sắp xếp/heuristic-order để tìm kiếm hiệu quả hơn).
- `ALGO_FUNCS`: dict ánh xạ tên thuật toán → hàm cài đặt, được `GameState`/`Enemy` gọi động theo lựa chọn của người chơi.

### `core/entities.py`
- **`Enemy`**:
  - Khởi tạo theo `path` đã tính sẵn (trừ AND-OR/No-Observation khởi tạo path rỗng và tính dần).
  - `update()`: xử lý di chuyển mượt giữa 2 tile (nội suy tuyến tính theo `speed`), trừ năng lượng theo frame, phát hiện chết/tới đích, và **replanning** khi gặp vật cản mới.
  - `_advance_and_or()` / `_advance_no_observation()`: logic tính từng bước tiếp theo riêng cho 2 thuật toán "phức tạp".
  - `hit()`: giảm năng lượng (dự phòng cho cơ chế tháp gây sát thương trong tương lai — hiện không có tower nào gọi hàm này).
  - `draw()`: vẽ hình quái xương (skeleton) thủ công bằng các đường thẳng/hình tròn/đa giác `pygame.draw`, thanh năng lượng phía trên đầu, nhãn tên thuật toán rút gọn, hiệu ứng "SLIP".
- **`Tower`**: đối tượng đơn giản, chỉ lưu vị trí và vẽ biểu tượng gỗ chéo (X) — `update()` hiện không làm gì (`return None`), xác nhận triết lý "vật cản không tấn công".

### `core/game_state.py`
- **`GameState`**: trung tâm điều phối:
  - Khởi tạo grid từ level, tìm ô `SPAWN`/`GOAL`, tính heatmap ban đầu.
  - `place_tower()` / `remove_tower()`: đặt/gỡ vật cản kèm kiểm tra hợp lệ bằng BFS.
  - `spawn_enemy()`: tạo `Enemy` mới theo thuật toán đang chọn (`selected_algo`), xử lý logic khởi tạo đặc biệt cho AND-OR (path rỗng, tính dần) và No Observation (tính belief state + kế hoạch hành động ban đầu).
  - `select_algo()`/`next_algo()`/`prev_algo()`: điều hướng danh sách 12 thuật toán.
  - `update()`: vòng lặp cập nhật mỗi frame — di chuyển quái, trừ mạng khi quái tới đích, kiểm tra game over, cộng điểm khi quái chết, kiểm tra điều kiện thắng.
  - `toggle_heatmap()`, `toggle_paths()`, `toggle_pause()`: các cờ hiển thị/trạng thái.

### `ui/renderer.py` (531 dòng — module lớn nhất)
- Khởi tạo các font (`consolas` với nhiều cỡ chữ).
- Vẽ Main Menu (`draw_main_menu`, `main_menu_button_at`) và Level Select (`draw_level_select`, `level_card_at`, `_draw_map_thumbnail`) — mỗi level có thumbnail thu nhỏ của bản đồ thật.
- Vẽ bản đồ chi tiết theo theme (`draw_map`, `_draw_grass_tile`, `_draw_road_tile`, `_draw_connected_blob` — thuật toán nối các ô đường liền mạch kiểu autotile, `_draw_tree_tile`, `_draw_spawn_portal` — cổng dịch chuyển xanh, `_draw_goal_castle` — lâu đài đích).
- Vẽ thực thể (`draw_entities`), đường đi hiện tại của quái (`_draw_fancy_path`), belief state (`_draw_belief_state`), các gợi ý runtime khác (`_draw_runtime_cues` — ví dụ mũi tên hướng dự định).
- Vẽ panel thông tin bên phải (`draw_panel`): tên level, trạng thái quái dẫn đầu (năng lượng, ý định, belief state), danh sách 12 thuật toán với phím tắt và màu nhóm, chú thích vật cản.
- Màn hình phụ: `draw_game_over`, `draw_paused`, `draw_win` cùng các hàm dò vị trí nút bấm tương ứng (`gameover_button_at`, `win_button_at`).
- Các hàm tiện ích vẽ: `_draw_button`, `draw_hover` (highlight ô đang trỏ chuột, xanh nếu đặt được/đỏ nếu không), `_draw_menu_illustration`, `_draw_gradient_background`, `_text`, `_center_text`, `_hline`, cùng các hàm module-level `_tile_center`, `_draw_arrow`, `_lerp_color`, `_hp_color`.

---
