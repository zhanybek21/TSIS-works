import pygame
import sys
import json
import os
from db import init_db, save_score, get_top_10, get_personal_best
from game import GameEngine, WIDTH, HEIGHT

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 4 - Snake DB")

FONT_L = pygame.font.SysFont(None, 64)
FONT_M = pygame.font.SysFont(None, 36)
FONT_S = pygame.font.SysFont(None, 24)

def load_settings():
    if not os.path.exists('settings.json'):
        return {'color': [0, 200, 0], 'grid': True, 'sound': True}
    with open('settings.json', 'r') as f:
        return json.load(f)

def save_settings(settings):
    with open('settings.json', 'w') as f:
        json.dump(settings, f)

settings = load_settings()
init_db()

def draw_text(text, font, color, y, x=WIDTH//2):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)
    return rect

def get_username():
    name = ""
    while True:
        screen.fill((30, 30, 30))
        draw_text("Enter Username:", FONT_L, (255, 255, 255), HEIGHT//3)
        draw_text(name + "_", FONT_M, (255, 255, 0), HEIGHT//2)
        draw_text("Press ENTER to start", FONT_S, (150, 150, 150), HEIGHT - 50)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15: name += event.unicode

def menu_screen():
    options = ["Play", "Leaderboard", "Settings", "Quit"]
    selected = 0
    while True:
        screen.fill((20, 20, 40))
        draw_text("SNAKE", FONT_L, (0, 255, 0), 100)
        
        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            draw_text(opt, FONT_M, color, 250 + i * 50)
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "Quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN: selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN: return options[selected]

def leaderboard_screen():
    top10 = get_top_10()
    while True:
        screen.fill((20, 40, 20))
        draw_text("TOP 10 SCORES", FONT_L, (255, 215, 0), 80)
        
        y = 150
        for i, row in enumerate(top10):
            text = f"{i+1}. {row[0]} - {row[1]} pts (Lvl {row[2]})"
            draw_text(text, FONT_S, (255, 255, 255), y)
            y += 35
            
        draw_text("Press ESC to return", FONT_S, (150, 150, 150), HEIGHT - 50)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return

def settings_screen():
    global settings
    colors = [(0, 200, 0), (200, 0, 0), (0, 0, 200)]
    color_names = ["Green", "Red", "Blue"]
    c_idx = colors.index(tuple(settings['color'])) if tuple(settings['color']) in colors else 0
    
    opts = ["Color", "Grid", "Sound", "Back"]
    selected = 0
    
    while True:
        screen.fill((40, 20, 20))
        draw_text("SETTINGS", FONT_L, (255, 255, 255), 100)
        
        c = (255, 255, 0) if selected == 0 else (255, 255, 255)
        draw_text(f"Color: {color_names[c_idx]}", FONT_M, c, 250)
        
        c = (255, 255, 0) if selected == 1 else (255, 255, 255)
        draw_text(f"Grid: {'On' if settings['grid'] else 'Off'}", FONT_M, c, 300)
        
        c = (255, 255, 0) if selected == 2 else (255, 255, 255)
        draw_text(f"Sound: {'On' if settings['sound'] else 'Off'}", FONT_M, c, 350)
        
        c = (255, 255, 0) if selected == 3 else (255, 255, 255)
        draw_text("Save & Back", FONT_M, c, 450)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected = (selected - 1) % 4
                if event.key == pygame.K_DOWN: selected = (selected + 1) % 4
                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        c_idx = (c_idx + 1) % len(colors)
                        settings['color'] = list(colors[c_idx])
                    elif selected == 1: settings['grid'] = not settings['grid']
                    elif selected == 2: settings['sound'] = not settings['sound']
                    elif selected == 3:
                        save_settings(settings)
                        return

def game_over_screen(score, level, best):
    while True:
        screen.fill((50, 10, 10))
        draw_text("GAME OVER", FONT_L, (255, 50, 50), 150)
        draw_text(f"Score: {score}", FONT_M, (255, 255, 255), 250)
        draw_text(f"Level: {level}", FONT_M, (255, 255, 255), 300)
        draw_text(f"Personal Best: {best}", FONT_M, (255, 215, 0), 350)
        
        draw_text("Press ENTER to Retry", FONT_S, (200, 200, 200), 450)
        draw_text("Press ESC for Menu", FONT_S, (200, 200, 200), 500)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return "Retry"
                if event.key == pygame.K_ESCAPE: return "Menu"

def main():
    clock = pygame.time.Clock()
    
    while True:
        choice = menu_screen()
        if choice == "Quit": break
        elif choice == "Leaderboard": leaderboard_screen()
        elif choice == "Settings": settings_screen()
        elif choice == "Play":
            username = get_username()
            best = get_personal_best(username)
            
            while True:
                game = GameEngine(screen, settings, username, best)
                running = True
                
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_UP and game.dy == 0: game.dx, game.dy = 0, -1
                            if event.key == pygame.K_DOWN and game.dy == 0: game.dx, game.dy = 0, 1
                            if event.key == pygame.K_LEFT and game.dx == 0: game.dx, game.dy = -1, 0
                            if event.key == pygame.K_RIGHT and game.dx == 0: game.dx, game.dy = 1, 0
                    
                    if not game.update():
                        running = False
                        
                    game.draw()
                    pygame.display.flip()
                    clock.tick(game.get_fps())
                
                save_score(username, game.score, game.level)
                if game.score > best: best = game.score
                
                post_action = game_over_screen(game.score, game.level, best)
                if post_action == "Menu": break

if __name__ == "__main__":
    main()