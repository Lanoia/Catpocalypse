import pygame
import math
import random
import os
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
            self.damage = 5
            self.scale_factor = 1.0  # Normal size
        elif enemy_type == ENEMY_FAST:
            # Fast enemy - high speed, low health (2 hits)
            self.width = 25
            self.height = 40
            self.speed = 1.8
            self.health = 50
            self.max_health = 50
            self.color = ORANGE
            self.damage = 5
            self.scale_factor = 0.8  # Smaller size
        else:  # ENEMY_TANK
            # Tank enemy - low speed, high health (5 hits)
            self.width = 40
            self.height = 60
            self.speed = 0.6
            self.health = 125
            self.max_health = 125
            self.color = PURPLE
            self.damage = 5
            self.scale_factor = 1.2  # Larger size
            
        self.attack_cooldown = 0
        self.attack_cooldown_max = 60  # 1 second at 60 FPS
        
        # Animation properties
        self.wobble = 0
        self.wobble_dir = 1
        self.wobble_speed = random.uniform(0.1, 0.2)
        self.wobble_amount = random.uniform(1, 3)
        
        # Sprite properties
        self.sprite = None
        self.sprite_width = int(self.width * 2)
        self.sprite_height = int(self.height * 2)
        self.sprite_placeholder = True
        
        # Load sprite
        self.load_sprite()
        
    def load_sprite(self):
        """Load enemy sprite"""
        try:
            # Get the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Get the assets directory path - one level up from script_dir, then into assets
            assets_dir = os.path.join(os.path.dirname(script_dir), 'assets')
            
            # Base path
            sprite_path = os.path.join(assets_dir, "images", "enemy", "New Piskel (7).png")
            
            print(f"Loading enemy sprite from: {sprite_path}")
            
            # Load the sprite
            self.sprite = pygame.image.load(sprite_path).convert_alpha()
            
            # Scale the sprite based on enemy type
            scaled_width = int(self.sprite_width * self.scale_factor)
            scaled_height = int(self.sprite_height * self.scale_factor)
            self.sprite = pygame.transform.scale(self.sprite, (scaled_width, scaled_height))
            
            # Apply color tint based on enemy type
            if self.enemy_type == ENEMY_NORMAL:
                # Normal enemy - red tint
                self.apply_color_tint(RED)
            elif self.enemy_type == ENEMY_FAST:
                # Fast enemy - orange tint
                self.apply_color_tint(ORANGE)
            else:  # ENEMY_TANK
                # Tank enemy - purple tint
                self.apply_color_tint(PURPLE)
            
            # Set sprite placeholder to False since we loaded the sprite
            self.sprite_placeholder = False
            
            print(f"Enemy sprite loaded successfully for type {self.enemy_type}")
        except Exception as e:
            print(f"Error loading enemy sprite: {e}")
            # If loading fails, use placeholder
            self.sprite_placeholder = True
            
    def apply_color_tint(self, color):
        """Apply a color tint to the sprite"""
        if self.sprite:
            # Create a copy of the sprite
            tinted_sprite = self.sprite.copy()
            
            # Create a surface with the tint color
            tint = pygame.Surface(tinted_sprite.get_size(), pygame.SRCALPHA)
            tint.fill((color[0], color[1], color[2], 100))  # Semi-transparent color
            
            # Apply the tint
            tinted_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Update the sprite
            self.sprite = tinted_sprite
        
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
            
        if not self.sprite_placeholder and self.sprite:
            # Calculate position to center the sprite on enemy coordinates
            sprite_x = self.x - self.sprite.get_width() // 2
            sprite_y = self.y - self.sprite.get_height() // 2 + wobble_offset
            
            # Apply flash effect if active
            if self.hit_flash > 0 and self.hit_flash % 2 == 0:
                # Create a copy of the sprite and apply a white overlay
                sprite_copy = self.sprite.copy()
                overlay = pygame.Surface(sprite_copy.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 150))  # Semi-transparent white
                sprite_copy.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(sprite_copy, (sprite_x, sprite_y))
            else:
                screen.blit(self.sprite, (sprite_x, sprite_y))
                
            # Draw health bar
            health_bar_width = self.sprite.get_width()
            health_bar_height = 3
            health_ratio = self.health / self.max_health
            
            pygame.draw.rect(screen, (255, 0, 0), 
                            (sprite_x, 
                             sprite_y - 10, 
                             health_bar_width, health_bar_height))
            pygame.draw.rect(screen, (0, 255, 0), 
                            (sprite_x, 
                             sprite_y - 10, 
                             health_bar_width * health_ratio, health_bar_height))
        else:
            # Draw placeholder (will be replaced with sprite later)
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
