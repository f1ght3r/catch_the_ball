from array import array
from io import BytesIO
import math
import random
import wave

import pygame

pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Prinde mingea!")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
large_font = pygame.font.SysFont(None, 52)


def create_relaxing_song():
    sample_rate = 11025
    bar_duration = 3.0
    chords = (
        (130.81, 164.81, 196.00),
        (110.00, 130.81, 164.81),
        (87.31, 110.00, 130.81),
        (98.00, 123.47, 146.83),
    )
    melody = (
        (0.0, 523.25), (0.75, 392.00), (1.5, 329.63), (2.25, 392.00),
        (3.0, 440.00), (3.75, 329.63), (4.5, 261.63), (5.25, 329.63),
        (6.0, 349.23), (6.75, 440.00), (7.5, 523.25), (8.25, 440.00),
        (9.0, 392.00), (9.75, 493.88), (10.5, 587.33), (11.25, 493.88),
    )
    duration = bar_duration * len(chords)
    samples = [0.0] * int(sample_rate * duration)

    def add_tone(start, length, frequency, volume):
        first_sample = int(start * sample_rate)
        sample_count = int(length * sample_rate)
        for offset in range(sample_count):
            elapsed = offset / sample_rate
            envelope = min(1.0, elapsed / 0.12, (length - elapsed) / 0.25)
            samples[first_sample + offset] += (
                math.sin(2 * math.pi * frequency * elapsed) * volume * envelope
            )

    for bar, chord in enumerate(chords):
        for frequency in chord:
            add_tone(bar * bar_duration, bar_duration, frequency, 0.12)
    for start, frequency in melody:
        add_tone(start, 0.65, frequency, 0.12)

    pcm = array(
        "h",
        (int(max(-1.0, min(1.0, sample)) * 32767) for sample in samples),
    )
    audio_file = BytesIO()
    with wave.open(audio_file, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    audio_file.seek(0)
    return pygame.mixer.Sound(file=audio_file)


music_channel = None
music_sound = None
try:
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    music_sound = create_relaxing_song()
    music_channel = pygame.mixer.Channel(0)
except pygame.error as error:
    print(f"Background music is unavailable: {error}")

try:
    background_image = pygame.image.load("Pasted Image").convert()
    background_image = pygame.transform.scale(background_image, screen.get_size())
except pygame.error:
    background_image = None

HIGH_SCORE_FILE = "highscore.txt"


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(value):
    with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
        file.write(str(value))


def reset_ball():
    global ball
    ball.x = random.randint(0, 500)
    ball.y = -20


def reset_round():
    global basket, ball, ball_speed, modifier, modifier_type, modifier_message
    basket = pygame.Rect(250, 350, 100, 20)
    ball = pygame.Rect(290, 0, 20, 20)
    ball_speed = 5
    modifier = None
    modifier_type = None
    modifier_message = ""


basket = pygame.Rect(250, 350, 100, 20)
ball = pygame.Rect(290, 0, 20, 20)
ball_speed = 5
score = 0
lives = 3
high_score = load_high_score()
state = "start"
paused = False
running = True
modifier = None
modifier_type = None
modifier_message = ""
music_enabled = True


def start_game():
    global score, lives, state, paused
    score = 0
    lives = 3
    paused = False
    state = "playing"
    reset_round()


def spawn_modifier():
    global modifier, modifier_type
    if modifier is not None:
        return
    modifier_type = random.choice(["slow", "wide", "life", "bonus"])
    modifier = pygame.Rect(random.randint(10, 560), -20, 20, 20)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and state == "start":
                start_game()
            elif event.key == pygame.K_p and state == "playing":
                paused = not paused
            elif event.key == pygame.K_r and state == "game_over":
                start_game()
            elif event.key == pygame.K_m:
                music_enabled = not music_enabled

    if state == "playing" and not paused:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            basket.x -= 5
        if keys[pygame.K_RIGHT]:
            basket.x += 5

        basket.x = max(0, min(basket.x, screen.get_width() - basket.width))

        if random.random() < 0.008:
            spawn_modifier()

        ball.y += ball_speed

        if modifier is not None:
            modifier.y += 4
            if basket.colliderect(modifier):
                if modifier_type == "slow":
                    ball_speed = max(2, ball_speed - 1)
                    modifier_message = "Slow motion!"
                elif modifier_type == "wide":
                    center_x = basket.centerx
                    basket.width = min(screen.get_width(), basket.width + 20)
                    basket.centerx = center_x
                    basket.clamp_ip(screen.get_rect())
                    modifier_message = "Bigger basket!"
                elif modifier_type == "life":
                    lives = min(5, lives + 1)
                    modifier_message = "Extra life!"
                elif modifier_type == "bonus":
                    score += 15
                    modifier_message = "Bonus +15!"
                modifier = None
                modifier_type = None
            elif modifier.y > 420:
                modifier = None
                modifier_type = None

        if basket.colliderect(ball):
            score += 10
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            reset_ball()

        if ball.y > 400:
            lives -= 1
            if lives <= 0:
                state = "game_over"
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            else:
                reset_ball()

    if background_image is not None:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((30, 35, 50))

    if state == "start":
        title = large_font.render("Catch the Ball", True, (255, 255, 255))
        subtitle = font.render("Press SPACE to start", True, (200, 200, 200))
        controls = font.render("Controls: LEFT / RIGHT | P = pause | M = music", True, (200, 200, 200))
        info = font.render("Green + balls grow the platform every time!", True, (255, 200, 100))
        screen.blit(title, (160, 70))
        screen.blit(subtitle, (180, 145))
        screen.blit(controls, (60, 205))
        screen.blit(info, (120, 245))

    elif state == "playing":
        pygame.draw.rect(screen, (70, 160, 240), basket)
        pygame.draw.ellipse(screen, (255, 180, 60), ball)

        if modifier is not None:
            color = {
                "slow": (80, 160, 255),
                "wide": (80, 255, 160),
                "life": (255, 220, 80),
                "bonus": (255, 120, 120),
            }[modifier_type]
            pygame.draw.circle(screen, color, (modifier.x + 10, modifier.y + 10), 10)
            if modifier_type == "wide":
                pygame.draw.rect(screen, (255, 255, 255), (modifier.x + 8, modifier.y + 4, 4, 12))
                pygame.draw.rect(screen, (255, 255, 255), (modifier.x + 4, modifier.y + 8, 12, 4))

        if modifier_message:
            msg = font.render(modifier_message, True, (255, 255, 255))
            screen.blit(msg, (220, 20))

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
        high_text = font.render(f"High score: {high_score}", True, (255, 215, 100))
        screen.blit(score_text, (20, 20))
        screen.blit(lives_text, (20, 50))
        screen.blit(high_text, (360, 20))

        if paused:
            pause_overlay = large_font.render("PAUSED", True, (255, 255, 255))
            screen.blit(pause_overlay, (210, 140))

    elif state == "game_over":
        game_over = large_font.render("GAME OVER", True, (255, 95, 95))
        final_score = font.render(f"Your score: {score}", True, (255, 255, 255))
        best_score = font.render(f"High score: {high_score}", True, (255, 215, 100))
        restart_hint = font.render("Press R to restart", True, (200, 200, 200))
        screen.blit(game_over, (175, 100))
        screen.blit(final_score, (215, 170))
        screen.blit(best_score, (185, 210))
        screen.blit(restart_hint, (200, 260))

    if music_channel is not None:
        if state == "playing" and music_enabled:
            if paused:
                music_channel.pause()
            elif music_channel.get_busy():
                music_channel.unpause()
            else:
                music_channel.play(music_sound, loops=-1)
        else:
            music_channel.stop()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
