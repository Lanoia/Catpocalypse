import pygame
import math
from sound_manager import sound_manager

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

class Player:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 40
        self.height = 60
        self.health = 100
        self.max_health = 100
        self.angle = 0
        self.gun_cooldown = 0
        self.gun_cooldown_max = 15
        self.ammo = 30
        self.max_ammo = 30
        self.reload_time = 0
        self.reload_time_max = 60  # 1 second at 60 FPS
        self.reloading = False
        self.score = 0
        self.kills = 0
        self.speed = 3  # Movement speed
        self.base_speed = 3  # Base movement speed
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        
        # Power-up effects
        self.speed_boost_time = 0
        self.damage_multiplier = 1
        self.damage_boost_time = 0
        
        # New powerup effects
        self.unlimited_ammo = False
        self.unlimited_ammo_time = 0
        self.fire_rate_boost = False
        self.fire_rate_boost_time = 0
        self.gun_cooldown_max_original = self.gun_cooldown_max
        
        # Animation
        self.flash_time = 0
        self.flash_color = None
        
        # Placeholder for sprite
        self.sprite_placeholder = True
        
    def draw(self, screen):
        # Draw player body with flash effect if active
        color = BLUE
        if self.flash_time > 0:
            color = self.flash_color if self.flash_time % 4 < 2 else BLUE
        
        # Draw player placeholder (will be replaced with sprite later)
        if self.sprite_placeholder:
            # Draw player body
            pygame.draw.rect(screen, color, (self.x - self.width//2, self.y - self.height//2, 
                                          self.width, self.height))
            
            # Draw a simple face to indicate this is a placeholder
            pygame.draw.rect(screen, BLACK, (self.x - self.width//2 + 5, self.y - self.height//2 + 5, 
                                          self.width - 10, 15), 1)  # Helmet
            pygame.draw.rect(screen, BLACK, (self.x - 15, self.y - 10, 
                                          30, 20), 1)  # Face outline
            
            # Draw text indicating this is a placeholder
            font = pygame.font.SysFont(None, 12)
            text = font.render("PLAYER", True, BLACK)
            screen.blit(text, (self.x - text.get_width()//2, self.y))
        
        # Draw player gun
        gun_length = 30
        end_x = self.x + math.cos(math.radians(self.angle)) * gun_length
        end_y = self.y + math.sin(math.radians(self.angle)) * gun_length
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 5)
        
        # Draw health bar
        health_bar_width = 50
        health_bar_height = 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - health_bar_width//2, 
                                      self.y - self.height//2 - 15, 
                                      health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - health_bar_width//2, 
                                        self.y - self.height//2 - 15, 
                                        health_bar_width * health_ratio, health_bar_height))
        
        # Draw power-up indicators
        indicator_y = self.y + self.height//2 + 10
        indicator_spacing = 12
        
        # Speed boost indicator
        if self.speed_boost_time > 0:
            pygame.draw.circle(screen, GREEN, (int(self.x - 15), int(indicator_y)), 5)
            
        # Damage boost indicator
        if self.damage_boost_time > 0:
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(indicator_y)), 5)
            
        # Unlimited ammo indicator
        if self.unlimited_ammo:
            pygame.draw.circle(screen, BLUE, (int(self.x + 15), int(indicator_y)), 5)
            
        # Fire rate boost indicator
        if self.fire_rate_boost:
            pygame.draw.circle(screen, ORANGE, (int(self.x + 30), int(indicator_y)), 5)
    
    def update(self, wall_x):
        # Update gun cooldown
        if self.gun_cooldown > 0:
            self.gun_cooldown -= 1
            
        # Update reload time
        if self.reloading:
            self.reload_time -= 1
            if self.reload_time <= 0:
                self.ammo = self.max_ammo
                self.reloading = False
                # Play reload complete sound
                sound_manager.play('reload')
                
        # Update power-up effects
        if self.speed_boost_time > 0:
            self.speed_boost_time -= 1
            if self.speed_boost_time <= 0:
                self.speed = self.base_speed  # Reset speed when boost expires
                
        if self.damage_boost_time > 0:
            self.damage_boost_time -= 1
            if self.damage_boost_time <= 0:
                self.damage_multiplier = 1  # Reset damage multiplier when boost expires
                
        # Update new powerup effects
        if self.unlimited_ammo_time > 0:
            self.unlimited_ammo_time -= 1
            if self.unlimited_ammo_time <= 0:
                self.unlimited_ammo = False
                
        if self.fire_rate_boost_time > 0:
            self.fire_rate_boost_time -= 1
            if self.fire_rate_boost_time <= 0:
                self.fire_rate_boost = False
                self.gun_cooldown_max = self.gun_cooldown_max_original
                
        # Update flash effect
        if self.flash_time > 0:
            self.flash_time -= 1
                
        # Handle movement
        if self.moving_up:
            self.y -= self.speed
        if self.moving_down:
            self.y += self.speed
        if self.moving_left and self.x > wall_x + self.width//2 + 10:  # Don't move past the wall
            self.x -= self.speed
        if self.moving_right and self.x < self.screen_width - self.width//2:
            self.x += self.speed
            
        # Keep player within screen bounds
        if self.y < self.height//2:
            self.y = self.height//2
        if self.y > self.screen_height - self.height//2:
            self.y = self.screen_height - self.height//2
    
    def shoot(self):
        if self.reloading:
            return False
            
        if self.gun_cooldown <= 0:
            if self.unlimited_ammo or self.ammo > 0:
                self.gun_cooldown = self.gun_cooldown_max
                
                # Only decrease ammo if not in unlimited ammo mode
                if not self.unlimited_ammo:
                    self.ammo -= 1
                    
                # Play shoot sound
                sound_manager.play('shoot')
                return True
            elif self.ammo <= 0:
                # Auto-reload when out of ammo
                self.reload()
        return False
    
    def reload(self):
        if not self.reloading and self.ammo < self.max_ammo:
            self.reloading = True
            self.reload_time = self.reload_time_max
            # Play reload sound
            sound_manager.play('reload')
    
    def take_damage(self, damage):
        self.health -= damage
        self.flash(RED, 20)  # Flash red when taking damage
        sound_manager.play('player_hit')
        
        if self.health <= 0:
            self.health = 0
            return True  # Player died
        return False
        
    def flash(self, color, duration=10):
        """Create a flash effect on the player"""
        self.flash_time = duration
        self.flash_color = color
        
    def apply_powerup(self, powerup_type):
        """Apply a power-up effect to the player"""
        # Power-up types: 0=Health, 1=Ammo, 2=Speed, 3=Damage, 4=Wall
        if powerup_type == 0:  # Health
            self.health = min(self.max_health, self.health + 25)
            self.flash(GREEN, 15)
            return "Health +25"
        elif powerup_type == 1:  # Ammo
            self.ammo = self.max_ammo
            self.reloading = False
            self.flash(BLUE, 15)
            return "Ammo Refilled"
        elif powerup_type == 2:  # Speed
            self.speed = self.base_speed * 1.5
            self.speed_boost_time = 300  # 5 seconds
            self.flash(GREEN, 15)
            return "Speed Boost!"
        elif powerup_type == 3:  # Damage
            self.damage_multiplier = 2
            self.damage_boost_time = 300  # 5 seconds
            self.flash(ORANGE, 15)
            return "Damage Boost!"
        return ""
