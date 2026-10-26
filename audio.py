"""Stream local soundtracks and synthesize short sound effects."""

from array import array
import io
import json
import math
from pathlib import Path
import wave

import pygame


def make_tune(notes, beat=0.12, bass=None):
    """Build a mono WAV in memory from frequencies (zero means a rest)."""
    rate = 22050
    samples = array("h")
    length = int(rate * beat)
    for step, frequency in enumerate(notes):
        low = bass[(step // 4) % len(bass)] if bass else 0
        for index in range(length):
            t = index / rate
            envelope = min(1, t / 0.008, (beat - t) / 0.025)
            melody = math.sin(2 * math.pi * frequency * t) if frequency else 0
            harmony = 0.35 * math.sin(2 * math.pi * low * t) if low else 0
            samples.append(int(10000 * envelope * (0.65 * melody + harmony)))
    # WAV samples are always little endian.
    import sys
    if sys.byteorder != "little":
        samples.byteswap()
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(samples.tobytes())
    output.seek(0)
    return output


class GameAudio:
    def __init__(self):
        self.available = False
        self.muted = False
        self.music_enabled = True
        self.master_volume = 1.0
        self.music_volume = 0.22
        self.sfx_volume = 0.55
        self.effects = {}
        self.current_track = None
        folder = Path(__file__).resolve().parent
        self.settings_path = folder / "settings.json"
        self.load_settings()
        # Older settings used `muted` for the M key. Treat that as music off.
        if self.muted:
            self.music_enabled = False
        self.muted = not self.music_enabled
        self.tracks = {
            "menu": folder / "menu_soundtrack.mp3",
            "game": folder / "game_soundrack.mp3",
        }
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            patterns = {
                "catch": ([660, 880], 0.055),
                "powerup": ([523, 659, 784, 1047], 0.065),
                "miss": ([220, 165], 0.12),
                "game_over": ([392, 330, 294, 196], 0.19),
                "start": ([523, 659, 784], 0.09),
            }
            for name, (notes, beat) in patterns.items():
                self.effects[name] = pygame.mixer.Sound(file=make_tune(notes, beat))
            try:
                self.effects["game_over"] = pygame.mixer.Sound(str(folder / "game_over.mp3"))
            except (pygame.error, OSError) as error:
                print(f"Could not load game_over.mp3; using default effect: {error}")
            self.available = True
            self.update_volume()
        except pygame.error:
            # Keep the game playable on machines with no audio device.
            self.available = False

    def load_settings(self):
        try:
            settings = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if not isinstance(settings, dict):
            return
        for name in ("muted", "music_enabled"):
            if isinstance(settings.get(name), bool):
                setattr(self, name, settings[name])
        for name in ("master_volume", "music_volume", "sfx_volume"):
            value = settings.get(name)
            if type(value) in (int, float) and math.isfinite(value):
                setattr(self, name, max(0.0, min(1.0, value)))

    def save_settings(self):
        settings = {name: getattr(self, name) for name in (
            "muted", "music_enabled", "master_volume", "music_volume", "sfx_volume")}
        temporary = self.settings_path.with_suffix(".json.tmp")
        try:
            temporary.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
            temporary.replace(self.settings_path)
        except OSError as error:
            print(f"Could not save audio settings: {error}")

    def update_volume(self):
        if self.available:
            master = self.master_volume
            pygame.mixer.music.set_volume(master * self.music_volume)
            if self.music_enabled:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
            for sound in self.effects.values():
                sound.set_volume(master * self.sfx_volume)

    def set_volume(self, name, value):
        if name not in ("master_volume", "music_volume", "sfx_volume"):
            raise ValueError(f"Unknown volume: {name}")
        setattr(self, name, max(0.0, min(1.0, value)))
        self.update_volume()
        self.save_settings()

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        self.muted = not self.music_enabled
        self.update_volume()
        self.save_settings()

    def toggle_mute(self):
        # Kept as an alias for older callers; M now toggles music only.
        self.toggle_music()

    def play(self, name):
        if self.available:
            self.effects[name].play()

    def start_music(self, track="game"):
        if self.available and track != self.current_track:
            try:
                pygame.mixer.music.load(str(self.tracks[track]))
                self.update_volume()
                pygame.mixer.music.play(loops=-1, fade_ms=400)
                self.update_volume()
                self.current_track = track
            except (pygame.error, OSError) as error:
                self.current_track = None
                print(f"Could not play {self.tracks[track].name}: {error}")

    def stop_music(self):
        if self.available:
            pygame.mixer.music.fadeout(400)
            self.current_track = None
