from abc import ABC, abstractmethod
import os
import json
import pygame

class NarutoGame(ABC):
    def __init__(self, title, width, height):
        self.title = title
        self.width = width
        self.height = height
        self.score = 0
        self.is_running = False
        self.paused = False
        self.high_score = self.load_high_score()
        self.difficulty = "Medium"
        self._audio = None
        self._audio_settings = self._load_audio_settings()
        self._init_audio()

    @abstractmethod
    def start_game(self):
        """Initialize the game window and loop."""
        pass

    @abstractmethod
    def update(self):
        """Game logic update."""
        pass

    @abstractmethod
    def draw(self):
        """Render elements."""
        pass

    def game_over(self):
        print(f"Game Over! Final Score in {self.title}: {self.score}")
        self.is_running = False
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        self.audio_play("defeat")

    def toggle_pause(self):
        self.paused = not self.paused

    def set_difficulty(self, level):
        if level in ("Easy", "Medium", "Hard"):
            self.difficulty = level
        else:
            self.difficulty = "Medium"

    def difficulty_factor(self):
        if self.difficulty == "Easy":
            return 0.8
        if self.difficulty == "Hard":
            return 1.25
        return 1.0

    def _scores_path(self):
        base = os.path.dirname(__file__)
        return os.path.join(base, "scores.json")

    def _sounds_path(self):
        base = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(base, "..", "static", "sounds"))

    def _images_path(self):
        base = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(base, "..", "static", "games", "assets", "images"))

    def _load_audio_settings(self):
        base = os.path.dirname(__file__)
        path = os.path.join(base, "audio_settings.json")
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f) or {}
        except Exception:
            return {}
        return {}

    def _init_audio(self):
        try:
            pygame.mixer.init()
        except Exception:
            return
        self._audio = {}
        self._background_music = None
        sp = self._sounds_path()
        suc = os.path.join(sp, "success.mp3")
        fail = os.path.join(sp, "fail.mp3")
        theme = os.path.join(sp, "Naruto Theme - The Raising Fighting Spirit.mp3")
        try:
            if os.path.exists(suc):
                self._audio["victory"] = pygame.mixer.Sound(suc)
            if os.path.exists(fail):
                self._audio["defeat"] = pygame.mixer.Sound(fail)
            if os.path.exists(theme):
                self._background_music = theme
        except Exception:
            pass
        mv = float(self._audio_settings.get("master", 0.6))
        gv = float(self._audio_settings.get("games", {}).get(self.title, 0.8))
        vol = max(0.0, min(1.0, mv * gv))
        for k in list(self._audio.keys()):
            try:
                self._audio[k].set_volume(vol)
            except Exception:
                pass

    def audio_play(self, kind):
        s = self._audio.get(kind)
        try:
            if s:
                s.play()
        except Exception:
            pass

    def play_background_music(self, loops=-1):
        """Play background music. loops=-1 for infinite loop, 0 for once, or specific number."""
        if not self._background_music:
            return
        try:
            mv = float(self._audio_settings.get("master", 0.6))
            gv = float(self._audio_settings.get("games", {}).get(self.title, 0.8))
            bv = float(self._audio_settings.get("background_music", 0.4))
            vol = max(0.0, min(1.0, mv * gv * bv))
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.load(self._background_music)
            pygame.mixer.music.play(loops)
        except Exception:
            pass

    def stop_background_music(self):
        """Stop background music."""
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def pause_background_music(self):
        """Pause background music."""
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

    def unpause_background_music(self):
        """Unpause background music."""
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass

    def is_background_music_playing(self):
        """Check if background music is playing."""
        try:
            return pygame.mixer.music.get_busy()
        except Exception:
            return False

    def load_high_score(self):
        path = self._scores_path()
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return int(data.get(self.title, 0))
        except Exception:
            return 0
        return 0

    def save_high_score(self):
        path = self._scores_path()
        data = {}
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
        except Exception:
            data = {}
        data[self.title] = int(self.high_score)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass
