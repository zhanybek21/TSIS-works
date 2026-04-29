import pygame
import random

CELL_SIZE = 30
GRID_W, GRID_H = 20, 20
WIDTH, HEIGHT = CELL_SIZE * GRID_W, CELL_SIZE * GRID_H

COLORS = {
    'bg': (30, 30, 30), 'grid': (50, 50, 50),
    'food_normal': (0, 255, 0), 'food_big': (255, 215, 0), 'food_poison': (200, 0, 0),
    'wall': (100, 100, 100), 'speed': (0, 255, 255), 'slow': (150, 100, 255), 'shield': (100, 150, 255)
}

class GameEngine:
    def __init__(self, screen, settings, username, personal_best):
        self.screen = screen
        self.settings = settings
        self.username = username
        self.personal_best = personal_best
        self.font = pygame.font.SysFont(None, 24)
        
        self.reset_game()

    def reset_game(self):
        self.snake = [(GRID_W//2, GRID_H//2), (GRID_W//2 - 1, GRID_H//2)]
        self.dx, self.dy = 1, 0
        self.score = 0
        self.level = 1
        self.foods_eaten = 0
        self.base_fps = 8
        
        self.obstacles = []
        self.food = None
        self.powerup = None
        self.powerup_active = None
        self.powerup_timer = 0
        self.shield_active = False
        
        self.spawn_food()

    def get_empty_cell(self):
        while True:
            x, y = random.randint(0, GRID_W-1), random.randint(0, GRID_H-1)
            if (x, y) not in self.snake and (x, y) not in self.obstacles:
                return x, y

    def spawn_food(self):
        x, y = self.get_empty_cell()
        rand = random.random()
        if rand < 0.2: f_type = 'food_poison'
        elif rand < 0.4: f_type = 'food_big'
        else: f_type = 'food_normal'
        self.food = {'pos': (x, y), 'type': f_type, 'time': pygame.time.get_ticks()}

    def spawn_powerup(self):
        if self.powerup or self.powerup_active: return
        x, y = self.get_empty_cell()
        p_type = random.choice(['speed', 'slow', 'shield'])
        self.powerup = {'pos': (x, y), 'type': p_type, 'time': pygame.time.get_ticks()}

    def spawn_obstacles(self):
        self.obstacles = []
        if self.level < 3: return
        num_blocks = self.level * 2
        for _ in range(num_blocks):
            while True:
                x, y = self.get_empty_cell()
                hx, hy = self.snake[0]
                if abs(x - hx) + abs(y - hy) > 3:
                    self.obstacles.append((x, y))
                    break

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.powerup and current_time - self.powerup['time'] > 8000:
            self.powerup = None
            
        if self.powerup_active in ['speed', 'slow'] and current_time > self.powerup_timer:
            self.powerup_active = None

        if not self.powerup and not self.powerup_active and random.random() < 0.02:
            self.spawn_powerup()

        if self.food['type'] == 'food_big' and current_time - self.food['time'] > 7000:
            self.spawn_food()

        hx, hy = self.snake[0]
        nx, ny = hx + self.dx, hy + self.dy
        
        collision = False
        if nx < 0 or nx >= GRID_W or ny < 0 or ny >= GRID_H: collision = True
        if (nx, ny) in self.snake: collision = True
        if (nx, ny) in self.obstacles: collision = True

        if collision:
            if self.shield_active:
                self.shield_active = False
                self.powerup_active = None
                if nx < 0: nx = GRID_W - 1
                elif nx >= GRID_W: nx = 0
                elif ny < 0: ny = GRID_H - 1
                elif ny >= GRID_H: ny = 0
                else: return False
            else:
                return False

        self.snake.insert(0, (nx, ny))
        ate_food = False

        if self.food and (nx, ny) == self.food['pos']:
            ate_food = True
            if self.food['type'] == 'food_normal':
                self.score += 10
            elif self.food['type'] == 'food_big':
                self.score += 30
            elif self.food['type'] == 'food_poison':
                self.snake = self.snake[:-2]
                if len(self.snake) < 2: return False
            
            self.foods_eaten += 1
            if self.foods_eaten % 5 == 0:
                self.level += 1
                self.spawn_obstacles()
            self.spawn_food()
        
        if self.powerup and (nx, ny) == self.powerup['pos']:
            self.powerup_active = self.powerup['type']
            if self.powerup_active == 'shield':
                self.shield_active = True
            else:
                self.powerup_timer = current_time + 5000
            self.powerup = None

        if not ate_food:
            self.snake.pop()

        return True

    def draw(self):
        self.screen.fill(COLORS['bg'])
        
        if self.settings.get('grid', True):
            for x in range(0, WIDTH, CELL_SIZE):
                pygame.draw.line(self.screen, COLORS['grid'], (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, CELL_SIZE):
                pygame.draw.line(self.screen, COLORS['grid'], (0, y), (WIDTH, y))

        for obs in self.obstacles:
            pygame.draw.rect(self.screen, COLORS['wall'], (obs[0]*CELL_SIZE, obs[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        if self.food:
            pygame.draw.rect(self.screen, COLORS[self.food['type']], (self.food['pos'][0]*CELL_SIZE, self.food['pos'][1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
        if self.powerup:
            pygame.draw.circle(self.screen, COLORS[self.powerup['type']], 
                             (self.powerup['pos'][0]*CELL_SIZE + CELL_SIZE//2, self.powerup['pos'][1]*CELL_SIZE + CELL_SIZE//2), CELL_SIZE//2 - 2)

        snake_color = self.settings.get('color', [0, 255, 0])
        for i, segment in enumerate(self.snake):
            color = snake_color if i > 0 else (min(255, snake_color[0]+50), min(255, snake_color[1]+50), min(255, snake_color[2]+50))
            pygame.draw.rect(self.screen, color, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            
        if self.shield_active:
            hx, hy = self.snake[0]
            pygame.draw.circle(self.screen, COLORS['shield'], (hx*CELL_SIZE + CELL_SIZE//2, hy*CELL_SIZE + CELL_SIZE//2), CELL_SIZE//2 + 4, 2)

        texts = [
            f"Score: {self.score}",
            f"Best: {self.personal_best}",
            f"Level: {self.level}"
        ]
        if self.powerup_active:
            texts.append(f"PWR: {self.powerup_active.upper()}")
            
        for i, text in enumerate(texts):
            img = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(img, (10, 10 + i * 25))

    def get_fps(self):
        fps = self.base_fps + (self.level - 1) * 1.5
        if self.powerup_active == 'speed': fps *= 1.5
        elif self.powerup_active == 'slow': fps *= 0.6
        return int(fps)