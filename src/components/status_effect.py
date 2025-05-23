import random
import pygame

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
        # Update particles
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