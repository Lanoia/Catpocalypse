import pygame
import math
import random
from sound_manager import sound_manager
from animation import animation_manager

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)  # Added BLACK color definition

# Enemy types
ENEMY_NORMAL = 0
ENEMY_FAST = 1
ENEMY_TANK = 2

class Enemy:
    def __init__(self, x, y, enemy_type=ENEMY_NORMAL):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.at_wall = False  # Flag to track if enemy has reached the wall
        self.hit_flash = 0  # Flash effect when hit
        
        # Set attributes based on enemy type
        if enemy_type == ENEMY_NORMAL:
            # Normal enemy - medium speed, medium health (3 hits)
            self.width = 30
            self.height = 50
            self.speed = 1.0
            self.health = 75
            self.max_health = 75
            self.color = RED
            self.damage = 5  # Reduced from 10 to 5
        elif enemy_type == ENEMY_FAST:
            # Fast enemy - high speed, low health (2 hits)
            self.width = 25
            self.height = 40
            self.speed = 1.8
            self.health = 50
            self.max_health = 50
            self.color = ORANGE
            self.damage = 5  # Reduced from 8 to 5
        else:  # ENEMY_TANK
            # Tank enemy - low speed, high health (5 hits)
            self.width = 40
            self.height = 60
            self.speed = 0.6
            self.health = 125
            self.max_health = 125
            self.color = PURPLE
            self.damage = 5  # Reduced from 15 to 5
            
        self.attack_cooldown = 0
        self.attack_cooldown_max = 60  # 1 second at 60 FPS
        
        # Animation properties
        self.wobble = 0
        self.wobble_dir = 1
        self.wobble_speed = random.uniform(0.1, 0.2)
        self.wobble_amount = random.uniform(1, 3)
        
        # Placeholder for sprite
        self.sprite_placeholder = True
        
    def update(self, target_x, target_y):
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        # Update hit flash effect
        if self.hit_flash > 0:
            self.hit_flash -= 1
            
        # Update wobble animation
        self.wobble += self.wobble_speed * self.wobble_dir
        if abs(self.wobble) > self.wobble_amount:
            self.wobble_dir *= -1
            
        # Check if at wall
        if abs(self.x - target_x) < 5:
            self.at_wall = True
            return
            
        # Move towards target
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            dx = dx / dist
            dy = dy / dist
            
            self.x += dx * self.speed
            self.y += dy * self.speed
            
    def draw(self, screen):
        # Apply wobble effect to y position
        wobble_offset = self.wobble
        
        # Draw enemy with hit flash effect
        color = self.color
        if self.hit_flash > 0:
            color = (255, 255, 255) if self.hit_flash % 2 == 0 else self.color
            
        # Draw placeholder (will be replaced with sprite later)
        if self.sprite_placeholder:
            # Draw basic cat shape
            pygame.draw.ellipse(screen, color, (self.x - self.width//2, 
                                             self.y - self.height//2 + wobble_offset, 
                                             self.width, self.height))
            
            # Draw cat ears (simple triangle shapes)
            ear_height = 8
            pygame.draw.polygon(screen, BLACK, [
                (self.x - 8, self.y - self.height//2 + wobble_offset + 5),
                (self.x - 12, self.y - self.height//2 + wobble_offset - ear_height),
                (self.x - 4, self.y - self.height//2 + wobble_offset + 5)
            ])
            pygame.draw.polygon(screen, BLACK, [
                (self.x + 8, self.y - self.height//2 + wobble_offset + 5),
                (self.x + 12, self.y - self.height//2 + wobble_offset - ear_height),
                (self.x + 4, self.y - self.height//2 + wobble_offset + 5)
            ])
            
            # Draw eyes
            eye_color = (255, 255, 0)  # Yellow eyes
            pygame.draw.circle(screen, eye_color, 
                              (int(self.x - 5), int(self.y - self.height//4 + wobble_offset)), 3)
            pygame.draw.circle(screen, eye_color, 
                              (int(self.x + 5), int(self.y - self.height//4 + wobble_offset)), 3)
            
            # Draw health bar
            health_bar_width = self.width
            health_bar_height = 3
            health_ratio = self.health / self.max_health
            
            pygame.draw.rect(screen, (255, 0, 0), 
                            (self.x - health_bar_width//2, 
                             self.y - self.height//2 - 10 + wobble_offset, 
                             health_bar_width, health_bar_height))
            pygame.draw.rect(screen, (0, 255, 0), 
                            (self.x - health_bar_width//2, 
                             self.y - self.height//2 - 10 + wobble_offset, 
                             health_bar_width * health_ratio, health_bar_height))
        
    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash = 5  # Flash for 5 frames
        
        # Play hit sound
        sound_manager.play('enemy_hit')
        
        if self.health <= 0:
            # Play death sound
            sound_manager.play('enemy_death')
            
            # Add death animation
            animation_manager.add_explosion(self.x, self.y)
            
            return True  # Enemy died
        return False
        
    def attack_wall(self, wall):
        """Attack the wall if cooldown allows"""
        if self.at_wall and self.attack_cooldown <= 0:
            self.attack_cooldown = self.attack_cooldown_max
            
            # Play wall hit sound
            sound_manager.play('wall_hit')
            
            # Add hit animation
            animation_manager.add_hit(self.x + self.width//2, self.y)
            
            return wall.take_damage(self.damage)
        return False
