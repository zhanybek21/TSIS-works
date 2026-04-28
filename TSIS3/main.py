import pygame
import sys
from persistence import load_data, save_data
from ui import Button, draw_text, FONT, TITLE_FONT
from racer import GameEngine

pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 3 - Advanced Racer")

settings = load_data('settings.json', {'sound': True, 'color': 'red', 'difficulty': 'Normal'})
leaderboard = load_data('leaderboard.json', [])

def get_username():
    name = ""
    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "Enter Username:", TITLE_FONT, (255, 255, 255), WIDTH//2, HEIGHT//3, center=True)
        draw_text(screen, name + "_", FONT, (255, 255, 0), WIDTH//2, HEIGHT//2, center=True)
        draw_text(screen, "Press ENTER to start", FONT, (150, 150, 150), WIDTH//2, HEIGHT//2 + 100, center=True)
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
                    if len(name) < 10: name += event.unicode

def menu_screen():
    btns = [
        Button(WIDTH//2 - 100, 300, 200, 50, "Play", (100, 255, 100), (50, 200, 50)),
        Button(WIDTH//2 - 100, 380, 200, 50, "Leaderboard", (100, 200, 255), (50, 150, 200)),
        Button(WIDTH//2 - 100, 460, 200, 50, "Settings", (255, 200, 100), (200, 150, 50)),
        Button(WIDTH//2 - 100, 540, 200, 50, "Quit", (255, 100, 100), (200, 50, 50))
    ]
    
    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "RACER GAME", TITLE_FONT, (255, 255, 255), WIDTH//2, 150, center=True)
        
        mouse_pos = pygame.mouse.get_pos()
        for b in btns:
            b.update(mouse_pos)
            b.draw(screen)
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if btns[0].is_clicked(event): return 'play'
            if btns[1].is_clicked(event): return 'leaderboard'
            if btns[2].is_clicked(event): return 'settings'
            if btns[3].is_clicked(event): return 'quit'

def settings_screen():
    global settings
    colors = ['red', 'blue', 'green']
    diffs = ['Easy', 'Normal', 'Hard']
    
    btn_color = Button(WIDTH//2 - 100, 250, 200, 50, f"Color: {settings['color']}", (200,200,200), (150,150,150))
    btn_diff = Button(WIDTH//2 - 100, 330, 200, 50, f"Diff: {settings['difficulty']}", (200,200,200), (150,150,150))
    btn_sound = Button(WIDTH//2 - 100, 410, 200, 50, f"Sound: {'On' if settings['sound'] else 'Off'}", (200,200,200), (150,150,150))
    btn_back = Button(WIDTH//2 - 100, 550, 200, 50, "Back", (255, 100, 100), (200, 50, 50))

    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "SETTINGS", TITLE_FONT, (255, 255, 255), WIDTH//2, 100, center=True)
        
        mouse_pos = pygame.mouse.get_pos()
        for b in [btn_color, btn_diff, btn_sound, btn_back]:
            b.update(mouse_pos)
            b.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if btn_color.is_clicked(event):
                settings['color'] = colors[(colors.index(settings['color']) + 1) % 3]
                btn_color.text = f"Color: {settings['color']}"
            if btn_diff.is_clicked(event):
                settings['difficulty'] = diffs[(diffs.index(settings['difficulty']) + 1) % 3]
                btn_diff.text = f"Diff: {settings['difficulty']}"
            if btn_sound.is_clicked(event):
                settings['sound'] = not settings['sound']
                btn_sound.text = f"Sound: {'On' if settings['sound'] else 'Off'}"
            if btn_back.is_clicked(event):
                save_data('settings.json', settings)
                return

def leaderboard_screen():
    btn_back = Button(WIDTH//2 - 100, 650, 200, 50, "Back", (255, 100, 100), (200, 50, 50))
    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "TOP 10 SCORES", TITLE_FONT, (255, 215, 0), WIDTH//2, 80, center=True)
        
        y = 180
        for i, entry in enumerate(leaderboard[:10]):
            text = f"{i+1}. {entry['name']} - {entry['score']} pts ({entry['dist']}m)"
            draw_text(screen, text, FONT, (255, 255, 255), WIDTH//2, y, center=True)
            y += 40

        btn_back.update(pygame.mouse.get_pos())
        btn_back.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if btn_back.is_clicked(event): return

def game_over_screen(result):
    btn_retry = Button(WIDTH//2 - 100, 450, 200, 50, "Retry", (100, 255, 100), (50, 200, 50))
    btn_menu = Button(WIDTH//2 - 100, 530, 200, 50, "Menu", (100, 200, 255), (50, 150, 200))
    
    while True:
        screen.fill((50, 10, 10))
        draw_text(screen, "CRASHED!", TITLE_FONT, (255, 50, 50), WIDTH//2, 150, center=True)
        draw_text(screen, f"Score: {result['score']}", FONT, (255, 255, 255), WIDTH//2, 250, center=True)
        draw_text(screen, f"Distance: {result['dist']}m", FONT, (255, 255, 255), WIDTH//2, 300, center=True)
        draw_text(screen, f"Coins: {result['coins']}", FONT, (255, 215, 0), WIDTH//2, 350, center=True)
        
        mouse_pos = pygame.mouse.get_pos()
        btn_retry.update(mouse_pos); btn_retry.draw(screen)
        btn_menu.update(mouse_pos); btn_menu.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return 'menu'
            if btn_retry.is_clicked(event): return 'retry'
            if btn_menu.is_clicked(event): return 'menu'

def main():
    while True:
        choice = menu_screen()
        if choice == 'quit':
            break
        elif choice == 'settings':
            settings_screen()
        elif choice == 'leaderboard':
            leaderboard_screen()
        elif choice == 'play':
            name = get_username()
            while True:
                game = GameEngine(screen, settings)
                result = game.run()
                if not result: break 
                
                leaderboard.append({'name': name, 'score': result['score'], 'dist': result['dist']})
                leaderboard.sort(key=lambda x: x['score'], reverse=True)
                save_data('leaderboard.json', leaderboard)
                
                post_choice = game_over_screen(result)
                if post_choice == 'menu': break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()