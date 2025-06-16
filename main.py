import pygame
import sys
import random
import math
from pygame.locals import *

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
LIGHT_GRAY = (200, 200, 200)  # For background
ORANGE = (255, 165, 0)  # For enemy type 2
PURPLE = (128, 0, 128)  # For enemy type 3

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Enemy types
ENEMY_NORMAL = 0
ENEMY_FAST = 1
ENEMY_TANK = 2

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
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
        self.reload_time_max = 120  # 2 seconds at 60 FPS
        self.reloading = False
        self.score = 0
        self.kills = 0
        self.speed = 3  # Movement speed
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        
    def draw(self, screen):
        # Draw player body
        pygame.draw.rect(screen, BLUE, (self.x - self.width//2, self.y - self.height//2, 
                                        self.width, self.height))
        
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
                
        # Handle movement
        if self.moving_up:
            self.y -= self.speed
        if self.moving_down:
            self.y += self.speed
        if self.moving_left and self.x > wall_x + self.width//2 + 10:  # Don't move past the wall
            self.x -= self.speed
        if self.moving_right and self.x < SCREEN_WIDTH - self.width//2:
            self.x += self.speed
            
        # Keep player within screen bounds
        if self.y < self.height//2:
            self.y = self.height//2
        if self.y > SCREEN_HEIGHT - self.height//2:
            self.y = SCREEN_HEIGHT - self.height//2
    
    def shoot(self):
        if not self.reloading and self.gun_cooldown <= 0 and self.ammo > 0:
            self.gun_cooldown = self.gun_cooldown_max
            self.ammo -= 1
            return True
        return False
    
    def reload(self):
        if not self.reloading and self.ammo < self.max_ammo:
            self.reloading = True
            self.reload_time = self.reload_time_max
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            return True  # Player died
        return False

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.radius = 3
        self.damage = 25
        self.lifetime = 60  # 1 second at 60 FPS
        
    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        self.lifetime -= 1
        
    def draw(self, screen):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
        
    def is_dead(self):
        return self.lifetime <= 0 or self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT

class Enemy:
    def __init__(self, x, y, enemy_type=ENEMY_NORMAL):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.at_wall = False  # Flag to track if enemy has reached the wall
        
        # Set attributes based on enemy type
        if enemy_type == ENEMY_NORMAL:
            # Normal enemy - medium speed, medium health (3 hits)
            self.width = 30
            self.height = 50
            self.speed = 1.0
            self.health = 75
            self.max_health = 75
            self.color = RED
        elif enemy_type == ENEMY_FAST:
            # Fast enemy - high speed, low health (2 hits)
            self.width = 25
            self.height = 40
            self.speed = 1.8
            self.health = 50
            self.max_health = 50
            self.color = ORANGE
        else:  # ENEMY_TANK
            # Tank enemy - low speed, high health (5 hits)
            self.width = 40
            self.height = 60
            self.speed = 0.6
            self.health = 125
            self.max_health = 125
            self.color = PURPLE
            
        self.attack_cooldown = 0
        self.attack_cooldown_max = 60  # 1 second at 60 FPS
        
    def draw(self, screen):
        # Draw enemy body
        pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y - self.height//2, 
                                      self.width, self.height))
        
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
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

class Wall:
    def __init__(self):
        self.x = SCREEN_WIDTH * 2 // 3  # Position wall at 2/3 of screen width
        self.width = 20
        self.height = SCREEN_HEIGHT
        self.health = 100
        self.max_health = 100
        
    def draw(self, screen):
        # Draw wall
        pygame.draw.rect(screen, BROWN, (self.x - self.width//2, 0, self.width, self.height))
        
        # Draw health bar at the top of the screen
        health_bar_width = 200
        health_bar_height = 10
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH//2 - health_bar_width//2, 20, 
                                      health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - health_bar_width//2, 20, 
                                        health_bar_width * health_ratio, health_bar_height))
        
        # Draw wall health text
        font = pygame.font.SysFont(None, 24)
        health_text = font.render(f"Wall: {self.health}/{self.max_health}", True, BLACK)
        text_x = SCREEN_WIDTH//2 - health_text.get_width()//2
        text_y = 35
        screen.blit(health_text, (text_x, text_y))
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Catpocalypse")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.state = MENU
        self.wave = 1
        self.wave_timer = 0
        self.wave_cooldown = 300  # 5 seconds at 60 FPS
        self.enemies_per_wave = 5
        self.reset_game()
        
    def reset_game(self):
        # Position player behind the wall
        self.player = Player(SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2)  # Position player at 5/6 of screen width
        self.bullets = []
        self.enemies = []
        self.wall = Wall()  # Add the wall
        # Remove the barricades as we're using a wall now
        self.barricades = []
        self.wave = 1
        self.wave_timer = self.wave_cooldown
        self.spawning_wave = False
        
    def spawn_wave(self):
        self.spawning_wave = True
        enemies_to_spawn = self.enemies_per_wave + (self.wave - 1) * 2
        
        for i in range(enemies_to_spawn):
            # Spawn enemies only from the left side
            x = -50
            y = random.randint(50, SCREEN_HEIGHT - 50)
            
            # Determine enemy type based on wave and random chance
            if self.wave < 3:
                # Early waves: mostly normal enemies, some fast enemies
                enemy_type = ENEMY_NORMAL if random.random() < 0.8 else ENEMY_FAST
            elif self.wave < 5:
                # Mid waves: mix of all types, but more normal enemies
                rand = random.random()
                if rand < 0.6:
                    enemy_type = ENEMY_NORMAL
                elif rand < 0.85:
                    enemy_type = ENEMY_FAST
                else:
                    enemy_type = ENEMY_TANK
            else:
                # Later waves: even distribution of all types
                enemy_type = random.choice([ENEMY_NORMAL, ENEMY_FAST, ENEMY_TANK])
                
            self.enemies.append(Enemy(x, y, enemy_type))
        
        self.spawning_wave = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.state == PLAYING:
                        self.state = MENU
                    elif self.state == MENU:
                        pygame.quit()
                        sys.exit()
                        
                if self.state == MENU and event.key == K_RETURN:
                    self.reset_game()
                    self.state = PLAYING
                    
                if self.state == GAME_OVER and event.key == K_RETURN:
                    self.state = MENU
                    
                if self.state == PLAYING and event.key == K_r:
                    self.player.reload()
                    
                # Player movement
                if self.state == PLAYING:
                    if event.key == K_w or event.key == K_UP:
                        self.player.moving_up = True
                    if event.key == K_s or event.key == K_DOWN:
                        self.player.moving_down = True
                    if event.key == K_a or event.key == K_LEFT:
                        self.player.moving_left = True
                    if event.key == K_d or event.key == K_RIGHT:
                        self.player.moving_right = True
                    
            if event.type == KEYUP:
                if self.state == PLAYING:
                    if event.key == K_w or event.key == K_UP:
                        self.player.moving_up = False
                    if event.key == K_s or event.key == K_DOWN:
                        self.player.moving_down = False
                    if event.key == K_a or event.key == K_LEFT:
                        self.player.moving_left = False
                    if event.key == K_d or event.key == K_RIGHT:
                        self.player.moving_right = False
                    
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.state == PLAYING:
                    if self.player.shoot():
                        # Create a new bullet
                        bullet_x = self.player.x + math.cos(math.radians(self.player.angle)) * 30
                        bullet_y = self.player.y + math.sin(math.radians(self.player.angle)) * 30
                        self.bullets.append(Bullet(bullet_x, bullet_y, self.player.angle))
                        
    def update(self):
        if self.state == PLAYING:
            # Update player angle based on mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.player.x
            dy = mouse_y - self.player.y
            self.player.angle = math.degrees(math.atan2(dy, dx))
            
            # Update player
            self.player.update(self.wall.x)
            
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update()
                if bullet.is_dead():
                    self.bullets.remove(bullet)
                    
            # Update enemies
            for enemy in self.enemies[:]:
                # Calculate the target position just in front of the wall
                target_x = self.wall.x - enemy.width//2 - self.wall.width//2
                target_y = enemy.y  # Keep the same y-coordinate to move straight to the wall
                
                # If enemy hasn't reached the wall yet, move towards it
                if not enemy.at_wall:
                    # Calculate direction to target
                    dx = target_x - enemy.x
                    dy = target_y - enemy.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    # If very close to target, mark as at wall
                    if dist < 2:
                        enemy.at_wall = True
                        enemy.x = target_x  # Snap to exact position
                    elif dist > 0:
                        # Move towards wall
                        dx /= dist
                        dy /= dist
                        enemy.x += dx * enemy.speed
                        enemy.y += dy * enemy.speed
                
                # Update attack cooldown
                if enemy.attack_cooldown > 0:
                    enemy.attack_cooldown -= 1
                
                # If at wall, attack when cooldown allows
                if enemy.at_wall:
                    if enemy.attack_cooldown <= 0:
                        enemy.attack_cooldown = enemy.attack_cooldown_max
                        if self.wall.take_damage(10):  # Wall takes 10 damage per attack
                            self.state = GAME_OVER
                
            # Check bullet collisions with enemies
            for bullet in self.bullets[:]:
                for enemy in self.enemies[:]:
                    if (abs(bullet.x - enemy.x) < enemy.width // 2 and
                        abs(bullet.y - enemy.y) < enemy.height // 2):
                        if enemy.take_damage(bullet.damage):
                            self.enemies.remove(enemy)
                            self.player.score += 100
                            self.player.kills += 1
                        if bullet in self.bullets:  # Check if bullet still exists
                            self.bullets.remove(bullet)
                        break
            
            # Wave management
            if len(self.enemies) == 0 and not self.spawning_wave:
                if self.wave_timer > 0:
                    self.wave_timer -= 1
                else:
                    self.wave += 1
                    self.spawn_wave()
                    self.wave_timer = self.wave_cooldown
    
    def draw(self):
        self.screen.fill(WHITE)
        
        if self.state == MENU:
            title = self.font.render("CATPOCALYPSE", True, BLACK)
            subtitle = self.small_font.render("A Survival Defense Shooter", True, BLACK)
            instruction = self.small_font.render("Press ENTER to start", True, BLACK)
            
            # Draw enemy type information
            enemy_info = [
                "Enemy Types:",
                "Red: Normal - 3 hits to kill",
                "Orange: Fast - 2 hits to kill",
                "Purple: Tank - 5 hits to kill"
            ]
            
            y_offset = SCREEN_HEIGHT//2 + 80
            for info in enemy_info:
                info_text = self.small_font.render(info, True, BLACK)
                self.screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, y_offset))
                y_offset += 25
            
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, SCREEN_HEIGHT//2))
            self.screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT//2 + 50))
            
        elif self.state == PLAYING:
            # Draw background - different colors for left and right of wall
            pygame.draw.rect(self.screen, LIGHT_GRAY, (0, 0, self.wall.x, SCREEN_HEIGHT))  # Enemy area
            pygame.draw.rect(self.screen, GRAY, (self.wall.x, 0, SCREEN_WIDTH - self.wall.x, SCREEN_HEIGHT))  # Player area
            
            # Draw wall
            self.wall.draw(self.screen)
            
            # Draw bullets
            for bullet in self.bullets:
                bullet.draw(self.screen)
                
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            # Draw player
            self.player.draw(self.screen)
            
            # Draw HUD
            # Health
            health_text = self.small_font.render(f"Health: {self.player.health}/{self.player.max_health}", True, BLACK)
            self.screen.blit(health_text, (10, 10))
            
            # Ammo
            ammo_text = self.small_font.render(f"Ammo: {self.player.ammo}/{self.player.max_ammo}", True, BLACK)
            self.screen.blit(ammo_text, (10, 40))
            
            # Wave
            wave_text = self.small_font.render(f"Wave: {self.wave}", True, BLACK)
            self.screen.blit(wave_text, (SCREEN_WIDTH - 100, 10))
            
            # Score
            score_text = self.small_font.render(f"Score: {self.player.score}", True, BLACK)
            self.screen.blit(score_text, (SCREEN_WIDTH - 150, 40))
            
            # Reload indicator
            if self.player.reloading:
                reload_text = self.small_font.render("Reloading...", True, RED)
                self.screen.blit(reload_text, (10, 70))
                
            # Wave timer
            if len(self.enemies) == 0 and self.wave_timer > 0:
                next_wave_text = self.small_font.render(f"Next wave in: {self.wave_timer // 60 + 1}", True, BLACK)
                self.screen.blit(next_wave_text, (SCREEN_WIDTH//2 - 80, 10))
                
        elif self.state == GAME_OVER:
            game_over_text = self.font.render("GAME OVER", True, RED)
            
            # Show different message based on what caused game over
            reason_text = self.small_font.render("Your wall was destroyed!", True, BLACK)
                
            score_text = self.small_font.render(f"Final Score: {self.player.score}", True, BLACK)
            kills_text = self.small_font.render(f"Enemies Killed: {self.player.kills}", True, BLACK)
            wave_text = self.small_font.render(f"Survived until wave: {self.wave}", True, BLACK)
            instruction = self.small_font.render("Press ENTER to return to menu", True, BLACK)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(reason_text, (SCREEN_WIDTH//2 - reason_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(kills_text, (SCREEN_WIDTH//2 - kills_text.get_width()//2, SCREEN_HEIGHT//2 + 10))
            self.screen.blit(wave_text, (SCREEN_WIDTH//2 - wave_text.get_width()//2, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT//2 + 80))
            
        pygame.display.flip()
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
