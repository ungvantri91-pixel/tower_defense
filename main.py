import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from config import *
from core.game_state import GameState
from ui.renderer     import Renderer

STATE_MAIN_MENU    = "main_menu"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING      = "playing"

def get_tile(mx, my):
    if mx >= COLS * TILE_SIZE:
        return -1, -1
    return my // TILE_SIZE, mx // TILE_SIZE

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Tower Defense — 12 AI Algorithms")
    clock    = pygame.time.Clock()
    renderer = Renderer(screen)
    app_state   = STATE_MAIN_MENU
    gs          = None
    hover_row, hover_col = -1, -1
    menu_hover  = None
    level_hover = -1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if app_state == STATE_MAIN_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    elif event.key in (pygame.K_RETURN, pygame.K_n):
                        gs = GameState(0)
                        app_state = STATE_PLAYING
                    elif event.key in (pygame.K_l, pygame.K_SPACE):
                        app_state = STATE_LEVEL_SELECT
                    elif event.key in (pygame.K_x, pygame.K_q):
                        pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    menu_hover = renderer.main_menu_button_at(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = renderer.main_menu_button_at(event.pos)
                    if action == "new_game":
                        gs = GameState(0)
                        app_state = STATE_PLAYING
                    elif action == "level":
                        app_state = STATE_LEVEL_SELECT
                    elif action == "exit":
                        pygame.quit(); sys.exit()
            elif app_state == STATE_LEVEL_SELECT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        app_state = STATE_MAIN_MENU
                    elif pygame.K_1 <= event.key <= pygame.K_3:
                        idx = event.key - pygame.K_1
                        if idx < len(LEVELS):
                            gs = GameState(idx)
                            app_state = STATE_PLAYING
                if event.type == pygame.MOUSEMOTION:
                    level_hover = renderer.level_card_at(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    idx = renderer.level_card_at(event.pos)
                    if idx is not None and idx < len(LEVELS):
                        gs = GameState(idx)
                        app_state = STATE_PLAYING
            elif app_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        gs = GameState(gs.level_index)
                    elif event.key == pygame.K_h:
                        gs.toggle_heatmap()
                    elif event.key == pygame.K_p:
                        gs.toggle_paths()
                    elif event.key == pygame.K_SPACE:
                        gs.toggle_pause()
                    elif event.key == pygame.K_ESCAPE:
                        app_state = STATE_LEVEL_SELECT
                    elif event.key == pygame.K_RETURN:
                        if not gs.game_over and not gs.win and not gs.paused:
                            gs.spawn_enemy()
                    elif event.key == pygame.K_UP:
                        gs.prev_algo()
                    elif event.key == pygame.K_DOWN:
                        gs.next_algo()
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        gs.select_algo(event.key - pygame.K_1)
                    elif event.key == pygame.K_0:
                        gs.select_algo(9)
                    elif event.key == pygame.K_MINUS:
                        gs.select_algo(10)
                    elif event.key == pygame.K_EQUALS:
                        gs.select_algo(11)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if gs.win:
                        action = renderer.win_button_at(event.pos)
                        if action == "next" and gs.level_index + 1 < len(LEVELS):
                            gs = GameState(gs.level_index + 1)
                        elif action == "levels":
                            app_state = STATE_LEVEL_SELECT
                        elif action == "retry":
                            gs = GameState(gs.level_index)
                    elif gs.game_over:
                        action = renderer.gameover_button_at(event.pos)
                        if action == "retry":
                            gs = GameState(gs.level_index)
                        elif action == "levels":
                            app_state = STATE_LEVEL_SELECT
                    else:
                        row, col = get_tile(mx, my)
                        if row >= 0:
                            if event.button == 1:
                                gs.place_tower(row, col)
                            elif event.button == 3:
                                gs.remove_tower(row, col)
                if event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    hover_row, hover_col = get_tile(mx, my)
        if app_state == STATE_MAIN_MENU:
            screen.fill(C_BG)
            renderer.draw_main_menu(menu_hover)
        elif app_state == STATE_LEVEL_SELECT:
            screen.fill(C_BG)
            renderer.draw_level_select(level_hover)
        elif app_state == STATE_PLAYING:
            gs.update()
            screen.fill(C_BG)
            renderer.draw_map(gs)
            renderer.draw_entities(gs)
            renderer.draw_panel(gs)
            if hover_row >= 0 and not gs.game_over and not gs.win:
                can_place = (
                    gs.grid[hover_row][hover_col] == EMPTY
                    and not any(t.row == hover_row and t.col == hover_col
                                for t in gs.towers)
                )
                renderer.draw_hover(hover_row, hover_col, can_place)
            if gs.game_over:
                renderer.draw_game_over(gs)
            elif gs.paused:
                renderer.draw_paused()
            elif gs.win:
                is_last = gs.level_index + 1 >= len(LEVELS)
                renderer.draw_win(gs, is_last)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
