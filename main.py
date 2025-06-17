import pygame
import sys
import random
import math
import os
from pygame.locals import *

# Import our modules
from player import Player
from enemy import Enemy, ENEMY_NORMAL, ENEMY_FAST, ENEMY_TANK
from wall import Wall
from bullet import Bullet
from powerup import PowerUp, spawn_random_powerup, POWERUP_UNLIMITED_AMMO, POWERUP_FIRE_RATE
from sound_manager import sound_manager
from settings import game_settings, DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD
from animation import animation_manager

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3
SETTINGS = 4

class Game:
    def __init__(self):
        # Set up display
        self.screen_flags = 0
        if game_settings.fullscreen:
            self.screen_flags = pygame.FULLSCREEN
            
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), self.screen_flags)
        pygame.display.set_caption("Catpocalypse")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 48)
        
        # Game state
        self.state = MENU
        self.wave = 1
        self.wave_timer = 0
        self.wave_cooldown = 300  # 5 seconds at 60 FPS
        self.enemies_per_wave = 5
        
        # Set volume from settings
        sound_manager.set_volume(game_settings.sound_volume)
        sound_manager.set_music_volume(game_settings.music_volume)
        
        # Start background music
        sound_manager.play_music()
        
        # Reset game
        self.reset_game()
        
    def reset_game(self):
        # Create wall
        self.wall = Wall(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Apply difficulty settings to wall health
        wall_health_multiplier = game_settings.get_difficulty_setting('wall_health_multiplier')
        self.wall.max_health = int(100 * wall_health_multiplier)
        self.wall.health = self.wall.max_health
        
        # Position player behind the wall
        self.player = Player(SCREEN_WIDTH * 5 // 6, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Apply difficulty settings to player health
        player_health_multiplier = game_settings.get_difficulty_setting('player_health_multiplier')
        self.player.max_health = int(100 * player_health_multiplier)
        self.player.health = self.player.max_health
        
        self.bullets = []
        self.enemies = []
        self.powerups = []
        self.wave = 1
        self.wave_timer = self.wave_cooldown
        self.spawning_wave = False
        self.game_over_reason = ""
        self.paused_time = 0
        
    def spawn_wave(self):
        self.spawning_wave = True
        
        # Apply difficulty settings to enemy count
        enemy_spawn_multiplier = game_settings.get_difficulty_setting('enemy_spawn_multiplier')
        enemies_to_spawn = int((self.enemies_per_wave + (self.wave - 1) * 2) * enemy_spawn_multiplier)
        
        # Play wave start sound
        sound_manager.play('wave_start')
        
        # Add wave start text animation
        animation_manager.add_text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                                  f"Wave {self.wave}", (255, 0, 0), 48, 120)
        
        for i in range(enemies_to_spawn):
            # Spawn enemies only from the left side
            x = random.randint(-100, -50)
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
                        self.state = PAUSED
                        self.paused_time = pygame.time.get_ticks()
                        sound_manager.pause_music()  # Pause music when game is paused
                    elif self.state == PAUSED:
                        self.state = PLAYING
                        sound_manager.unpause_music()  # Resume music when game is unpaused
                    elif self.state == MENU:
                        pygame.quit()
                        sys.exit()
                    elif self.state == SETTINGS:
                        self.state = MENU
                        
                if self.state == MENU:
                    if event.key == K_RETURN:
                        self.reset_game()
                        self.state = PLAYING
                        sound_manager.play('menu_select')
                    elif event.key == K_s:
                        self.state = SETTINGS
                        sound_manager.play('menu_select')
                        
                if self.state == SETTINGS:
                    if event.key == K_1:
                        game_settings.set_difficulty(DIFFICULTY_EASY)
                        sound_manager.play('menu_select')
                    elif event.key == K_2:
                        game_settings.set_difficulty(DIFFICULTY_NORMAL)
                        sound_manager.play('menu_select')
                    elif event.key == K_3:
                        game_settings.set_difficulty(DIFFICULTY_HARD)
                        sound_manager.play('menu_select')
                    elif event.key == K_f:
                        fullscreen = game_settings.toggle_fullscreen()
                        sound_manager.play('menu_select')
                        # Update screen mode
                        if fullscreen:
                            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    elif event.key == K_m:
                        # Toggle music
                        music_enabled = sound_manager.toggle_music()
                        sound_manager.play('menu_select')
                    elif event.key == K_PLUS or event.key == K_EQUALS:
                        # Increase sound volume
                        new_volume = min(1.0, game_settings.sound_volume + 0.1)
                        game_settings.set_sound_volume(new_volume)
                        sound_manager.set_volume(new_volume)
                        sound_manager.play('menu_select')
                    elif event.key == K_MINUS:
                        # Decrease sound volume
                        new_volume = max(0.0, game_settings.sound_volume - 0.1)
                        game_settings.set_sound_volume(new_volume)
                        sound_manager.set_volume(new_volume)
                        sound_manager.play('menu_select')
                    elif event.key == K_RIGHTBRACKET:
                        # Increase music volume
                        new_volume = min(1.0, game_settings.music_volume + 0.1)
                        game_settings.set_music_volume(new_volume)
                        sound_manager.set_music_volume(new_volume)
                        sound_manager.play('menu_select')
                    elif event.key == K_LEFTBRACKET:
                        # Decrease music volume
                        new_volume = max(0.0, game_settings.music_volume - 0.1)
                        game_settings.set_music_volume(new_volume)
                        sound_manager.set_music_volume(new_volume)
                        sound_manager.play('menu_select')
                        
                if self.state == GAME_OVER and event.key == K_RETURN:
                    self.state = MENU
                    sound_manager.play('menu_select')
                    sound_manager.play_music()  # Resume music when returning to menu
                    
                if self.state == PLAYING:
                    if event.key == K_r:
                        self.player.reload()
                    elif event.key == K_p:
                        self.state = PAUSED
                        self.paused_time = pygame.time.get_ticks()
                        
                    # Player movement
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
                        
                        # Apply damage multiplier
                        damage = 25 * self.player.damage_multiplier
                        
                        self.bullets.append(Bullet(bullet_x, bullet_y, self.player.angle, damage))
                        
    def update(self):
        if self.state == PLAYING:
            # Update animations
            animation_manager.update()
            
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
                
                # Update enemy
                enemy.update(target_x, target_y)
                
                # If at wall, attack when cooldown allows
                if enemy.at_wall:
                    if enemy.attack_wall(self.wall):
                        self.state = GAME_OVER
                        self.game_over_reason = "Your wall was destroyed!"
                        sound_manager.pause_music()  # Pause background music
                        sound_manager.play('game_over')
                
            # Update powerups
            for powerup in self.powerups[:]:
                powerup.update()
                
                # Check if powerup is expired
                if powerup.is_expired():
                    self.powerups.remove(powerup)
                    continue
                    
                # Check if player collected powerup
                if (abs(powerup.x - self.player.x) < self.player.width // 2 + powerup.radius and
                    abs(powerup.y - self.player.y) < self.player.height // 2 + powerup.radius):
                    
                    # Apply powerup effect
                    message = ""
                    if False:  # Removed wall powerup
                        self.wall.repair(25)
                        message = "Wall Repaired"
                    else:
                        message = self.player.apply_powerup(powerup.type)
                        
                    # Play powerup sound
                    sound_manager.play('powerup')
                    
                    # Add powerup animation
                    animation_manager.add_powerup(powerup.x, powerup.y)
                    
                    # Add text animation
                    animation_manager.add_text(powerup.x, powerup.y - 20, message, YELLOW, 24)
                    
                    # Remove powerup
                    self.powerups.remove(powerup)
                
            # Check bullet collisions with enemies
            for bullet in self.bullets[:]:
                for enemy in self.enemies[:]:
                    if (abs(bullet.x - enemy.x) < enemy.width // 2 + bullet.radius and
                        abs(bullet.y - enemy.y) < enemy.height // 2 + bullet.radius):
                        
                        if enemy.take_damage(bullet.damage):
                            self.enemies.remove(enemy)
                            self.player.score += 100
                            self.player.kills += 1
                            
                            # Chance to spawn a powerup when enemy dies
                            powerup_chance = game_settings.get_difficulty_setting('powerup_chance')
                            if random.random() < powerup_chance:
                                # Spawn powerup at enemy position
                                # Spawn powerup at enemy position
                                self.powerups.append(PowerUp(enemy.x, enemy.y))
                                
                        if bullet in self.bullets:  # Check if bullet still exists
                            self.bullets.remove(bullet)
                        break
            
            # Check bullet collisions with powerups
            for bullet in self.bullets[:]:
                for powerup in self.powerups[:]:
                    if (abs(bullet.x - powerup.x) < powerup.radius + bullet.radius and
                        abs(bullet.y - powerup.y) < powerup.radius + bullet.radius):
                        
                        # Apply powerup effect
                        message = powerup.apply_effect(self.player)
                        
                        # Play powerup sound
                        sound_manager.play('powerup')
                        
                        # Add powerup animation
                        animation_manager.add_powerup(powerup.x, powerup.y)
                        
                        # Add text animation
                        animation_manager.add_text(powerup.x, powerup.y - 20, message, YELLOW, 24)
                        
                        # Remove powerup and bullet
                        self.powerups.remove(powerup)
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
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game_over()
        elif self.state == PAUSED:
            self.draw_game()  # Draw game in background
            self.draw_pause_menu()
        elif self.state == SETTINGS:
            self.draw_settings()
            
        pygame.display.flip()
        
    def draw_menu(self):
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.large_font.render("CATPOCALYPSE", True, BLACK)
        subtitle = self.font.render("A Survival Defense Shooter", True, BLACK)
        
        # Draw cat silhouette
        cat_width = 200
        cat_height = 150
        cat_x = SCREEN_WIDTH // 2 - cat_width // 2
        cat_y = SCREEN_HEIGHT // 2 - 150
        
        # Draw basic cat shape
        pygame.draw.ellipse(self.screen, BLACK, (cat_x, cat_y + 50, cat_width, cat_height // 2))  # Body
        pygame.draw.circle(self.screen, BLACK, (cat_x + cat_width // 2, cat_y + 30), 40)  # Head
        
        # Draw ears
        pygame.draw.polygon(self.screen, BLACK, [
            (cat_x + cat_width // 2 - 30, cat_y + 10),
            (cat_x + cat_width // 2 - 40, cat_y - 20),
            (cat_x + cat_width // 2 - 10, cat_y + 5)
        ])
        pygame.draw.polygon(self.screen, BLACK, [
            (cat_x + cat_width // 2 + 30, cat_y + 10),
            (cat_x + cat_width // 2 + 40, cat_y - 20),
            (cat_x + cat_width // 2 + 10, cat_y + 5)
        ])
        
        # Draw eyes (glowing red)
        pygame.draw.circle(self.screen, RED, (cat_x + cat_width // 2 - 15, cat_y + 25), 8)
        pygame.draw.circle(self.screen, RED, (cat_x + cat_width // 2 + 15, cat_y + 25), 8)
        
        # Draw menu options with key bindings highlighted
        start_text = self.font.render("Press [ENTER] to start", True, BLACK)
        settings_text = self.font.render("Press [S] for settings", True, BLACK)
        quit_text = self.font.render("Press [ESC] to quit", True, BLACK)
        
        # Position all elements
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 100))
        
        self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT - 150))
        self.screen.blit(settings_text, (SCREEN_WIDTH//2 - settings_text.get_width()//2, SCREEN_HEIGHT - 100))
        self.screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT - 50))
            
    def draw_settings(self):
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.font.render("SETTINGS", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Calculate grid positions
        grid_width = SCREEN_WIDTH // 2
        grid_height = 200
        left_col = SCREEN_WIDTH // 4
        right_col = SCREEN_WIDTH * 3 // 4
        top_row = 120
        bottom_row = 320
        
        # Draw difficulty settings (top-left quadrant)
        difficulty_title = self.font.render("Difficulty:", True, BLACK)
        easy_text = self.small_font.render("[1] Easy", True, BLACK if game_settings.difficulty != DIFFICULTY_EASY else GREEN)
        normal_text = self.small_font.render("[2] Normal", True, BLACK if game_settings.difficulty != DIFFICULTY_NORMAL else GREEN)
        hard_text = self.small_font.render("[3] Hard", True, BLACK if game_settings.difficulty != DIFFICULTY_HARD else GREEN)
        
        # Draw display settings (top-right quadrant)
        display_title = self.font.render("Display:", True, BLACK)
        fullscreen_text = self.small_font.render("[F] Fullscreen: " + ("ON" if game_settings.fullscreen else "OFF"), True, BLACK)
        
        # Draw sound settings (bottom-left quadrant)
        sound_title = self.font.render("Sound:", True, BLACK)
        sound_volume_text = self.small_font.render("Volume: " + str(int(game_settings.sound_volume * 100)) + "%", True, BLACK)
        sound_controls = self.small_font.render("[+/-] Adjust volume", True, BLACK)
        
        # Draw music settings (bottom-right quadrant)
        music_title = self.font.render("Music:", True, BLACK)
        music_toggle_text = self.small_font.render("[M] Music: " + ("ON" if sound_manager.music_enabled else "OFF"), True, BLACK)
        
        # Draw back option
        back_text = self.font.render("Press [ESC] to return to menu", True, BLACK)
        
        # Position elements in grid layout
        # Top-left quadrant (Difficulty)
        self.screen.blit(difficulty_title, (left_col - difficulty_title.get_width()//2, top_row))
        self.screen.blit(easy_text, (left_col - easy_text.get_width()//2, top_row + 50))
        self.screen.blit(normal_text, (left_col - normal_text.get_width()//2, top_row + 80))
        self.screen.blit(hard_text, (left_col - hard_text.get_width()//2, top_row + 110))
        
        # Top-right quadrant (Display)
        self.screen.blit(display_title, (right_col - display_title.get_width()//2, top_row))
        self.screen.blit(fullscreen_text, (right_col - fullscreen_text.get_width()//2, top_row + 50))
        
        # Bottom-left quadrant (Sound)
        self.screen.blit(sound_title, (left_col - sound_title.get_width()//2, bottom_row))
        self.screen.blit(sound_volume_text, (left_col - sound_volume_text.get_width()//2, bottom_row + 50))
        self.screen.blit(sound_controls, (left_col - sound_controls.get_width()//2, bottom_row + 80))
        
        # Bottom-right quadrant (Music)
        self.screen.blit(music_title, (right_col - music_title.get_width()//2, bottom_row))
        self.screen.blit(music_toggle_text, (right_col - music_toggle_text.get_width()//2, bottom_row + 50))
        
        # Return to menu prompt at the bottom
        self.screen.blit(back_text, (SCREEN_WIDTH//2 - back_text.get_width()//2, SCREEN_HEIGHT - 50))
        
    def draw_game(self):
        # Draw background - different colors for left and right of wall
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, 0, self.wall.x, SCREEN_HEIGHT))  # Enemy area
        pygame.draw.rect(self.screen, GRAY, (self.wall.x, 0, SCREEN_WIDTH - self.wall.x, SCREEN_HEIGHT))  # Player area
        
        # Draw wall
        self.wall.draw(self.screen)
        
        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(self.screen)
            
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Draw player
        self.player.draw(self.screen)
        
        # Draw animations
        animation_manager.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
            
    def draw_hud(self):
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
            reload_progress = 1 - (self.player.reload_time / self.player.reload_time_max)
            reload_text = self.small_font.render("Reloading...", True, RED)
            self.screen.blit(reload_text, (10, 70))
            
            # Draw reload progress bar
            pygame.draw.rect(self.screen, RED, (10, 95, 100, 5))
            pygame.draw.rect(self.screen, GREEN, (10, 95, 100 * reload_progress, 5))
            
        # Wave timer
        if len(self.enemies) == 0 and self.wave_timer > 0:
            next_wave_text = self.small_font.render(f"Next wave in: {self.wave_timer // 60 + 1}", True, BLACK)
            self.screen.blit(next_wave_text, (SCREEN_WIDTH//2 - 80, 10))
            
        # Controls reminder with key bindings highlighted
        controls_text = self.small_font.render("[WASD] Move | Mouse: Aim | [LMB] Shoot | [R] Reload | [P/ESC] Pause", True, BLACK)
        self.screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 20))
        
    def draw_pause_menu(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause menu with key bindings highlighted
        pause_text = self.large_font.render("PAUSED", True, WHITE)
        continue_text = self.font.render("Press [ESC] to continue", True, WHITE)
        quit_text = self.font.render("Press [Q] to quit to menu", True, WHITE)
        
        self.screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 70))
        
    def draw_game_over(self):
        # Draw game in background
        self.draw_game()
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.large_font.render("GAME OVER", True, RED)
        
        # Show reason for game over
        reason_text = self.font.render(self.game_over_reason, True, WHITE)
            
        # Show stats
        score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        kills_text = self.font.render(f"Enemies Killed: {self.player.kills}", True, WHITE)
        wave_text = self.font.render(f"Survived until wave: {self.wave}", True, WHITE)
        
        # Show difficulty
        difficulty_names = ["Easy", "Normal", "Hard"]
        difficulty_text = self.font.render(f"Difficulty: {difficulty_names[game_settings.difficulty]}", True, WHITE)
        
        # Show instruction with key binding highlighted
        instruction = self.font.render("Press [ENTER] to return to menu", True, WHITE)
        
        # Position all elements
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 150))
        self.screen.blit(reason_text, (SCREEN_WIDTH//2 - reason_text.get_width()//2, SCREEN_HEIGHT//2 - 90))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 30))
        self.screen.blit(kills_text, (SCREEN_WIDTH//2 - kills_text.get_width()//2, SCREEN_HEIGHT//2 + 10))
        self.screen.blit(wave_text, (SCREEN_WIDTH//2 - wave_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(difficulty_text, (SCREEN_WIDTH//2 - difficulty_text.get_width()//2, SCREEN_HEIGHT//2 + 90))
        self.screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT//2 + 150))
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
