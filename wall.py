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
        
        # Draw health bar at the top of the screen
        health_bar_width = 200
        health_bar_height = 10
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.screen_width//2 - health_bar_width//2, 20, 
                                      health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (self.screen_width//2 - health_bar_width//2, 20, 
                                        health_bar_width * health_ratio, health_bar_height))
        
        # Draw wall health text
        font = pygame.font.SysFont(None, 24)
        health_text = font.render(f"Wall: {self.health}/{self.max_health}", True, BLACK)
        text_x = self.screen_width//2 - health_text.get_width()//2
        text_y = 35
        screen.blit(health_text, (text_x, text_y))
    
    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash = 10  # Flash for 10 frames
        self.hit_y = self.height * (1 - self.health / self.max_health)  # Hit position based on health
        
        # Add hit animation
        animation_manager.add_hit(self.x - self.width//2, self.hit_y)
        
        # Add text animation showing damage
        animation_manager.add_text(self.x - 30, self.hit_y, f"-{damage}", (255, 0, 0), 20)
        
        return self.health <= 0
        
    def repair(self, amount):
        """Repair the wall by the specified amount"""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        
        # Add text animation showing repair amount
        repair_amount = self.health - old_health
        if repair_amount > 0:
            animation_manager.add_text(self.x - 30, self.height // 2, f"+{repair_amount}", (0, 255, 0), 24)
            
        return self.health
