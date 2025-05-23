import random
import math
import pygame
from src.utils.constants import YELLOW, WHITE

class LevelSystem:
    def __init__(self):
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.level_up_animation = 0
        self.level_up_particles = []

    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.level_up()
        return self.xp, self.xp_to_next_level

    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        self.level_up_animation = 60
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.level_up_particles.append({
                'pos': [0, 0],
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'lifetime': random.randint(30, 60),
                'max_lifetime': 60
            })
        return True

    def update(self):
        if self.level_up_animation > 0:
            self.level_up_animation -= 1
            for particle in self.level_up_particles[:]:
                particle['pos'][0] += particle['vel'][0]
                particle['pos'][1] += particle['vel'][1]
                particle['lifetime'] -= 1
                if particle['lifetime'] <= 0:
                    self.level_up_particles.remove(particle)

    def draw(self, screen, x, y):
        bar_width = 200
        bar_height = 20
        xp_percent = self.xp / self.xp_to_next_level
        
        pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height), border_radius=10)
        if xp_percent > 0:
            fill_width = int(bar_width * xp_percent)
            pygame.draw.rect(screen, YELLOW, (x, y, fill_width, bar_height), border_radius=10)
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 2, border_radius=10)
        
        level_text = f"Level {self.level}"
        font = pygame.font.Font(None, 24)
        text_surface = font.render(level_text, True, WHITE)
        screen.blit(text_surface, (x + bar_width + 10, y))
        
        xp_text = f"XP: {self.xp}/{self.xp_to_next_level}"
        text_surface = font.render(xp_text, True, WHITE)
        screen.blit(text_surface, (x, y - 25))
        
        if self.level_up_animation > 0:
            for particle in self.level_up_particles:
                alpha = int((particle['lifetime'] / particle['max_lifetime']) * 255)
                color = (*YELLOW, alpha)
                pos = (int(x + bar_width/2 + particle['pos'][0]), 
                      int(y + bar_height/2 + particle['pos'][1]))
                pygame.draw.circle(screen, color, pos, 3) 