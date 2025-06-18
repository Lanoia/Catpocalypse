import pygame
import math

class Animation:
    def __init__(self, x, y, animation_type, duration=30):
        self.x = x
        self.y = y
        self.type = animation_type
        self.duration = duration
        self.current_frame = 0
        self.finished = False
        
        # Animation types
        self.EXPLOSION = 0
        self.HIT = 1
        self.POWERUP = 2
        self.TEXT = 3
        
        # Text for text animations
        self.text = ""
        self.color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 24)
        
    def update(self):
        """Update animation frame"""
        self.current_frame += 1
        if self.current_frame >= self.duration:
            self.finished = True
            
    def draw(self, screen):
        """Draw the animation based on its type"""
        if self.type == self.EXPLOSION:
            self._draw_explosion(screen)
        elif self.type == self.HIT:
            self._draw_hit(screen)
        elif self.type == self.POWERUP:
            self._draw_powerup(screen)
        elif self.type == self.TEXT:
            self._draw_text(screen)
            
    def _draw_explosion(self, screen):
        """Draw explosion animation"""
        # Calculate size based on current frame
        progress = self.current_frame / self.duration
        size = int(30 * progress)
        alpha = int(255 * (1 - progress))
        
        # Create a surface with alpha channel
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw explosion circles with decreasing alpha
        pygame.draw.circle(surf, (255, 165, 0, alpha), (size, size), size)
        pygame.draw.circle(surf, (255, 0, 0, alpha), (size, size), int(size * 0.7))
        
        # Draw the surface to the screen
        screen.blit(surf, (self.x - size, self.y - size))
        
    def _draw_hit(self, screen):
        """Draw hit animation"""
        # Calculate size and alpha based on current frame
        progress = self.current_frame / self.duration
        size = int(10 * (1 - progress))
        alpha = int(255 * (1 - progress))
        
        # Create a surface with alpha channel
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw hit effect (X shape)
        pygame.draw.line(surf, (255, 255, 255, alpha), 
                        (0, 0), (size * 2, size * 2), 2)
        pygame.draw.line(surf, (255, 255, 255, alpha), 
                        (0, size * 2), (size * 2, 0), 2)
        
        # Draw the surface to the screen
        screen.blit(surf, (self.x - size, self.y - size))
        
    def _draw_powerup(self, screen):
        """Draw powerup animation"""
        # Calculate size and alpha based on current frame
        progress = self.current_frame / self.duration
        size = int(20 * (1 - progress))
        alpha = int(255 * (1 - progress))
        
        # Create a surface with alpha channel
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw powerup effect (expanding circle)
        pygame.draw.circle(surf, (255, 255, 0, alpha), (size, size), size, 2)
        
        # Draw the surface to the screen
        screen.blit(surf, (self.x - size, self.y - size))
        
    def _draw_text(self, screen):
        """Draw floating text animation"""
        # Calculate position and alpha based on current frame
        progress = self.current_frame / self.duration
        y_offset = int(20 * progress)
        alpha = int(255 * (1 - progress))
        
        # Create text surface
        text_surf = self.font.render(self.text, True, self.color)
        
        # Create a surface with alpha channel
        surf = pygame.Surface((text_surf.get_width(), text_surf.get_height()), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))  # Fill with transparent color
        
        # Blit text to surface with alpha
        text_surf.set_alpha(alpha)
        surf.blit(text_surf, (0, 0))
        
        # Draw the surface to the screen
        screen.blit(surf, (self.x - text_surf.get_width() // 2, self.y - y_offset))
        
    def set_text(self, text, color=(255, 255, 255), size=24):
        """Set text for text animations"""
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont(None, size)
        
class AnimationManager:
    def __init__(self):
        self.animations = []
        
    def add_explosion(self, x, y, duration=30):
        """Add explosion animation"""
        anim = Animation(x, y, 0, duration)
        self.animations.append(anim)
        
    def add_hit(self, x, y, duration=15):
        """Add hit animation"""
        anim = Animation(x, y, 1, duration)
        self.animations.append(anim)
        
    def add_powerup(self, x, y, duration=30):
        """Add powerup animation"""
        anim = Animation(x, y, 2, duration)
        self.animations.append(anim)
        
    def add_text(self, x, y, text, color=(255, 255, 255), size=24, duration=60):
        """Add floating text animation"""
        anim = Animation(x, y, 3, duration)
        anim.set_text(text, color, size)
        self.animations.append(anim)
        
    def update(self):
        """Update all animations and remove finished ones"""
        for anim in self.animations[:]:
            anim.update()
            if anim.finished:
                self.animations.remove(anim)
                
    def draw(self, screen):
        """Draw all active animations"""
        for anim in self.animations:
            anim.draw(screen)
            
# Create a global instance
animation_manager = AnimationManager()
