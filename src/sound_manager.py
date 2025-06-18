import pygame
import os
import sys

class SoundManager:
    def __init__(self):
        # Initialize the sound mixer if not already initialized
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                print("Sound mixer initialized successfully in SoundManager")
            except Exception as e:
                print(f"Error initializing sound mixer in SoundManager: {str(e)}")
            
        # Dictionary to store loaded sounds
        self.sounds = {}
        
        # Dictionary to store music
        self.music = None
        self.music_paused = False
        
        # Sound volume (0.0 to 1.0)
        self.volume = 0.7
        self.music_volume = 0.5
        
        # Sound enabled flag
        self.sound_enabled = True
        self.music_enabled = True
        
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (e.g., PyInstaller)
            self.script_dir = os.path.dirname(sys.executable)
        else:
            # If the application is run as a script
            self.script_dir = os.path.dirname(os.path.abspath(__file__))
            
        print(f"Script directory: {self.script_dir}")
        
        # Try to load sounds
        self._load_sounds()
        self._load_music()
        
    def _load_sounds(self):
        """Load all game sounds"""
        sound_files = {
            'shoot': 'shoot.mp3',
            'reload': 'reload.mp3',
            'enemy_death': 'enemy_death.mp3',
            'powerup': 'powerup.mp3',
            'game_over': 'game_over.mp3',
            'menu_select': 'menu_select.mp3',
            'wall_hit': 'wall_hit.mp3',
            'wave_start': 'menu_select.mp3'  # Default to menu_select for wave_start
        }
        
        # Get the assets directory path - one level up from script_dir, then into assets
        assets_dir = os.path.join(os.path.dirname(self.script_dir), 'assets')
        sounds_dir = os.path.join(assets_dir, 'sounds')
        
        # Check if we have enemy_hit.mp3, if not use wall_hit.mp3 for enemy_hit
        enemy_hit_path = os.path.join(sounds_dir, 'enemy_hit.mp3')
        if os.path.exists(enemy_hit_path):
            sound_files['enemy_hit'] = 'enemy_hit.mp3'
        else:
            sound_files['enemy_hit'] = 'wall_hit.mp3'  # Use wall_hit as a fallback
            
        # Check if we have player_hit.mp3, if not use enemy_hit as fallback
        player_hit_path = os.path.join(sounds_dir, 'player_hit.mp3')
        if os.path.exists(player_hit_path):
            sound_files['player_hit'] = 'player_hit.mp3'
        else:
            sound_files['player_hit'] = sound_files['enemy_hit']  # Use enemy_hit as a fallback
            
        # Check if we have wave_start.mp3
        wave_start_path = os.path.join(sounds_dir, 'wave_start.mp3')
        if os.path.exists(wave_start_path):
            sound_files['wave_start'] = 'wave_start.mp3'
        
        # Print all sound files in the sounds directory
        print(f"Contents of sounds directory ({sounds_dir}):")
        if os.path.exists(sounds_dir):
            for file in os.listdir(sounds_dir):
                print(f"  - {file}")
        else:
            print(f"  Sounds directory not found: {sounds_dir}")
        
        for sound_name, file_name in sound_files.items():
            self._load_sound(sound_name, file_name)
            
    def _load_sound(self, sound_name, file_name):
        """Load a single sound file"""
        try:
            # Get the assets directory path - one level up from script_dir, then into assets
            assets_dir = os.path.join(os.path.dirname(self.script_dir), 'assets')
            sound_path = os.path.join(assets_dir, 'sounds', file_name)
            
            if os.path.exists(sound_path):
                self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                self.sounds[sound_name].set_volume(self.volume)
                print(f"Loaded sound: {sound_path}")
            else:
                print(f"Sound file not found: {sound_path}")
        except Exception as e:
            print(f"Could not load sound: {file_name}. Error: {str(e)}")
            
    def _load_music(self):
        """Load background music"""
        try:
            # Get the assets directory path - one level up from script_dir, then into assets
            assets_dir = os.path.join(os.path.dirname(self.script_dir), 'assets')
            sounds_dir = os.path.join(assets_dir, 'sounds')
            
            # Check for background music file
            bg_music_path = os.path.join(sounds_dir, 'bg music.mp3')
            if os.path.exists(bg_music_path):
                self.music = bg_music_path
                print(f"Loaded background music: {bg_music_path}")
            else:
                print(f"Background music file not found: {bg_music_path}")
                
                # Try alternative filenames
                alt_names = ['background.mp3', 'bgmusic.mp3', 'music.mp3']
                for alt_name in alt_names:
                    alt_path = os.path.join(sounds_dir, alt_name)
                    if os.path.exists(alt_path):
                        self.music = alt_path
                        print(f"Loaded alternative background music: {alt_path}")
                        break
        except Exception as e:
            print(f"Could not load background music. Error: {str(e)}")
            
    def play(self, sound_name):
        """Play a sound by name"""
        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {str(e)}")
        else:
            print(f"Sound '{sound_name}' not found or not loaded")
            
    def play_music(self, loop=-1):
        """Play background music"""
        if not self.music_enabled or not self.music:
            print("Music is disabled or not loaded")
            return
            
        try:
            pygame.mixer.music.load(self.music)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loop)
            print(f"Playing music: {self.music}")
        except Exception as e:
            print(f"Error playing music: {str(e)}")
            
    def stop_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error stopping music: {str(e)}")
        
    def pause_music(self):
        """Pause background music"""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.music_paused = True
        except Exception as e:
            print(f"Error pausing music: {str(e)}")
            
    def unpause_music(self):
        """Unpause background music"""
        try:
            if self.music_paused:
                pygame.mixer.music.unpause()
                self.music_paused = False
        except Exception as e:
            print(f"Error unpausing music: {str(e)}")
            
    def set_volume(self, volume):
        """Set volume for all sounds (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                try:
                    sound.set_volume(self.volume)
                except Exception as e:
                    print(f"Error setting sound volume: {str(e)}")
                
    def set_music_volume(self, volume):
        """Set volume for background music (0.0 to 1.0)"""
        try:
            self.music_volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception as e:
            print(f"Error setting music volume: {str(e)}")
                
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled
        
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled:
            self.play_music()
        else:
            self.stop_music()
            
        return self.music_enabled
        
# Create a global instance
sound_manager = SoundManager()
