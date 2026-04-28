import pygame
import sys
import math
from datetime import datetime
from tools import flood_fill

pygame.init()
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 2 - Paint")

try:
    icon_image = pygame.image.load("assets/icon.png")
    pygame.display.set_icon(icon_image)
except Exception:
    pass

font = pygame.font.SysFont(None, 24)

COLORS = [
    (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), 
    (255, 255, 0), (255, 165, 0), (128, 0, 128), (255, 255, 255)
]
color_idx = 0
current_color = COLORS[color_idx]

TOOLS = ['pencil', 'line', 'rect', 'circle', 'square', 'right_tri', 'eq_tri', 'rhombus', 'fill', 'text', 'eraser']
tool_idx = 0
current_tool = TOOLS[tool_idx]

brush_size = 2

canvas = pygame.Surface((WIDTH, HEIGHT - 50))
canvas.fill((255, 255, 255))
canvas_copy = canvas.copy()

drawing = False
start_pos = (0, 0)
last_pos = (0, 0)

text_mode = False
text_content = ""
text_pos = (0, 0)

def draw_shape(surface, tool, start, end, color, size):
    x1, y1 = start
    x2, y2 = end
    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    
    if tool == 'line':
        pygame.draw.line(surface, color, start, end, size)
    elif tool == 'rect':
        pygame.draw.rect(surface, color, rect, size)
    elif tool == 'circle':
        radius = int(math.hypot(x2 - x1, y2 - y1))
        pygame.draw.circle(surface, color, start, radius, size)
    elif tool == 'square':
        side = max(abs(x2 - x1), abs(y2 - y1))
        sq_rect = pygame.Rect(x1 if x2 > x1 else x1 - side, y1 if y2 > y1 else y1 - side, side, side)
        pygame.draw.rect(surface, color, sq_rect, size)
    elif tool == 'right_tri':
        pygame.draw.polygon(surface, color, [(x1, y1), (x1, y2), (x2, y2)], size)
    elif tool == 'eq_tri':
        mid_x = (x1 + x2) / 2
        pygame.draw.polygon(surface, color, [(mid_x, y1), (x1, y2), (x2, y2)], size)
    elif tool == 'rhombus':
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        pygame.draw.polygon(surface, color, [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)], size)

def draw_ui():
    pygame.draw.rect(screen, (220, 220, 220), (0, HEIGHT - 50, WIDTH, 50))
    ui_text = f"Tool (Up/Down): {current_tool}  |  Size (1,2,3): {brush_size}px  |  Color (Left/Right)  |  Save: Ctrl+S"
    txt_surf = font.render(ui_text, True, (0, 0, 0))
    screen.blit(txt_surf, (15, HEIGHT - 35))
    
    pygame.draw.rect(screen, current_color, (WIDTH - 50, HEIGHT - 40, 30, 30))
    if current_color == (255, 255, 255):
        pygame.draw.rect(screen, (0, 0, 0), (WIDTH - 50, HEIGHT - 40, 30, 30), 1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if text_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    text_mode = False
                    txt_surf = font.render(text_content, True, current_color)
                    canvas.blit(txt_surf, text_pos)
                    text_content = ""
                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_content = ""
                elif event.key == pygame.K_BACKSPACE:
                    text_content = text_content[:-1]
                else:
                    text_content += event.unicode
            continue

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                fname = datetime.now().strftime("canvas_%Y%m%d_%H%M%S.png")
                pygame.image.save(canvas, fname)
            elif event.key == pygame.K_1: brush_size = 2
            elif event.key == pygame.K_2: brush_size = 5
            elif event.key == pygame.K_3: brush_size = 10
            elif event.key == pygame.K_UP: tool_idx = (tool_idx + 1) % len(TOOLS); current_tool = TOOLS[tool_idx]
            elif event.key == pygame.K_DOWN: tool_idx = (tool_idx - 1) % len(TOOLS); current_tool = TOOLS[tool_idx]
            elif event.key == pygame.K_RIGHT: color_idx = (color_idx + 1) % len(COLORS); current_color = COLORS[color_idx]
            elif event.key == pygame.K_LEFT: color_idx = (color_idx - 1) % len(COLORS); current_color = COLORS[color_idx]

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and event.pos[1] < HEIGHT - 50:
                start_pos = event.pos
                last_pos = event.pos
                
                if current_tool == 'fill':
                    flood_fill(canvas, start_pos[0], start_pos[1], current_color)
                elif current_tool == 'text':
                    text_mode = True
                    text_pos = start_pos
                    text_content = ""
                else:
                    drawing = True
                    canvas_copy = canvas.copy()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False
                if current_tool not in ['pencil', 'eraser']:
                    canvas.blit(canvas_copy, (0, 0))
                    draw_shape(canvas, current_tool, start_pos, event.pos, current_color, brush_size)

        if event.type == pygame.MOUSEMOTION:
            if drawing:
                if current_tool == 'pencil':
                    pygame.draw.line(canvas, current_color, last_pos, event.pos, brush_size)
                    last_pos = event.pos
                elif current_tool == 'eraser':
                    pygame.draw.circle(canvas, (255, 255, 255), event.pos, brush_size * 3)
                else:
                    canvas.blit(canvas_copy, (0, 0))
                    draw_shape(canvas, current_tool, start_pos, event.pos, current_color, brush_size)

    screen.fill((200, 200, 200))
    screen.blit(canvas, (0, 0))
    
    if text_mode:
        txt_surf = font.render(text_content + "|", True, current_color)
        screen.blit(txt_surf, text_pos)

    draw_ui()
    pygame.display.flip()

pygame.quit()
sys.exit()