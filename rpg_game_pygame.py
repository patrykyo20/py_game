import pygame
import sys
import random
import os
import math

pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
PURPLE = (128, 0, 128)
DARK_PURPLE = (75, 0, 130)
SILVER = (192, 192, 192)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)

POISON_COLOR = (0, 255, 0)
BURN_COLOR = (255, 69, 0)
BLESS_COLOR = (255, 215, 0)
STEALTH_COLOR = (128, 128, 128)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.icon = icon
        self.animation_offset = 0
        self.animation_speed = 2
        self.shadow_offset = 5
        self.glow_radius = 0
        self.glow_color = (255, 255, 255, 128)

    def draw(self, screen, font):
        if self.is_hovered:
            self.animation_offset = min(self.animation_offset + self.animation_speed, 5)
            self.glow_radius = min(self.glow_radius + 1, 10)
        else:
            self.animation_offset = max(self.animation_offset - self.animation_speed, 0)
            self.glow_radius = max(self.glow_radius - 1, 0)

        if self.glow_radius > 0:
            glow_surf = pygame.Surface((self.rect.width + self.glow_radius * 2, 
                                      self.rect.height + self.glow_radius * 2), 
                                     pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, self.glow_color, 
                           (self.glow_radius, self.glow_radius, 
                            self.rect.width, self.rect.height), 
                           border_radius=10)
            screen.blit(glow_surf, 
                       (self.rect.x - self.glow_radius, 
                        self.rect.y - self.glow_radius))

        shadow_rect = self.rect.copy()
        shadow_rect.x += self.shadow_offset
        shadow_rect.y += self.shadow_offset
        pygame.draw.rect(screen, (0, 0, 0, 128), shadow_rect, border_radius=10)
        
        color = self.hover_color if self.is_hovered else self.color
        button_rect = self.rect.copy()
        button_rect.y -= self.animation_offset
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=10)
        
        if self.icon:
            icon_rect = self.icon.get_rect(center=(button_rect.x + 30, button_rect.centery))
            screen.blit(self.icon, icon_rect)
            text_x = button_rect.x + 60
        else:
            text_x = button_rect.x
        
        text_surface = font.render(self.text, True, WHITE)
        shadow_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=(text_x, button_rect.centery))
        screen.blit(shadow_surface, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class StatusEffect:
    def __init__(self, name, duration, color, effect_func):
        self.name = name
        self.duration = duration
        self.color = color
        self.effect_func = effect_func
        self.particles = []

    def apply(self, target):
        return self.effect_func(target)

    def update(self):
        self.duration -= 1
        for particle in self.particles[:]:
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, screen, pos):
        for particle in self.particles:
            alpha = int((particle['lifetime'] / particle['max_lifetime']) * 255)
            color = (*self.color, alpha)
            pygame.draw.circle(screen, color, 
                             (int(pos[0] + particle['offset'][0]), 
                              int(pos[1] + particle['offset'][1])), 
                             2)

    def add_particle(self, pos):
        self.particles.append({
            'offset': [random.uniform(-10, 10), random.uniform(-10, 10)],
            'lifetime': random.randint(20, 40),
            'max_lifetime': 40
        })

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

class Character:
    def __init__(self, name, stats):
        self.name = name
        self.max_health = stats['health']
        self.health = stats['health']
        self.attack = stats['attack']
        self.defense = stats['defense']
        self.special_cooldown = 0
        self.max_special_cooldown = 3
        self.sprite = CharacterSprite(name, name != "Enemy")
        self.particles = []
        self.effects = []
        self.stealth = False
        self.stealth_timer = 0
        self.crit_chance = 0.1
        self.dodge_chance = 0.05
        self.level_system = LevelSystem()
        self.base_stats = stats.copy()   

    def level_up_stats(self):
        if self.name == "Warrior":
            self.max_health += 15
            self.attack += 2
            self.defense += 2
        elif self.name == "Mage":
            self.max_health += 8
            self.attack += 3
            self.defense += 1
        elif self.name == "Archer":
            self.max_health += 10
            self.attack += 2
            self.defense += 1
        elif self.name == "Rogue":
            self.max_health += 8
            self.attack += 2
            self.defense += 1
            self.crit_chance += 0.02
        elif self.name == "Paladin":
            self.max_health += 12
            self.attack += 1
            self.defense += 2
        
        self.health = self.max_health
        return True

    def update(self):
        self.sprite.update()
        self.update_particles()
        self.update_effects()
        if self.stealth:
            self.stealth_timer -= 1
            if self.stealth_timer <= 0:
                self.stealth = False
        self.level_system.update()

    def update_effects(self):
        for effect in self.effects[:]:
            effect.update()
            if effect.duration <= 0:
                self.effects.remove(effect)
            else:
                effect.apply(self)

    def add_effect(self, effect):
        self.effects.append(effect)

    def draw(self, screen):
        self.sprite.draw(screen)
        self.draw_particles(screen)
        for effect in self.effects:
            effect.draw_particles(screen, self.sprite.position)
        self.level_system.draw(screen, self.sprite.position[0], self.sprite.position[1] - 50)

    def add_particle(self, pos, color, velocity, lifetime):
        self.particles.append({
            'pos': list(pos),
            'vel': list(velocity),
            'color': color,
            'lifetime': lifetime,
            'max_lifetime': lifetime
        })

    def update_particles(self):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, screen):
        for particle in self.particles:
            alpha = int((particle['lifetime'] / particle['max_lifetime']) * 255)
            color = (*particle['color'], alpha)
            pos = (int(particle['pos'][0]), int(particle['pos'][1]))
            pygame.draw.circle(screen, color, pos, 2)

    def take_damage(self, damage):
        if random.random() < self.dodge_chance:
            return 0, "DODGE!"

        is_crit = random.random() < self.crit_chance
        if is_crit:
            damage *= 1.5

        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        self.sprite.flash()
        
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.add_particle(
                self.sprite.position,
                (255, 0, 0),
                [math.cos(angle) * speed, math.sin(angle) * speed],
                30
            )
        return actual_damage, "CRITICAL!" if is_crit else ""

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.add_particle(
                self.sprite.position,
                (0, 255, 0),
                [math.cos(angle) * speed, math.sin(angle) * speed],
                30
            )
        return amount

    def is_alive(self):
        return self.health > 0

    def get_health_percentage(self):
        return (self.health / self.max_health) * 100

    def use_special_ability(self, target):
        if self.special_cooldown > 0:
            return False, "Special ability is on cooldown!"

        self.special_cooldown = self.max_special_cooldown
        
        if self.name == "Warrior":
            damage = self.attack * 2
            actual_damage, message = target.take_damage(damage)
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(3, 6)
                self.add_particle(
                    self.sprite.position,
                    (255, 100, 0),
                    [math.cos(angle) * speed, math.sin(angle) * speed],
                    40
                )
            return True, f"{self.name} uses Berserker Rage and deals {actual_damage} damage! {message}"
            
        elif self.name == "Mage":
            damage = self.attack * 1.5
            actual_damage, message = target.take_damage(damage)
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(3, 6)
                self.add_particle(
                    self.sprite.position,
                    (255, 200, 0),
                    [math.cos(angle) * speed, math.sin(angle) * speed],
                    40
                )
            if random.random() < 0.5: 
                target.add_effect(StatusEffect("Burn", 3, BURN_COLOR, 
                    lambda t: t.take_damage(5)[0]))
                return True, f"{self.name} casts Fireball dealing {actual_damage} damage and burns the target! {message}"
            return True, f"{self.name} casts Fireball dealing {actual_damage} damage! {message}"
            
        elif self.name == "Archer":
            damage = self.attack * 2.5
            actual_damage, message = target.take_damage(damage)
            for _ in range(20):
                angle = random.uniform(-0.2, 0.2) 
                speed = random.uniform(5, 8)
                self.add_particle(
                    self.sprite.position,
                    (200, 200, 200),
                    [math.cos(angle) * speed, math.sin(angle) * speed],
                    30
                )
            return True, f"{self.name} uses Precision Shot and deals {actual_damage} damage! {message}"

        elif self.name == "Rogue":
            self.stealth = True
            self.stealth_timer = 2
            self.crit_chance = 0.5 
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                self.add_particle(
                    self.sprite.position,
                    (128, 128, 128),
                    [math.cos(angle) * speed, math.sin(angle) * speed],
                    30
                )
            return True, f"{self.name} enters Stealth mode!"

        elif self.name == "Paladin":
            heal_amount = self.attack * 1.5
            self.heal(heal_amount)
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 4)
                self.add_particle(
                    self.sprite.position,
                    (255, 255, 200),
                    [math.cos(angle) * speed, math.sin(angle) * speed],
                    30
                )
            self.add_effect(StatusEffect("Blessed", 2, BLESS_COLOR,
                lambda t: setattr(t, 'defense', t.defense + 5)))
            return True, f"{self.name} uses Holy Light and heals for {heal_amount}!"

        return False, "No special ability available!"

    def update_cooldowns(self):
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

    def gain_xp(self, amount):
        if self.level_system.add_xp(amount):
            self.level_up_stats()
            return True
        return False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Epic RPG Battle")
        self.clock = pygame.time.Clock()
        
        self.title_font = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.background = self.create_background()
        
        self.attack_button = Button(50, WINDOW_HEIGHT - 100, 200, 50, "Attack", DARK_BLUE, BLUE)
        self.special_button = Button(300, WINDOW_HEIGHT - 100, 200, 50, "Special Ability", PURPLE, DARK_PURPLE)
        
        self.class_buttons = [
            Button(WINDOW_WIDTH//2 - 150, 200, 300, 60, "Warrior", DARK_BLUE, BLUE),
            Button(WINDOW_WIDTH//2 - 150, 300, 300, 60, "Mage", PURPLE, DARK_PURPLE),
            Button(WINDOW_WIDTH//2 - 150, 400, 300, 60, "Archer", (0, 100, 0), (0, 200, 0)),
            Button(WINDOW_WIDTH//2 - 150, 500, 300, 60, "Rogue", (50, 50, 50), (100, 100, 100)),
            Button(WINDOW_WIDTH//2 - 150, 600, 300, 60, "Paladin", (200, 200, 255), (255, 255, 200))
        ]
        
        self.player = None
        self.enemy = None
        self.combat_log = []
        self.current_turn = 0
        self.game_state = "character_select"
        
        self.screen_shake = 0
        self.shake_duration = 0
        self.shake_intensity = 0
        self.enemy_level = 1
        self.enemy_xp_reward = 50

    def create_background(self):
        background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            color = (
                int(20 + (y / WINDOW_HEIGHT) * 10),
                int(20 + (y / WINDOW_HEIGHT) * 10),
                int(40 + (y / WINDOW_HEIGHT) * 20)
            )
            pygame.draw.line(background, color, (0, y), (WINDOW_WIDTH, y))
        return background

    def apply_screen_shake(self, intensity=5, duration=10):
        self.shake_intensity = intensity
        self.shake_duration = duration

    def get_shake_offset(self):
        if self.shake_duration > 0:
            self.shake_duration -= 1
            return (
                random.randint(-self.shake_intensity, self.shake_intensity),
                random.randint(-self.shake_intensity, self.shake_intensity)
            )
        return (0, 0)

    def draw_text(self, text, x, y, color=WHITE, font=None, centered=False, shadow=True):
        if font is None:
            font = self.font
        if shadow:
            shadow_surface = font.render(text, True, (0, 0, 0))
            if centered:
                shadow_rect = shadow_surface.get_rect(center=(x + 2, y + 2))
            else:
                shadow_rect = shadow_surface.get_rect(topleft=(x + 2, y + 2))
            self.screen.blit(shadow_surface, shadow_rect)
        
        text_surface = font.render(text, True, color)
        if centered:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_health_bar(self, character, x, y):
        bar_width = 300
        bar_height = 30
        
        shadow_rect = pygame.Rect(x + 2, y + 2, bar_width, bar_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), shadow_rect, border_radius=15)
        
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (50, 50, 50), bg_rect, border_radius=15)
        
        health_width = int((character.health / character.max_health) * bar_width)
        if health_width > 0:
            health_rect = pygame.Rect(x, y, health_width, bar_height)
            health_color = (
                int(255 * (1 - character.health/character.max_health)),
                int(255 * (character.health/character.max_health)),
                0
            )
            pygame.draw.rect(self.screen, health_color, health_rect, border_radius=15)
        
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2, border_radius=15)
        
        health_text = f"{character.name}: {character.health}/{character.max_health}"
        self.draw_text(health_text, x, y - 25, WHITE, self.small_font, shadow=True)

    def draw_character_select(self):
        self.screen.blit(self.background, (0, 0))
        
        title = "Choose Your Hero"
        self.draw_text(title, WINDOW_WIDTH//2, 100, GOLD, self.title_font, True)
        
        descriptions = [
            "Warrior - High health, balanced stats",
            "Mage - High attack, low defense",
            "Archer - Balanced stats, good range",
            "Rogue - Stealth and critical hits",
            "Paladin - Healing and defense buffs"
        ]
        
        for i, desc in enumerate(descriptions):
            y = 280 + i * 100
            desc_bg = pygame.Surface((400, 40))
            desc_bg.fill((30, 30, 50))
            desc_bg.set_alpha(200)
            self.screen.blit(desc_bg, (WINDOW_WIDTH//2 - 200, y - 20))
            self.draw_text(desc, WINDOW_WIDTH//2, y, WHITE, self.small_font, True)
        
        for button in self.class_buttons:
            button.draw(self.screen, self.font)

    def draw_battle_screen(self):
        shake_offset = self.get_shake_offset()
        
        self.screen.blit(self.background, shake_offset)
        
        self.player.update()
        self.enemy.update()
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        
        self.draw_health_bar(self.player, 50, 50)
        self.draw_text(f"Attack: {self.player.attack}", 50, 100, LIGHT_BLUE)
        self.draw_text(f"Defense: {self.player.defense}", 50, 130, LIGHT_BLUE)
        if self.player.special_cooldown > 0:
            self.draw_text(f"Special Cooldown: {self.player.special_cooldown}", 50, 160, RED)
        
        self.draw_health_bar(self.enemy, WINDOW_WIDTH - 350, 50)
        self.draw_text(f"Attack: {self.enemy.attack}", WINDOW_WIDTH - 350, 100, LIGHT_BLUE)
        self.draw_text(f"Defense: {self.enemy.defense}", WINDOW_WIDTH - 350, 130, LIGHT_BLUE)
        if self.enemy.special_cooldown > 0:
            self.draw_text(f"Special Cooldown: {self.enemy.special_cooldown}", WINDOW_WIDTH - 350, 160, RED)
        
        self.draw_text("Combat Log:", 50, 250, GOLD)
        log_background = pygame.Surface((WINDOW_WIDTH - 100, 200))
        log_background.fill((30, 30, 50))
        log_background.set_alpha(200)
        self.screen.blit(log_background, (50, 280))
        
        for i, entry in enumerate(self.combat_log[-5:]):
            self.draw_text(entry, 70, 300 + i * 30, WHITE, self.small_font)
        
        self.attack_button.draw(self.screen, self.font)
        self.special_button.draw(self.screen, self.font)

    def execute_turn(self, action):
        self.current_turn += 1
        self.combat_log.append(f"--- Turn {self.current_turn} ---")
        
        if action == 'attack':
            damage = self.player.attack
            actual_damage, message = self.enemy.take_damage(damage)
            self.combat_log.append(f"{self.player.name} attacks for {actual_damage} damage! {message}")
            self.apply_screen_shake(5, 10)
        elif action == 'special':
            success, message = self.player.use_special_ability(self.enemy)
            self.combat_log.append(message)
            self.apply_screen_shake(10, 15)
        
        if not self.enemy.is_alive():
            if self.player.gain_xp(self.enemy_xp_reward):
                self.combat_log.append(f"{self.player.name} leveled up to level {self.player.level_system.level}!")
            self.combat_log.append(f"{self.enemy.name} has been defeated!")
            self.game_state = "game_over"
            return
        
        if random.random() < 0.3 and self.enemy.special_cooldown == 0:
            success, message = self.enemy.use_special_ability(self.player)
            self.combat_log.append(message)
            self.apply_screen_shake(10, 15)
        else:
            damage = self.enemy.attack
            actual_damage, message = self.player.take_damage(damage)
            self.combat_log.append(f"{self.enemy.name} attacks for {actual_damage} damage! {message}")
            self.apply_screen_shake(5, 10)
        
        self.player.update_cooldowns()
        self.enemy.update_cooldowns()
        
        if not self.player.is_alive():
            self.combat_log.append(f"{self.player.name} has been defeated!")
            self.game_state = "game_over"

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.game_state == "character_select":
                    for i, button in enumerate(self.class_buttons):
                        if button.handle_event(event):
                            stats = {
                                'health': [120, 80, 100, 90, 110][i],
                                'attack': [15, 20, 18, 17, 14][i],
                                'defense': [10, 5, 8, 6, 12][i]
                            }
                            self.player = Character(["Warrior", "Mage", "Archer", "Rogue", "Paladin"][i], stats)
                            self.enemy = Character("Enemy", {'health': 100, 'attack': 12, 'defense': 8})
                            self.player.sprite.position = [WINDOW_WIDTH // 4 - 50, WINDOW_HEIGHT // 2 - 75]
                            self.player.sprite.target_position = self.player.sprite.position.copy()
                            self.enemy.sprite.position = [3 * WINDOW_WIDTH // 4 - 50, WINDOW_HEIGHT // 2 - 75]
                            self.enemy.sprite.target_position = self.enemy.sprite.position.copy()
                            self.game_state = "battle"
                
                elif self.game_state == "battle":
                    if self.attack_button.handle_event(event):
                        self.execute_turn('attack')
                    elif self.special_button.handle_event(event):
                        self.execute_turn('special')
                
                elif self.game_state == "game_over":
                    pygame.quit()
                    sys.exit()
            
            if self.game_state == "character_select":
                self.draw_character_select()
            elif self.game_state == "battle":
                self.draw_battle_screen()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run() 