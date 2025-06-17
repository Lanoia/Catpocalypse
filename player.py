import pygame
import math
import os
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
        
        # Animation state
        self.is_moving = False
        self.is_shooting = False
        self.animation_frame = 0
        self.animation_speed = 0.2  # Lower is faster
        self.animation_timer = 0
        self.facing_left = True  # Default facing left
        
        # Player sprites
        self.idle_sprite = None
        self.run_sprite = None
        
        # Gun sprites
        self.gun_sprites = {
            'default': None,
            'fire_rate_boost': None
        }
        self.gun_offset = (0, 0)  # Offset from player center
        
        # Load sprites
        self.load_sprites()
        
    def load_sprites(self):
        """Load player sprites and prepare animations"""
        try:
            # Base paths
            base_path = os.path.join("assets", "player")
            gun_path = os.path.join("assets", "gun")
            
            # Load the player sprites
            self.idle_sprite = pygame.image.load(os.path.join(base_path, "__Cat_Idle_000.png")).convert_alpha()
            self.run_sprite = pygame.image.load(os.path.join(base_path, "__Cat_Run_000.png")).convert_alpha()
            
            # Scale the sprites to match player dimensions
            scale_factor = 0.5  # Adjust as needed
            self.sprite_width = int(self.width * 2)  # Make sprite wider than player hitbox
            self.sprite_height = int(self.height * 2)  # Make sprite taller than player hitbox
            
            self.idle_sprite = pygame.transform.scale(self.idle_sprite, (self.sprite_width, self.sprite_height))
            self.run_sprite = pygame.transform.scale(self.run_sprite, (self.sprite_width, self.sprite_height))
            
            # Create horizontally flipped versions (mirror images)
            self.idle_sprite = pygame.transform.flip(self.idle_sprite, True, False)
            self.run_sprite = pygame.transform.flip(self.run_sprite, True, False)
            
            # Load gun sprites
            try:
                # Default gun (pistol)
                default_gun = pygame.image.load(os.path.join(gun_path, "pistol.png")).convert_alpha()
                # Create horizontally flipped version (mirror image)
                default_gun = pygame.transform.flip(default_gun, True, False)
                self.gun_sprites['default'] = default_gun
                
                # Fire rate boost gun (submachine)
                boost_gun = pygame.image.load(os.path.join(gun_path, "submachine.png")).convert_alpha()
                # Create horizontally flipped version (mirror image)
                boost_gun = pygame.transform.flip(boost_gun, True, False)
                self.gun_sprites['fire_rate_boost'] = boost_gun
                
                print("Gun sprites loaded and flipped successfully")
            except Exception as e:
                print(f"Error loading gun sprites: {e}")
                # If gun sprites fail to load, we'll use the line drawing fallback
            
            # Set sprite placeholder to False since we loaded the sprite
            self.sprite_placeholder = False
            
            print("Player sprites loaded and flipped successfully")
        except Exception as e:
            print(f"Error loading player sprite: {e}")
            # If loading fails, use placeholder
            self.sprite_placeholder = True
        
    def draw(self, screen):
        # Determine which sprite to use based on player state
        current_sprite = self.idle_sprite
        if self.is_moving:
            current_sprite = self.run_sprite
        
        # Draw player with flash effect if active
        color = BLUE
        if self.flash_time > 0:
            color = self.flash_color if self.flash_time % 4 < 2 else BLUE
        
        if not self.sprite_placeholder and current_sprite:
            # Calculate position to center the sprite on player coordinates
            sprite_x = self.x - self.sprite_width // 2
            sprite_y = self.y - self.sprite_height // 2
            
            # Apply flash effect if active
            if self.flash_time > 0 and self.flash_time % 4 < 2:
                # Create a copy of the sprite and apply a color overlay
                sprite_copy = current_sprite.copy()
                overlay = pygame.Surface(sprite_copy.get_size(), pygame.SRCALPHA)
                overlay.fill((*self.flash_color, 128))  # Add alpha value
                sprite_copy.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(sprite_copy, (sprite_x, sprite_y))
            else:
                screen.blit(current_sprite, (sprite_x, sprite_y))
        else:
            # Draw player placeholder (will be replaced with sprite later)
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
        
        # Draw player gun - choose between sprite and line drawing
        gun_length = 30
        end_x = self.x + math.cos(math.radians(self.angle)) * gun_length
        end_y = self.y + math.sin(math.radians(self.angle)) * gun_length
        
        # Determine which gun sprite to use
        gun_key = 'fire_rate_boost' if self.fire_rate_boost else 'default'
        gun_sprite = self.gun_sprites.get(gun_key)
        
        if gun_sprite:
            # Scale gun sprite - INCREASED SIZE
            gun_scale = 1.0  # Adjust as needed
            gun_width = int(gun_sprite.get_width() * gun_scale)
            gun_height = int(gun_sprite.get_height() * gun_scale)
            scaled_gun = pygame.transform.scale(gun_sprite, (gun_width, gun_height))
            
            # Rotate gun sprite to match player's aim angle
            rotated_gun = pygame.transform.rotate(scaled_gun, -self.angle)  # Negative angle for correct rotation
            
            # Calculate position to place the gun - adjusted for larger size
            # Offset the gun position to better align with the player
            offset_distance = 20  # Distance from player center
            offset_x = math.cos(math.radians(self.angle)) * offset_distance
            offset_y = math.sin(math.radians(self.angle)) * offset_distance
            
            gun_x = self.x - rotated_gun.get_width() // 2 + offset_x
            gun_y = self.y - rotated_gun.get_height() // 2 + offset_y
            
            # Draw the gun sprite
            screen.blit(rotated_gun, (gun_x, gun_y))
        else:
            # Fallback to line drawing if sprites aren't available
            pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 5)
        
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
        self.is_moving = False
        if self.moving_up:
            self.y -= self.speed
            self.is_moving = True
        if self.moving_down:
            self.y += self.speed
            self.is_moving = True
        if self.moving_left and self.x > wall_x + self.width//2 + 10:  # Don't move past the wall
            self.x -= self.speed
            self.is_moving = True
        if self.moving_right and self.x < self.screen_width - self.width//2:
            self.x += self.speed
            self.is_moving = True
            
        # Keep player within screen bounds
        if self.y < self.height//2:
            self.y = self.height//2
        if self.y > self.screen_height - self.height//2:
            self.y = self.screen_height - self.height//2
            
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= 3:  # Faster animation update
            self.animation_timer = 0
            self.animation_frame += 1
            
        # Reset shooting flag (will be set to true when shoot() is called)
        self.is_shooting = False
    
    def shoot(self):
        if self.reloading:
            return False
            
        if self.gun_cooldown <= 0:
            if self.unlimited_ammo or self.ammo > 0:
                self.gun_cooldown = self.gun_cooldown_max
                
                # Only decrease ammo if not in unlimited ammo mode
                if not self.unlimited_ammo:
                    self.ammo -= 1
                    
                # Set shooting flag for animation
                self.is_shooting = True
                    
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
