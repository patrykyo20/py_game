import pygame
import math

class CharacterSprite:
    def __init__(self, character_type, is_player=True):
        self.type = character_type
        self.is_player = is_player
        self.size = (100, 150)
        self.position = [0, 0]
        self.target_position = [0, 0]
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_attacking = False
        self.attack_progress = 0
        self.flash_timer = 0
        self.stealth_alpha = 255
        self.create_sprite()

    def create_sprite(self):
        self.sprite = pygame.Surface(self.size, pygame.SRCALPHA)
        if self.type == "Warrior":
            self.draw_warrior()
        elif self.type == "Mage":
            self.draw_mage()
        elif self.type == "Archer":
            self.draw_archer()
        elif self.type == "Rogue":
            self.draw_rogue()
        elif self.type == "Paladin":
            self.draw_paladin()
        else: 
            self.draw_enemy()

    def draw_warrior(self):
        pygame.draw.rect(self.sprite, (100, 100, 100), (40, 30, 20, 60))
        pygame.draw.circle(self.sprite, (255, 200, 150), (50, 20), 15)
        pygame.draw.rect(self.sprite, (200, 200, 200), (60, 40, 30, 5))
        pygame.draw.rect(self.sprite, (150, 150, 150), (85, 35, 5, 15))
        pygame.draw.rect(self.sprite, (150, 100, 50), (30, 40, 10, 30))

    def draw_mage(self):
        pygame.draw.rect(self.sprite, (100, 50, 150), (40, 30, 20, 60))
        pygame.draw.circle(self.sprite, (255, 200, 150), (50, 20), 15)
        pygame.draw.rect(self.sprite, (150, 100, 50), (60, 30, 5, 60))
        pygame.draw.circle(self.sprite, (255, 255, 0), (65, 30), 8)

    def draw_archer(self):
        pygame.draw.rect(self.sprite, (50, 100, 50), (40, 30, 20, 60))
        pygame.draw.circle(self.sprite, (255, 200, 150), (50, 20), 15)
        pygame.draw.arc(self.sprite, (150, 100, 50), (60, 40, 30, 30), 0, math.pi, 3)
        pygame.draw.line(self.sprite, (200, 200, 200), (70, 55), (90, 55), 2)

    def draw_rogue(self):
        pygame.draw.rect(self.sprite, (50, 50, 50), (40, 30, 20, 60))
        pygame.draw.circle(self.sprite, (255, 200, 150), (50, 20), 15)
        pygame.draw.arc(self.sprite, (30, 30, 30), (35, 10, 30, 30), 0, math.pi, 3)
        pygame.draw.line(self.sprite, (200, 200, 200), (30, 50), (20, 40), 3)
        pygame.draw.line(self.sprite, (200, 200, 200), (70, 50), (80, 40), 3)

    def draw_paladin(self):
        pygame.draw.rect(self.sprite, (200, 200, 255), (40, 30, 20, 60))
        pygame.draw.circle(self.sprite, (255, 200, 150), (50, 20), 15)
        pygame.draw.arc(self.sprite, (200, 200, 200), (35, 15, 30, 20), 0, math.pi, 3)
        pygame.draw.rect(self.sprite, (255, 255, 200), (30, 40, 10, 30))
        pygame.draw.circle(self.sprite, (255, 255, 0), (35, 55), 5)

    def draw_enemy(self):
        pygame.draw.rect(self.sprite, (150, 0, 0), (40, 30, 20, 60))
        pygame.draw.circle(self.sprite, (100, 0, 0), (50, 20), 15)
        pygame.draw.circle(self.sprite, (255, 0, 0), (45, 18), 3)
        pygame.draw.circle(self.sprite, (255, 0, 0), (55, 18), 3)
        pygame.draw.line(self.sprite, (200, 200, 200), (30, 50), (20, 40), 3)
        pygame.draw.line(self.sprite, (200, 200, 200), (70, 50), (80, 40), 3)

    def update(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

        if self.is_attacking:
            self.attack_progress += 0.1
            if self.attack_progress >= 1:
                self.is_attacking = False
                self.attack_progress = 0
                self.position = self.target_position.copy()
            else:
                progress = math.sin(self.attack_progress * math.pi)
                self.position[0] = self.target_position[0] + (50 * progress)

        if self.flash_timer > 0:
            self.flash_timer -= 1

    def draw(self, screen):
        if self.flash_timer > 0:
            flash_surface = self.sprite.copy()
            flash_surface.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(flash_surface, self.position)
        else:
            screen.blit(self.sprite, self.position)

    def flash(self):
        self.flash_timer = 10 