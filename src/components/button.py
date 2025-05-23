import pygame
from src.utils.constants import WHITE

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
        # Animate button on hover
        if self.is_hovered:
            self.animation_offset = min(self.animation_offset + self.animation_speed, 5)
            self.glow_radius = min(self.glow_radius + 1, 10)
        else:
            self.animation_offset = max(self.animation_offset - self.animation_speed, 0)
            self.glow_radius = max(self.glow_radius - 1, 0)

        # Draw glow effect
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

        # Draw button shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += self.shadow_offset
        shadow_rect.y += self.shadow_offset
        pygame.draw.rect(screen, (0, 0, 0, 128), shadow_rect, border_radius=10)
        
        # Draw main button
        color = self.hover_color if self.is_hovered else self.color
        button_rect = self.rect.copy()
        button_rect.y -= self.animation_offset
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=10)
        
        # Draw icon if exists
        if self.icon:
            icon_rect = self.icon.get_rect(center=(button_rect.x + 30, button_rect.centery))
            screen.blit(self.icon, icon_rect)
            text_x = button_rect.x + 60
        else:
            text_x = button_rect.x
        
        # Draw text with shadow
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