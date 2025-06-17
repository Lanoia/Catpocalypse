import pygame
import os

class SoundManager:
    def __init__(self):
        # Initialize the sound mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
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
            'wall_hit': 'wall_hit.mp3'
        }
        
        # Check if we have enemy_hit.mp3, if not use wall_hit.mp3 for enemy_hit
        if os.path.exists(os.path.join('sounds', 'enemy_hit.mp3')):
            sound_files['enemy_hit'] = 'enemy_hit.mp3'
        else:
            sound_files['enemy_hit'] = 'wall_hit.mp3'  # Use wall_hit as a fallback
            
        # Check if we have player_hit.mp3, if not use enemy_hit as fallback
        if os.path.exists(os.path.join('sounds', 'player_hit.mp3')):
            sound_files['player_hit'] = 'player_hit.mp3'
        else:
            sound_files['player_hit'] = 'enemy_hit.mp3'  # Use enemy_hit as a fallback
            
        # Check if we have wave_start.mp3, if not use menu_select as fallback
        if os.path.exists(os.path.join('sounds', 'wave_start.mp3')):
            sound_files['wave_start'] = 'wave_start.mp3'
        else:
            sound_files['wave_start'] = 'menu_select.mp3'  # Use menu_select as a fallback
        
        for sound_name, file_name in sound_files.items():
            self._load_sound(sound_name, file_name)
            
    def _load_sound(self, sound_name, file_name):
        """Load a single sound file"""
        try:
            sound_path = os.path.join('sounds', file_name)
            if os.path.exists(sound_path):
                self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                self.sounds[sound_name].set_volume(self.volume)
                print(f"Loaded sound: {file_name}")
            else:
                print(f"Sound file not found: {file_name}")
        except Exception as e:
            print(f"Could not load sound: {file_name}. Error: {str(e)}")
            
    def _load_music(self):
        """Load background music"""
        try:
            # Check for background music file
            bg_music_path = os.path.join('sounds', 'bg music.mp3')
            if os.path.exists(bg_music_path):
                self.music = bg_music_path
                print(f"Loaded background music: {bg_music_path}")
            else:
                print("Background music file not found")
        except Exception as e:
            print(f"Could not load background music. Error: {str(e)}")
            
    def play(self, sound_name):
        """Play a sound by name"""
        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()
            
    def play_music(self, loop=-1):
        """Play background music"""
        if not self.music_enabled or not self.music:
            return
            
        try:
            pygame.mixer.music.load(self.music)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loop)
        except Exception as e:
            print(f"Error playing music: {str(e)}")
            
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        
    def pause_music(self):
        """Pause background music"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.music_paused = True
            
    def unpause_music(self):
        """Unpause background music"""
        if self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False
            
    def set_volume(self, volume):
        """Set volume for all sounds (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)
                
    def set_music_volume(self, volume):
        """Set volume for background music (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
                
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
