import pygame
from animation import animation_manager

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)

class Wall:
    def __init__(self, screen_width, screen_height):
        self.x = screen_width * 2 // 3  # Position wall at 2/3 of screen width
        self.width = 20
        self.height = screen_height
        self.health = 100
        self.max_health = 100
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Animation properties
        self.hit_flash = 0
        self.hit_y = 0
        
    def draw(self, screen):
        # Draw wall with hit flash effect
        color = BROWN
        if self.hit_flash > 0:
            color = (200, 100, 50) if self.hit_flash % 2 == 0 else BROWN
            self.hit_flash -= 1
            
            # Draw hit effect
            pygame.draw.circle(screen, RED, (int(self.x - self.width//2), int(self.hit_y)), 
                              int(10 * (1 - self.hit_flash / 10)), 2)
            
        # Draw wall
        pygame.draw.rect(screen, color, (self.x - self.width//2, 0, self.width, self.height))
        
        # Draw brick pattern
        for y in range(0, self.height, 20):
            pygame.draw.line(screen, (100, 50, 20), 
                            (self.x - self.width//2, y), 
                            (self.x + self.width//2, y), 1)
            
            # Alternate brick pattern
            offset = 0 if (y // 20) % 2 == 0 else self.width // 2
            for x in range(offset, self.width, self.width):
                pygame.draw.line(screen, (100, 50, 20), 
                                (self.x - self.width//2 + x, y), 
                                (self.x - self.width//2 + x, y + 20), 1)
    
    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash = 10  # Flash for 10 frames
        self.hit_y = self.height * (1 - self.health / self.max_health)  # Hit position based on health
        
        if self.health <= 0:
            self.health = 0
            return True  # Wall destroyed
        return False
        
    def repair(self, amount):
        self.health = min(self.max_health, self.health + amount)
