import pygame

def flood_fill(surface, x, y, fill_color):
    target_color = surface.get_at((x, y))
    if target_color == fill_color:
        return

    width, height = surface.get_size()
    stack = [(x, y)]

    while stack:
        cx, cy = stack.pop()
        if surface.get_at((cx, cy)) == target_color:
            surface.set_at((cx, cy), fill_color)
            if cx > 0: stack.append((cx - 1, cy))
            if cx < width - 1: stack.append((cx + 1, cy))
            if cy > 0: stack.append((cx, cy - 1))
            if cy < height - 1: stack.append((cx, cy + 1))