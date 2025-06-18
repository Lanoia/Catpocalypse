import pygame
import random
import math

# Power-up types
POWERUP_UNLIMITED_AMMO = 0
POWERUP_FIRE_RATE = 1

class PowerUp:
    def __init__(self, x, y, powerup_type=None):
        self.x = x
        self.y = y
        # If powerup_type is not specified, randomly choose one
        self.type = powerup_type if powerup_type is not None else random.randint(0, 1)
        self.radius = 15
        self.pulse_size = 0
        self.pulse_direction = 1
        self.lifetime = 600  # 10 seconds at 60 FPS
        self.colors = {
            POWERUP_UNLIMITED_AMMO: (0, 0, 255),    # Blue for unlimited ammo
            POWERUP_FIRE_RATE: (255, 165, 0)        # Orange for fire rate
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
        if self.type == POWERUP_UNLIMITED_AMMO:
            # Draw infinity symbol
            size = 6
            # Draw the infinity symbol (∞)
            pygame.draw.line(screen, (255, 255, 255), 
                            (self.x - size, self.y), (self.x + size, self.y), 2)
            pygame.draw.arc(screen, (255, 255, 255),
                           (self.x - size, self.y - size//2, size, size), 0, 3.14, 2)
            pygame.draw.arc(screen, (255, 255, 255),
                           (self.x, self.y - size//2, size, size), 0, 3.14, 2)
        elif self.type == POWERUP_FIRE_RATE:
            # Draw lightning bolt for fire rate
            points = [(self.x - 3, self.y - 5), (self.x + 2, self.y - 1), 
                     (self.x - 1, self.y + 1), (self.x + 3, self.y + 5)]
            pygame.draw.lines(screen, (255, 255, 255), False, points, 2)
        
    def is_expired(self):
        return self.lifetime <= 0
        
    def apply_effect(self, player):
        """Apply the power-up effect to the player"""
        effect_duration = 180  # 3 seconds at 60 FPS
        
        if self.type == POWERUP_UNLIMITED_AMMO:
            # Enable unlimited ammo for 3 seconds
            player.unlimited_ammo = True
            player.unlimited_ammo_time = effect_duration
            return "Unlimited Ammo!"
        
        elif self.type == POWERUP_FIRE_RATE:
            # Increase fire rate (decrease cooldown) for 3 seconds
            player.fire_rate_boost = True
            player.fire_rate_boost_time = effect_duration
            # Reduce cooldown by half
            player.gun_cooldown_max_original = player.gun_cooldown_max
            player.gun_cooldown_max = player.gun_cooldown_max // 2
            return "Fire Rate Boost!"
            
        return "Power-up!"

def spawn_random_powerup(min_x, max_x, min_y, max_y):
    """Spawn a random power-up within the given boundaries"""
    x = random.randint(min_x, max_x)
    y = random.randint(min_y, max_y)
    return PowerUp(x, y)
