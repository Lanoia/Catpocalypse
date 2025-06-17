import pygame
import random
import math

# Power-up types
POWERUP_HEALTH = 0
POWERUP_AMMO = 1
POWERUP_SPEED = 2
POWERUP_DAMAGE = 3
POWERUP_WALL = 4

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.radius = 15
        self.pulse_size = 0
        self.pulse_direction = 1
        self.lifetime = 600  # 10 seconds at 60 FPS
        self.colors = {
            POWERUP_HEALTH: (255, 0, 0),      # Red for health
            POWERUP_AMMO: (0, 0, 255),        # Blue for ammo
            POWERUP_SPEED: (0, 255, 0),       # Green for speed
            POWERUP_DAMAGE: (255, 165, 0),    # Orange for damage
            POWERUP_WALL: (139, 69, 19)       # Brown for wall repair
        }
        self.color = self.colors.get(self.type, (255, 255, 0))  # Default to yellow
        
    def update(self):
        # Create a pulsing effect
        self.pulse_size += 0.2 * self.pulse_direction
        if self.pulse_size > 5:
            self.pulse_direction = -1
        elif self.pulse_size < -3:
            self.pulse_direction = 1
            
        # Decrease lifetime
        self.lifetime -= 1
        
    def draw(self, screen):
        # Draw the power-up with a pulsing effect
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 
                          int(self.radius + self.pulse_size))
        
        # Draw an icon or symbol based on the power-up type
        if self.type == POWERUP_HEALTH:
            # Draw a plus sign
            pygame.draw.line(screen, (255, 255, 255), 
                            (self.x - 5, self.y), (self.x + 5, self.y), 2)
            pygame.draw.line(screen, (255, 255, 255), 
                            (self.x, self.y - 5), (self.x, self.y + 5), 2)
        elif self.type == POWERUP_AMMO:
            # Draw a bullet symbol
            pygame.draw.rect(screen, (255, 255, 255), 
                            (self.x - 2, self.y - 5, 4, 10))
        elif self.type == POWERUP_SPEED:
            # Draw a lightning bolt
            points = [(self.x - 3, self.y - 5), (self.x + 2, self.y - 1), 
                     (self.x - 1, self.y + 1), (self.x + 3, self.y + 5)]
            pygame.draw.lines(screen, (255, 255, 255), False, points, 2)
        elif self.type == POWERUP_DAMAGE:
            # Draw a star
            pygame.draw.polygon(screen, (255, 255, 255), 
                               [(self.x, self.y - 5), (self.x + 2, self.y - 2), 
                                (self.x + 5, self.y - 2), (self.x + 3, self.y + 1),
                                (self.x + 4, self.y + 4), (self.x, self.y + 2),
                                (self.x - 4, self.y + 4), (self.x - 3, self.y + 1),
                                (self.x - 5, self.y - 2), (self.x - 2, self.y - 2)])
        elif self.type == POWERUP_WALL:
            # Draw a brick pattern
            pygame.draw.rect(screen, (255, 255, 255), 
                            (self.x - 5, self.y - 3, 10, 6), 1)
            pygame.draw.line(screen, (255, 255, 255), 
                            (self.x, self.y - 3), (self.x, self.y + 3), 1)
        
    def is_expired(self):
        return self.lifetime <= 0
        
    def apply_effect(self, player, wall):
        """Apply the power-up effect to the player or wall"""
        if self.type == POWERUP_HEALTH:
            # Restore 25 health points, up to max health
            player.health = min(player.max_health, player.health + 25)
            return "Health +25"
        
        elif self.type == POWERUP_AMMO:
            # Restore full ammo and cancel reload if reloading
            player.ammo = player.max_ammo
            player.reloading = False
            return "Ammo Refilled"
        
        elif self.type == POWERUP_SPEED:
            # Increase player speed by 50% for 5 seconds
            player.speed *= 1.5
            player.speed_boost_time = 300  # 5 seconds at 60 FPS
            return "Speed Boost!"
        
        elif self.type == POWERUP_DAMAGE:
            # Double bullet damage for 5 seconds
            player.damage_multiplier = 2
            player.damage_boost_time = 300  # 5 seconds at 60 FPS
            return "Damage Boost!"
        
        elif self.type == POWERUP_WALL:
            # Repair wall by 25 health points, up to max health
            wall.health = min(wall.max_health, wall.health + 25)
            return "Wall Repaired"
            
        return "Power-up!"

def spawn_random_powerup(min_x, max_x, min_y, max_y):
    """Spawn a random power-up within the given boundaries"""
    x = random.randint(min_x, max_x)
    y = random.randint(min_y, max_y)
    powerup_type = random.randint(0, 4)  # Random type from 0 to 4
    return PowerUp(x, y, powerup_type)
