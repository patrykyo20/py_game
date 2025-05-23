import pygame
import sys
import random
from src.components.button import Button
from src.components.character import Character
from src.utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, RED, GREEN, BLUE, GOLD,
    DARK_BLUE, LIGHT_BLUE, PURPLE, DARK_PURPLE, SILVER, DARK_GREEN,
    YELLOW, CHARACTER_STATS
)

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
                            character_type = ["Warrior", "Mage", "Archer", "Rogue", "Paladin"][i]
                            self.player = Character(character_type, CHARACTER_STATS[character_type])
                            self.enemy = Character("Enemy", CHARACTER_STATS["Enemy"])
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