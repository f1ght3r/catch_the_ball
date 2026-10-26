"""Loop an MP4 as a Pygame background using OpenCV."""

from pathlib import Path

import pygame

try:
    import cv2
except ImportError:
    cv2 = None


class VideoBackground:
    def __init__(self, path, size):
        self.size = size
        self.capture = None
        self.frame = None
        self.frame_interval = 1000 / 30
        self.frame_timer = 0
        if cv2 is None or not Path(path).is_file():
            return
        capture = cv2.VideoCapture(str(path))
        if not capture.isOpened():
            capture.release()
            return
        fps = capture.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            self.frame_interval = 1000 / fps
        self.capture = capture
        self._read_frame()

    @property
    def available(self):
        return self.capture is not None and self.frame is not None

    def _read_frame(self):
        if self.capture is None:
            return
        success, image = self.capture.read()
        if not success:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, image = self.capture.read()
        if not success:
            return

        target_width, target_height = self.size
        height, width = image.shape[:2]
        scale = max(target_width / width, target_height / height)
        resized = cv2.resize(image, (round(width * scale), round(height * scale)),
                             interpolation=cv2.INTER_AREA)
        x = (resized.shape[1] - target_width) // 2
        y = (resized.shape[0] - target_height) // 2
        cropped = resized[y:y + target_height, x:x + target_width]
        rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        self.frame = pygame.image.frombuffer(rgb.tobytes(), self.size, "RGB").convert()

    def update(self, elapsed):
        if self.capture is None:
            return
        self.frame_timer += elapsed
        while self.frame_timer >= self.frame_interval:
            self.frame_timer -= self.frame_interval
            self._read_frame()

    def draw(self, surface):
        if self.frame is None:
            surface.fill((15, 18, 38))
        else:
            surface.blit(self.frame, (0, 0))

    def close(self):
        if self.capture is not None:
            self.capture.release()
