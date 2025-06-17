import pygame
import math

class Bullet:
    def __init__(self, x, y, angle, damage=25, speed=10):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.radius = 3
        self.damage = damage
        self.lifetime = 60  # 1 second at 60 FPS
        
        # Trail effect
        self.trail = []
        self.max_trail_length = 5
        
    def update(self):
        # Store current position for trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
            
        # Update position
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        self.lifetime -= 1
        
    def draw(self, screen):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            # Calculate alpha based on position in trail
            alpha = int(255 * (i / len(self.trail)))
            radius = int(self.radius * (i / len(self.trail)))
            
            # Create a surface with alpha channel
            surf = pygame.Surface((radius * 2 + 1, radius * 2 + 1), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 0, alpha), (radius + 1, radius + 1), max(1, radius))
            
            # Draw the surface to the screen
            screen.blit(surf, (trail_x - radius, trail_y - radius))
        
        # Draw bullet
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius)
        
    def is_dead(self):
        return self.lifetime <= 0 or self.x < 0 or self.x > 800 or self.y < 0 or self.y > 600
