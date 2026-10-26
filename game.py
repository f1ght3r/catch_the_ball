import random
from pathlib import Path

import pygame
from audio import GameAudio
from video import VideoBackground

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()
audio = GameAudio()
audio.start_music("menu")

WINDOW_SIZE = (900, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Prinde mingea!")
clock = pygame.time.Clock()
background = VideoBackground(Path(__file__).resolve().parent / "background.mp4",
                             screen.get_size())

# Neon palette sampled from the pixel-art city background.
INK = (16, 20, 43)
PANEL = (23, 29, 59, 218)
TEXT = (235, 239, 255)
MUTED = (159, 169, 205)
CYAN = (83, 214, 218)
PINK = (235, 103, 151)
VIOLET = (153, 116, 214)
BUTTON = (67, 75, 133)
BUTTON_HOVER = (104, 92, 171)

# Load the bundled Pixelify Sans variable font, then try a system copy.
game_folder = Path(__file__).resolve().parent
bundled_font = game_folder / "PixelifySans-VariableFont_wght.ttf"
font_path = str(bundled_font) if bundled_font.is_file() else pygame.font.match_font("Pixelify Sans")
font = pygame.font.Font(font_path, 32)

basket = pygame.Rect(400, 550, 100, 20)
ball = pygame.Rect(440, 0, 20, 20)

score = 0
lives = 3
basket_speed = 8
ball_speed = 4
running = True
state = "start"
now = 0  # Gameplay time freezes in menus, including settings opened while paused.
pause_buttons = {
    "resume": ("Resume", pygame.Rect(340, 220, 220, 45)),
    "settings": ("Settings", pygame.Rect(340, 290, 220, 45)),
    "menu": ("Main Menu", pygame.Rect(340, 360, 220, 45)),
}
start_button = pygame.Rect(350, 430, 200, 50)
settings_button = pygame.Rect(730, 545, 150, 35)
back_button = pygame.Rect(350, 510, 200, 40)
music_toggle = pygame.Rect(340, 105, 220, 40)
volume_sliders = {
    "master_volume": ("Master", pygame.Rect(325, 220, 350, 10)),
    "music_volume": ("Music", pygame.Rect(325, 320, 350, 10)),
    "sfx_volume": ("SFX", pygame.Rect(325, 420, 350, 10)),
}
dragging_slider = None
settings_return_state = "start"
small_font = pygame.font.Font(font_path, 24)
wide_until = slow_until = 0
modifiers = []
next_modifier_at = 0
ball_colors = {"normal": PINK, "wide": (99, 222, 172),
               "slow": CYAN, "bonus": VIOLET}


def spawn_ball():
    ball.x = random.randint(0, screen.get_width() - ball.width)
    ball.y = -ball.height


def centered_text(text, y, text_font=font, color=TEXT):
    surface = text_font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, y)))


def draw_panel(rect, alpha=218, radius=14):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (*PANEL[:3], alpha), panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, (*VIOLET, 150), panel.get_rect(), 2, border_radius=radius)
    screen.blit(panel, rect)


def draw_button(rect, label, text_font=font):
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    color = BUTTON_HOVER if hovered else BUTTON
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, CYAN if hovered else VIOLET, rect, 2, border_radius=8)
    surface = text_font.render(label, True, TEXT)
    screen.blit(surface, surface.get_rect(center=rect.center))

while running:
    elapsed = clock.tick(60)
    background.update(elapsed)
    if state == "playing":
        now += elapsed
    for event in pygame.event.get():
        pointer = event.pos if hasattr(event, "pos") else None
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            audio.toggle_music()
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                and state in ("playing", "paused")):
            state = "paused" if state == "playing" else "playing"
            continue
        if state == "paused":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pause_buttons["resume"][1].collidepoint(pointer):
                    state = "playing"
                elif pause_buttons["settings"][1].collidepoint(pointer):
                    settings_return_state = "paused"
                    state = "settings"
                elif pause_buttons["menu"][1].collidepoint(pointer):
                    state = "start"
                    audio.start_music("menu")
            continue
        if state == "settings":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = settings_return_state
                dragging_slider = None
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(pointer):
                    state = settings_return_state
                    dragging_slider = None
                    continue
                if music_toggle.collidepoint(pointer):
                    audio.toggle_music()
                for name, (_, track) in volume_sliders.items():
                    if track.inflate(20, 26).collidepoint(pointer):
                        dragging_slider = name
                        audio.set_volume(name, (pointer[0] - track.left) / track.width)
            if event.type == pygame.MOUSEMOTION and dragging_slider:
                track = volume_sliders[dragging_slider][1]
                audio.set_volume(dragging_slider, (pointer[0] - track.left) / track.width)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_slider == "sfx_volume":
                    audio.play("catch")
                dragging_slider = None
            continue
        if (state in ("start", "game_over")
                and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and settings_button.collidepoint(pointer)):
            settings_return_state = state
            state = "settings"
            continue
        if event.type == pygame.MOUSEMOTION and state == "playing":
            basket.centerx = pointer[0]
        clicked_start = (event.type == pygame.MOUSEBUTTONDOWN
                         and event.button == 1 and start_button.collidepoint(pointer))
        restart_key = (event.type == pygame.KEYDOWN and event.key == pygame.K_r
                       and state == "game_over")
        if (clicked_start and state in ("start", "game_over")) or restart_key:
            score = 0
            lives = 3
            wide_until = slow_until = 0
            basket.width = 100
            basket.centerx = screen.get_width() // 2
            spawn_ball()
            modifiers.clear()
            next_modifier_at = now + random.randint(3000, 6000)
            state = "playing"
            audio.play("start")
            audio.start_music()

    # 1. Muta cosul     
    keys = pygame.key.get_pressed()
    center = basket.centerx
    basket.width = 160 if now < wide_until else 100
    basket.centerx = center
    if state == "playing" and keys[pygame.K_LEFT]:
        basket.x -= basket_speed
    if state == "playing" and keys[pygame.K_RIGHT]:
        basket.x += basket_speed


    if basket.x < 0:
        basket.x = 0
    if basket.right > screen.get_width():
        basket.right = screen.get_width()
    # 2. Fa mingea sa cada
    if state == "playing":
        ball.y += 2 if now < slow_until else ball_speed

    # 3. Verifica daca mingea a fost prinsa de cos
    if state == "playing" and ball.colliderect(basket):
        score += 1
        audio.play("catch")
        spawn_ball()

    # 4. Reseteaza mingea daca a cazut jos
    if state == "playing" and ball.top >= screen.get_height():
        lives -= 1
        if lives > 0:
            audio.play("miss")
            spawn_ball()
        else:
            state = "game_over"
            audio.start_music("menu")
            audio.play("game_over")

    # Modificatorii apar independent de mingea normala.
    if state == "playing":
        if now >= next_modifier_at:
            modifier_rect = pygame.Rect(0, -26, 26, 26)
            modifier_rect.x = random.randint(0, screen.get_width() - modifier_rect.width)
            modifiers.append((random.choice(("wide", "slow", "bonus")), modifier_rect))
            next_modifier_at = now + random.randint(3000, 6000)

        for modifier_type, modifier_rect in modifiers[:]:
            modifier_rect.y += 3
            if modifier_rect.colliderect(basket):
                audio.play("powerup")
                if modifier_type == "wide":
                    wide_until = now + 8000
                elif modifier_type == "slow":
                    slow_until = now + 8000
                else:
                    score += 3
                modifiers.remove((modifier_type, modifier_rect))
            elif modifier_rect.top >= screen.get_height():
                # Un modificator ratat nu costa o viata.
                modifiers.remove((modifier_type, modifier_rect))

    background.draw(screen)
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((10, 13, 32, 82))
    screen.blit(shade, (0, 0))
    pygame.draw.rect(screen, CYAN, basket, border_radius=5)
    pygame.draw.rect(screen, TEXT, basket, 2, border_radius=5)
    pygame.draw.ellipse(screen, ball_colors["normal"], ball)
    for modifier_type, modifier_rect in modifiers:
        pygame.draw.rect(screen, ball_colors[modifier_type], modifier_rect, border_radius=5)
        label = {"wide": "W", "slow": "S", "bonus": "+"}[modifier_type]
        symbol = small_font.render(label, True, INK)
        screen.blit(symbol, symbol.get_rect(center=modifier_rect.center))
    score_text = font.render(f"Scor: {score}", True, TEXT)
    screen.blit(score_text, (10, 10))
    # Deseneaza inimile direct, fara a depinde de fonturi pentru simboluri.
    for index in range(3):
        x = screen.get_width() - 100 + index * 30
        y = 12
        color = PINK if index < lives else (65, 70, 96)
        pygame.draw.circle(screen, color, (x + 6, y + 6), 6)
        pygame.draw.circle(screen, color, (x + 18, y + 6), 6)
        pygame.draw.polygon(screen, color, [(x, y + 7), (x + 24, y + 7), (x + 12, y + 23)])

    effects = []
    if now < wide_until:
        effects.append(f"Cos lat: {(wide_until - now + 999) // 1000}s")
    if now < slow_until:
        effects.append(f"Minge lenta: {(slow_until - now + 999) // 1000}s")
    centered_text(" | ".join(effects), 55, small_font)

    if state in ("start", "game_over"):
        draw_panel(pygame.Rect(64, 42, 772, 498), 225)
        centered_text("Prinde mingea!" if state == "start" else "Game over!", 95)
        centered_text("Ai 3 inimi!" if state == "start" else f"Scor final: {score}", 155)
        centered_text("Control: mouse sau sagetile stanga/dreapta", 220, small_font)
        centered_text("Verde: cos mai lat pentru 8 secunde", 275, small_font)
        centered_text("Albastru: mingi mai lente pentru 8 secunde", 320, small_font)
        centered_text("Mov: 3 puncte", 365, small_font)
        draw_button(start_button, "START" if state == "start" else "JOACA DIN NOU")
        if state == "game_over":
            centered_text("Sau apasa R pentru restart", 510, small_font)
        draw_button(settings_button, "Settings", small_font)

    if state == "paused":
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((*INK, 220))
        screen.blit(overlay, (0, 0))
        centered_text("Paused", 130)
        for label, button in pause_buttons.values():
            draw_button(button, label)
        centered_text("Esc: resume", 470, small_font)

    if state == "settings":
        draw_panel(pygame.Rect(64, 30, 772, 540), 235)
        centered_text("Settings", 60)
        pygame.draw.rect(screen, CYAN if audio.music_enabled else (81, 83, 108),
                         music_toggle, border_radius=8)
        centered_text("Music: ON" if audio.music_enabled else "Music: OFF", music_toggle.centery)
        for name, (label, track) in volume_sliders.items():
            value = getattr(audio, name)
            text = small_font.render(f"{label}: {round(value * 100)}%", True, TEXT)
            screen.blit(text, (185, track.y - 5))
            pygame.draw.rect(screen, (61, 66, 101), track, border_radius=5)
            filled = pygame.Rect(track.x, track.y, round(track.width * value), track.height)
            pygame.draw.rect(screen, VIOLET, filled, border_radius=5)
            pygame.draw.circle(screen, TEXT,
                               (track.x + round(track.width * value), track.centery), 9)
        draw_button(back_button, "Back")

    audio_label = "M: music off" if not audio.music_enabled else "M: music on"
    if not audio.available:
        audio_label = "Sunet indisponibil"
    screen.blit(small_font.render(audio_label, True, MUTED), (10, 575))
    pygame.display.flip()

background.close()
pygame.quit()
