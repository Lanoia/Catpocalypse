import json
import os

# Difficulty settings
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2

class Settings:
    def __init__(self):
        # Default settings
        self.difficulty = DIFFICULTY_NORMAL
        self.sound_volume = 0.7
        self.music_volume = 0.5
        self.fullscreen = False
        
        # Difficulty multipliers
        self.difficulty_settings = {
            DIFFICULTY_EASY: {
                'player_health_multiplier': 1.5,
                'wall_health_multiplier': 1.5,
                'enemy_health_multiplier': 0.8,
                'enemy_speed_multiplier': 0.8,
                'enemy_spawn_multiplier': 0.8,
                'powerup_chance': 0.15
            },
            DIFFICULTY_NORMAL: {
                'player_health_multiplier': 1.0,
                'wall_health_multiplier': 1.0,
                'enemy_health_multiplier': 1.0,
                'enemy_speed_multiplier': 1.0,
                'enemy_spawn_multiplier': 1.0,
                'powerup_chance': 0.1
            },
            DIFFICULTY_HARD: {
                'player_health_multiplier': 0.8,
                'wall_health_multiplier': 0.8,
                'enemy_health_multiplier': 1.2,
                'enemy_speed_multiplier': 1.2,
                'enemy_spawn_multiplier': 1.2,
                'powerup_chance': 0.05
            }
        }
        
        # Load settings from file if it exists
        self.settings_file = 'settings.json'
        self.load_settings()
        
    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.difficulty = data.get('difficulty', DIFFICULTY_NORMAL)
                    self.sound_volume = data.get('sound_volume', 0.7)
                    self.music_volume = data.get('music_volume', 0.5)
                    self.fullscreen = data.get('fullscreen', False)
            except:
                print("Error loading settings, using defaults")
                
    def save_settings(self):
        """Save settings to file"""
        data = {
            'difficulty': self.difficulty,
            'sound_volume': self.sound_volume,
            'music_volume': self.music_volume,
            'fullscreen': self.fullscreen
        }
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(data, f)
        except:
            print("Error saving settings")
            
    def get_difficulty_setting(self, setting_name):
        """Get a specific difficulty setting based on current difficulty"""
        return self.difficulty_settings[self.difficulty].get(setting_name, 1.0)
        
    def set_difficulty(self, difficulty):
        """Set the game difficulty"""
        if difficulty in [DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD]:
            self.difficulty = difficulty
            self.save_settings()
            
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        self.save_settings()
        return self.fullscreen
        
    def set_sound_volume(self, volume):
        """Set sound volume (0.0 to 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        self.save_settings()
        
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        self.save_settings()
        
# Create a global instance
game_settings = Settings()
