# ==================== 1. IMPORTURI ====================
from array import array
from io import BytesIO
import math
import random
from pathlib import Path
import wave

import pygame


# ==================== 2. INITIALIZARE PYGAME SI FEREASTRA ====================
pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
game_over_tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
game_over_tint.fill((220, 25, 35, 115))
pygame.display.set_caption("Prinde mingea!")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
large_font = pygame.font.Font(None, 56)


# ==================== 3. INCARCAREA FUNDALURILOR ====================
def load_background(filename):
    background_file = Path(__file__).with_name(filename)
    if not background_file.is_file():
        return None

    try:
        image = pygame.image.load(str(background_file)).convert()
    except pygame.error as error:
        print(f"Nu s-a putut incarca {filename}: {error}")
        return None
    return pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))


background_images = {
    "start": load_background("start_background.png"),
    "playing": load_background("game_background.png"),
    "game_over": load_background("game_over_background.png"),
    "shared": load_background("background.png"),
}


# ==================== 4. GENERAREA SI REDAREA MUZICII ====================
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
    music_channel.play(music_sound, loops=-1)
except pygame.error as error:
    print(f"Muzica de fundal nu este disponibila: {error}")
music_enabled = music_channel is not None

# ==================== 5. CONFIGURAREA JOCULUI SI OBIECTELE ====================
basket = pygame.Rect(250, 350, 100, 20)
ball = pygame.Rect(290, 0, 20, 20)
ball_value = 1
ball_color = (245, 245, 245)

score = 0
lives = 3
game_state = "start"
difficulty = "Normal"
difficulty_settings = {
    "Usor": {"lives": 5, "speed": 3},
    "Normal": {"lives": 3, "speed": 5},
    "Greu": {"lives": 2, "speed": 7},
}
HIGH_SCORE_FILES = {
    "Usor": Path(__file__).with_name("highscore_easy.txt"),
    "Normal": Path(__file__).with_name("highscore.txt"),
    "Greu": Path(__file__).with_name("highscore_hard.txt"),
}


def load_high_score(filename):
    try:
        return int(filename.read_text(encoding="utf-8").strip())
    except FileNotFoundError:
        return 0
    except ValueError:
        return 0


high_scores = {
    mode: load_high_score(filename)
    for mode, filename in HIGH_SCORE_FILES.items()
}
high_score = high_scores["Normal"]
modifier_name = "Normal"
modifier_end_time = 0
next_modifier_time = 0
ball_speed = 5
basket_width = 100


# ==================== 6. RESETAREA MINGII SI A RUNDEI ====================
def reset_ball():
    global ball_value, ball_color

    ball.y = -20
    ball.x = random.randint(0, SCREEN_WIDTH - ball.width)
    ball_value = random.choices((1, 3, 5), weights=(70, 20, 10), k=1)[0]
    ball_color = {
        1: (245, 245, 245),
        3: (255, 215, 0),
        5: (100, 220, 255),
    }[ball_value]


def reset_game():
    global score, lives, game_state, basket_width, ball_speed
    global modifier_name, modifier_end_time, next_modifier_time

    score = 0
    lives = difficulty_settings[difficulty]["lives"]
    basket_width = 100
    ball_speed = difficulty_settings[difficulty]["speed"]
    basket.width = basket_width
    basket.x = (SCREEN_WIDTH - basket.width) // 2
    modifier_name = "Normal"
    modifier_end_time = 0
    next_modifier_time = pygame.time.get_ticks() + 8000
    reset_ball()
    game_state = "playing"


# ==================== 7. FUNCTII DE DESENARE ====================
def draw_centered(text, y, text_font=font, color=(245, 245, 245)):
    image = text_font.render(text, True, color)
    screen.blit(image, image.get_rect(center=(SCREEN_WIDTH // 2, y)))


def draw_modifier_icon(name, x, y):
    colors = {
        "Minge rapida": (255, 180, 60),
        "Minge lenta": (120, 210, 255),
        "Cos lat": (100, 220, 150),
        "Cos ingust": (190, 150, 255),
    }
    color = colors.get(name, (180, 180, 180))
    icon = pygame.Rect(x, y, 24, 24)
    pygame.draw.rect(screen, (45, 50, 65), icon)
    pygame.draw.rect(screen, color, icon, 2)

    if name == "Minge rapida":
        pygame.draw.line(screen, color, (x + 5, y + 8), (x + 18, y + 8), 2)
        pygame.draw.line(screen, color, (x + 3, y + 12), (x + 16, y + 12), 2)
        pygame.draw.line(screen, color, (x + 5, y + 16), (x + 18, y + 16), 2)
    elif name == "Minge lenta":
        pygame.draw.rect(screen, color, (x + 5, y + 5, 14, 14), 2)
        pygame.draw.line(screen, color, (x + 12, y + 7), (x + 12, y + 12), 2)
        pygame.draw.line(screen, color, (x + 12, y + 12), (x + 16, y + 14), 2)
    elif name in ("Cos lat", "Cos ingust"):
        width = 18 if name == "Cos lat" else 10
        left = x + (24 - width) // 2
        pygame.draw.line(screen, color, (left, y + 7), (left + 2, y + 18), 2)
        pygame.draw.line(
            screen, color, (left + 2, y + 18), (left + width - 2, y + 18), 2
        )
        pygame.draw.line(
            screen,
            color,
            (left + width - 2, y + 18),
            (left + width, y + 7),
            2,
        )


# ==================== 8. INCARCAREA SI SALVAREA RECORDURILOR ====================
def save_high_score():
    try:
        HIGH_SCORE_FILES[difficulty].write_text(f"{high_score}\n", encoding="utf-8")
    except OSError as error:
        print(f"Nu s-a putut salva recordul: {error}")


def update_high_score():
    global high_score
    if score > high_score:
        high_score = score
        high_scores[difficulty] = high_score
        save_high_score()


# ==================== 9. MODIFICATORII JOCULUI ====================
def apply_random_modifier(now):
    global modifier_name, modifier_end_time, next_modifier_time
    global ball_speed, basket_width

    modifier = random.choice(("Minge rapida", "Minge lenta", "Cos lat", "Cos ingust"))
    base_speed = difficulty_settings[difficulty]["speed"]
    ball_speed = base_speed
    basket_width = 100

    if modifier == "Minge rapida":
        ball_speed = base_speed + 3
    elif modifier == "Minge lenta":
        ball_speed = max(2, base_speed - 2)
    elif modifier == "Cos lat":
        basket_width = 150
    else:
        basket_width = 60

    basket.width = basket_width
    basket.x = min(basket.x, SCREEN_WIDTH - basket.width)
    modifier_name = modifier
    modifier_end_time = now + 5000
    next_modifier_time = now + 10000


# ==================== 10. BUCLEA PRINCIPALA A JOCULUI ====================
running = True
while running:
    now = pygame.time.get_ticks()

    # -------------------- 10.1 Evenimente si taste --------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m and music_channel is not None:
                music_enabled = not music_enabled
                if music_enabled:
                    music_channel.play(music_sound, loops=-1)
                else:
                    music_channel.stop()
            elif game_state == "start":
                if event.key in (pygame.K_1, pygame.K_KP1):
                    difficulty = "Usor"
                    high_score = high_scores[difficulty]
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    difficulty = "Normal"
                    high_score = high_scores[difficulty]
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    difficulty = "Greu"
                    high_score = high_scores[difficulty]
                elif event.key == pygame.K_RETURN:
                    reset_game()
                elif event.key == pygame.K_i:
                    game_state = "instructions"
            elif game_state == "instructions":
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    game_state = "start"
            elif game_state == "playing" and event.key in (pygame.K_p, pygame.K_ESCAPE):
                game_state = "paused"
            elif game_state == "paused" and event.key in (pygame.K_p, pygame.K_ESCAPE):
                game_state = "playing"
            elif game_state == "game_over":
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    game_state = "start"

    # -------------------- 10.2 Miscare si reguli --------------------
    if game_state == "playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            basket.x -= 5
        if keys[pygame.K_RIGHT]:
            basket.x += 5

        basket.x = max(0, min(basket.x, SCREEN_WIDTH - basket.width))
        ball.y += ball_speed

        if basket.colliderect(ball):
            score += ball_value
            update_high_score()
            reset_ball()
        elif ball.top > SCREEN_HEIGHT:
            lives -= 1
            reset_ball()
            if lives <= 0:
                game_state = "game_over"

        if now >= modifier_end_time and modifier_name != "Normal":
            modifier_name = "Normal"
            ball_speed = difficulty_settings[difficulty]["speed"]
            basket_width = 100
            basket.width = basket_width
            basket.x = min(basket.x, SCREEN_WIDTH - basket.width)
        if now >= next_modifier_time:
            apply_random_modifier(now)

    # -------------------- 10.3 Desenarea ecranelor --------------------
    background_image = background_images.get(game_state)
    if background_image is None:
        background_image = background_images["shared"]
    if background_image is None:
        screen.fill((30, 35, 50))
    else:
        screen.blit(background_image, (0, 0))
    if game_state == "game_over":
        screen.blit(game_over_tint, (0, 0))

    if game_state == "start":
        draw_centered("Prinde mingea!", 70, large_font, (255, 180, 60))
        draw_centered("Apasa ENTER pentru joc", 145)
        draw_centered("Apasa I pentru instructiuni", 185)
        draw_centered(
            f"Dificultate: {difficulty} (1 Usor | 2 Normal | 3 Greu)", 235,
            color=(255, 220, 120),
        )
        draw_centered(f"Record: {high_score}", 285, color=(150, 220, 170))
        draw_centered("Apasa M pentru a porni/opri muzica", 330)
    elif game_state == "instructions":
        draw_centered("Instructiuni", 75, large_font, (255, 180, 60))
        draw_centered("Foloseste sagetile stanga/dreapta pentru cos", 140)
        draw_centered("Mingea alba: 1 punct; aurie: 3 puncte.", 180)
        draw_centered("Mingea albastra: 5 puncte.", 215)
        draw_centered("Fiecare ratare consuma una dintre cele 3 vieti.", 250)
        draw_centered("P sau ESC: pauza | Modificatorii dureaza 5 secunde", 290)
        draw_centered("ENTER, ESC sau BACKSPACE: inapoi", 345)
        draw_centered("M: porneste/opreste muzica", 385)
        draw_centered("Dificultate: Usor 5 vieti/lent | Normal 3 | Greu 2/rapid", 435)
    else:
        pygame.draw.rect(screen, (70, 160, 240), basket)
        pygame.draw.ellipse(screen, ball_color, ball)
        screen.blit(font.render(f"Scor: {score}", True, (245, 245, 245)), (15, 12))
        screen.blit(font.render(f"Vieti: {lives}", True, (245, 245, 245)), (15, 45))
        screen.blit(font.render(f"Record: {high_score}", True, (150, 220, 170)), (430, 12))
        screen.blit(
            font.render(f"Dificultate: {difficulty}", True, (255, 220, 120)),
            (15, 110),
        )

        if game_state == "playing":
            draw_modifier_icon(modifier_name, 15, 78)
            screen.blit(
                font.render(f"Modificator: {modifier_name}", True, (245, 220, 120)),
                (48, 78),
            )
        elif game_state == "paused":
            draw_centered("PAUZA", 180, large_font, (255, 220, 120))
            draw_centered("Apasa P sau ESC pentru a continua", 225)
        elif game_state == "game_over":
            draw_centered("JOC TERMINAT", 170, large_font, (255, 120, 120))
            draw_centered(f"Scor final: {score}   Record: {high_score}", 220)
            draw_centered("Apasa R pentru restart sau ENTER pentru meniu", 270)

    # -------------------- 10.4 Afisarea cadrului si controlul FPS --------------------
    pygame.display.flip()
    clock.tick(60)

# ==================== 11. INCHIDEREA PYGAME ====================
pygame.quit()