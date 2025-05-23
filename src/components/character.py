import random
import math

import pygame
from src.components.character_sprite import CharacterSprite
from src.components.level_system import LevelSystem
from src.components.status_effect import StatusEffect
from src.utils.constants import BURN_COLOR, BLESS_COLOR

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