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
            self.damage = 10
        elif enemy_type == ENEMY_FAST:
            # Fast enemy - high speed, low health (2 hits)
            self.width = 25
            self.height = 40
            self.speed = 1.8
            self.health = 50
            self.max_health = 50
            self.color = ORANGE
            self.damage = 8
        else:  # ENEMY_TANK
            # Tank enemy - low speed, high health (5 hits)
            self.width = 40
            self.height = 60
            self.speed = 0.6
            self.health = 125
            self.max_health = 125
            self.color = PURPLE
            self.damage = 15
            
        self.attack_cooldown = 0
        self.attack_cooldown_max = 60  # 1 second at 60 FPS
        
        # Animation properties
        self.wobble = 0
        self.wobble_dir = 1
        self.wobble_speed = random.uniform(0.1, 0.2)
        
        # Placeholder for sprite
        self.sprite_placeholder = True
        
    def draw(self, screen):
        # Calculate wobble effect
        wobble_offset = math.sin(self.wobble) * 2
        
        # Draw enemy body with hit flash effect
        color = self.color
        if self.hit_flash > 0:
            color = (255, 255, 255) if self.hit_flash % 2 == 0 else self.color
            self.hit_flash -= 1
            
        # Draw enemy with wobble effect
        pygame.draw.rect(screen, color, 
                        (self.x - self.width//2, 
                         self.y - self.height//2 + wobble_offset, 
                         self.width, self.height))
        
        # Draw placeholder indicator (will be replaced with sprite later)
        if self.sprite_placeholder:
            # Draw a simple cat silhouette placeholder
            if self.enemy_type == ENEMY_NORMAL:
                type_text = "NORMAL"
            elif self.enemy_type == ENEMY_FAST:
                type_text = "FAST"
            else:
                type_text = "TANK"
                
            # Draw text indicating this is a placeholder
            font = pygame.font.SysFont(None, 12)
            text = font.render(f"CAT {type_text}", True, BLACK)
            screen.blit(text, (self.x - text.get_width()//2, self.y))
            
            # Draw cat ears (simple triangle shapes)
            ear_height = 8
            pygame.draw.polygon(screen, BLACK, [
                (self.x - 8, self.y - self.height//2 + wobble_offset + 5),
                (self.x - 12, self.y - self.height//2 + wobble_offset - ear_height),
                (self.x - 4, self.y - self.height//2 + wobble_offset - 2)
            ], 1)
            pygame.draw.polygon(screen, BLACK, [
                (self.x + 8, self.y - self.height//2 + wobble_offset + 5),
                (self.x + 12, self.y - self.height//2 + wobble_offset - ear_height),
                (self.x + 4, self.y - self.height//2 + wobble_offset - 2)
            ], 1)
        
        # Draw health bar
        health_bar_width = 40
        health_bar_height = 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - health_bar_width//2, 
                                      self.y - self.height//2 - 10, 
                                      health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - health_bar_width//2, 
                                        self.y - self.height//2 - 10, 
                                        health_bar_width * health_ratio, health_bar_height))
                                        
        # Draw attack indicator if at wall and cooldown is low
        if self.at_wall and self.attack_cooldown < 15:
            indicator_size = int(15 * (1 - self.attack_cooldown / 15))
            pygame.draw.circle(screen, (255, 0, 0, 128), 
                              (int(self.x + self.width//2), int(self.y)), 
                              indicator_size, 2)
    
    def update(self, target_x, target_y):
        # Update wobble animation
        self.wobble += self.wobble_speed
        if self.wobble > math.pi * 2:
            self.wobble -= math.pi * 2
            
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        # If not at wall, move towards target
        if not self.at_wall:
            # Calculate direction to target
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # If very close to target, mark as at wall
            if dist < 2:
                self.at_wall = True
                self.x = target_x  # Snap to exact position
            elif dist > 0:
                # Move towards wall
                dx /= dist
                dy /= dist
                self.x += dx * self.speed
                self.y += dy * self.speed
    
    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash = 6  # Flash for 6 frames
        
        # Play hit sound
        sound_manager.play('enemy_hit')
        
        # Add hit animation
        animation_manager.add_hit(self.x, self.y)
        
        if self.health <= 0:
            # Play death sound
            sound_manager.play('enemy_death')
            
            # Add explosion animation
            animation_manager.add_explosion(self.x, self.y)
            return True
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
