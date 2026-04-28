import pygame
import random
import os
from ui import draw_text, FONT, SMALL_FONT

WIDTH, HEIGHT = 600, 800
LANES = [150, 300, 450]

def load_image(name, w, h):
    path = os.path.join("assets", name)
    try:
        # Убрали .convert_alpha(), так как окно на момент импорта еще не создано
        img = pygame.image.load(path)
        return pygame.transform.scale(img, (w, h))
    except Exception as e:
        print(f"Ошибка загрузки {name}: {e}")
        return None

IMG_COIN = load_image("coin.png", 40, 40)
IMG_PLAYER = load_image("my_car.png", 50, 90)
IMG_ENEMY = load_image("opponent_car.png", 50, 90)

COLORS = {
    'enemy': (150, 0, 150), 'coin': (255, 215, 0), 'oil': (50, 50, 50),
    'barrier': (255, 140, 0), 'nitro': (0, 255, 255), 
    'shield': (100, 100, 255), 'repair': (0, 255, 100)
}

class Entity:
    def __init__(self, x, y, w, h, type_name):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.type_name = type_name
        self.active = True
        self.spawn_time = pygame.time.get_ticks()

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > HEIGHT:
            self.active = False

    def draw(self, surface):
        if self.type_name == 'coin' and IMG_COIN is not None:
            surface.blit(IMG_COIN, self.rect)
        elif self.type_name == 'enemy' and IMG_ENEMY is not None:
            surface.blit(IMG_ENEMY, self.rect)
        else:
            color = COLORS.get(self.type_name, (255, 255, 255))
            if self.type_name in ['coin', 'nitro', 'shield', 'repair']:
                pygame.draw.circle(surface, color, self.rect.center, self.rect.width // 2)
                pygame.draw.circle(surface, (0, 0, 0), self.rect.center, self.rect.width // 2, 2)
            else:
                pygame.draw.rect(surface, color, self.rect)
                pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

class GameEngine:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.clock = pygame.time.Clock()
        
        self.player_lane = 1
        self.player_rect = pygame.Rect(0, 0, 50, 90)
        self.player_rect.center = (LANES[self.player_lane], HEIGHT - 120)
        
        self.score = 0
        self.distance = 0
        self.coins = 0
        
        base_speeds = {"Easy": 5, "Normal": 8, "Hard": 12}
        self.base_speed = base_speeds.get(settings['difficulty'], 8)
        self.speed = self.base_speed
        
        self.entities = []
        self.spawn_timer = 0
        
        self.active_powerup = None
        self.powerup_timer = 0
        self.shield_active = False

        self.road_offset = 0

    def spawn_entity(self):
        lane = random.choice(LANES)
        y_pos = -100
        
        for e in self.entities:
            if e.rect.centerx == lane and e.rect.y < 100:
                return

        rand = random.random()
        if rand < 0.4:
            self.entities.append(Entity(lane, y_pos, 50, 90, 'enemy'))
        elif rand < 0.6:
            self.entities.append(Entity(lane, y_pos, 40, 40, 'barrier'))
        elif rand < 0.7:
            self.entities.append(Entity(lane, y_pos, 60, 60, 'oil'))
        elif rand < 0.9:
            coin = Entity(lane, y_pos, 40, 40, 'coin')
            coin.value = random.choices([1, 5, 10], weights=[70, 20, 10])[0]
            self.entities.append(coin)
        else:
            p_type = random.choice(['nitro', 'shield', 'repair'])
            self.entities.append(Entity(lane, y_pos, 30, 30, p_type))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            
            current_speed = self.base_speed + (self.distance / 1000)
            if self.active_powerup == 'nitro':
                current_speed *= 2

            self.distance += current_speed / 10

            self.spawn_timer += dt
            spawn_rate = max(300, 1500 - int(self.distance / 5))
            if self.spawn_timer > spawn_rate:
                self.spawn_entity()
                self.spawn_timer = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.player_lane > 0:
                        self.player_lane -= 1
                    if event.key == pygame.K_RIGHT and self.player_lane < 2:
                        self.player_lane += 1

            target_x = LANES[self.player_lane]
            self.player_rect.centerx += (target_x - self.player_rect.centerx) * 0.2

            current_time = pygame.time.get_ticks()
            if self.active_powerup and current_time > self.powerup_timer:
                self.active_powerup = None
                self.shield_active = False

            for e in self.entities[:]:
                e.update(current_speed)
                
                if e.type_name in ['nitro', 'shield', 'repair']:
                    if current_time - e.spawn_time > 5000:
                        e.active = False

                if not e.active:
                    self.entities.remove(e)
                    continue

                if self.player_rect.colliderect(e.rect):
                    if e.type_name == 'coin':
                        self.coins += e.value
                        self.score += e.value * 10
                        self.entities.remove(e)
                    elif e.type_name in ['nitro', 'shield', 'repair']:
                        self.active_powerup = e.type_name
                        self.powerup_timer = current_time + (5000 if e.type_name == 'nitro' else 0)
                        if e.type_name == 'shield':
                            self.shield_active = True
                        elif e.type_name == 'repair':
                            self.entities = [x for x in self.entities if x.type_name not in ['enemy', 'barrier', 'oil']]
                        self.score += 50
                        self.entities.remove(e)
                    elif e.type_name == 'oil':
                        self.distance = max(0, self.distance - 50)
                        self.entities.remove(e)
                    elif e.type_name in ['enemy', 'barrier']:
                        if self.shield_active:
                            self.shield_active = False
                            self.active_powerup = None
                            self.entities.remove(e)
                        else:
                            self.score += int(self.distance)
                            return {"score": self.score, "dist": int(self.distance), "coins": self.coins}

            self.screen.fill((100, 100, 100))
            
            self.road_offset = (self.road_offset + current_speed) % 40
            for y in range(-40, HEIGHT, 40):
                pygame.draw.rect(self.screen, (255, 255, 255), (WIDTH//3 - 5, y + self.road_offset, 10, 20))
                pygame.draw.rect(self.screen, (255, 255, 255), (WIDTH*2//3 - 5, y + self.road_offset, 10, 20))

            for e in self.entities:
                e.draw(self.screen)

            if IMG_PLAYER is not None:
                self.screen.blit(IMG_PLAYER, self.player_rect)
            else:
                pygame.draw.rect(self.screen, (0,0,200), self.player_rect)

            if self.shield_active:
                pygame.draw.circle(self.screen, COLORS['shield'], self.player_rect.center, 60, 3)

            draw_text(self.screen, f"Score: {self.score + int(self.distance)}", FONT, (255,255,255), 10, 10)
            draw_text(self.screen, f"Coins: {self.coins}", FONT, (255,255,255), 10, 40)
            draw_text(self.screen, f"Dist: {int(self.distance)}m", FONT, (255,255,255), 10, 70)
            
            if self.active_powerup:
                rem = max(0, (self.powerup_timer - current_time)//1000) if self.active_powerup == 'nitro' else '∞'
                draw_text(self.screen, f"PWR: {self.active_powerup.upper()} ({rem}s)", SMALL_FONT, COLORS[self.active_powerup], WIDTH//2, 20, center=True)

            pygame.display.flip()

        return None