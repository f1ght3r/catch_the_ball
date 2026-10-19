import random
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BALL CATCHER ARCADE!")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28, bold=True)
big_font = pygame.font.SysFont("arial", 52, bold=True)

# Colors
BG = (18, 22, 45)
WHITE = (255, 255, 255)
BLUE = (60, 180, 255)
ORANGE = (255, 160, 40)
GOLD = (255, 220, 40)
RED = (255, 65, 85)
GREEN = (70, 255, 150)
PURPLE = (190, 90, 255)

basket = pygame.Rect(WIDTH // 2 - 55, HEIGHT - 65, 110, 22)

score = 0
lives = 10
combo = 0
best_combo = 0
game_over = False
elapsed = 0

balls = []
particles = []
stars = [
    [random.randrange(WIDTH), random.randrange(HEIGHT),
     random.choice([1, 2, 3])]
    for _ in range(70)
]

def spawn_ball():
    kind = random.choices(
        ["normal", "gold", "bomb"],
        weights=[70, 15, 15]
    )[0]

    radius = 13 if kind != "gold" else 15

    balls.append({
        "rect": pygame.Rect(
            random.randint(10, WIDTH - 35), -35,
            radius * 2, radius * 2
        ),
        "kind": kind,
        "speed": random.uniform(2.5, 4.5) + elapsed * 0.025,
        "phase": random.random() * 6.28
    })

def burst(x, y, color):
    for _ in range(16):
        particles.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-4, 4),
            "dy": random.uniform(-5, 3),
            "life": 30,
            "color": color
        })

def reset_game():
    global score, lives, combo, best_combo
    global game_over, elapsed, balls, particles

    score = 0
    lives = 10
    combo = 0
    best_combo = 0
    elapsed = 0
    balls = []
    particles = []
    game_over = False
    basket.centerx = WIDTH // 2

spawn_ball()
spawn_timer = 0
running = True

while running:
    dt = clock.tick(60) / 1000
    elapsed += dt if not game_over else 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and game_over:
                reset_game()
                spawn_timer = 0

    keys = pygame.key.get_pressed()

    if not game_over:
        # Move basket
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            basket.x -= 420 * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            basket.x += 420 * dt

        basket.x = max(0, min(WIDTH - basket.width, basket.x))

        # Spawn new falling objects
        spawn_timer += dt
        spawn_delay = max(0.28, 0.85 - elapsed * 0.008)

        if spawn_timer >= spawn_delay:
            spawn_ball()
            spawn_timer = 0

        # Move objects and detect collisions
        for ball in balls[:]:
            ball["rect"].y += ball["speed"] * 60 * dt

            if ball["rect"].colliderect(basket):
                kind = ball["kind"]
                x, y = ball["rect"].center

                if kind == "bomb":
                    lives -= 1
                    combo = 0
                    burst(x, y, RED)
                else:
                    combo += 1
                    best_combo = max(best_combo, combo)

                    points = 5 if kind == "gold" else 1
                    bonus = min(combo - 1, 10)
                    score += points + bonus

                    color = GOLD if kind == "gold" else GREEN
                    burst(x, y, color)

                balls.remove(ball)

                if lives <= 0:
                    game_over = True

            elif ball["rect"].top > HEIGHT:
                if ball["kind"] != "bomb":
                    lives -= 1
                    combo = 0

                balls.remove(ball)

                if lives <= 0:
                    game_over = True

    # Background
    screen.fill(BG)

    # Moving stars
    for star in stars:
        star[1] += star[2] * 0.5
        if star[1] > HEIGHT:
            star[0] = random.randrange(WIDTH)
            star[1] = 0

        pygame.draw.circle(
            screen, (65, 75, 115),
            (star[0], int(star[1])), star[2]
        )

    # Draw basket with a glowing rim
    pygame.draw.rect(screen, BLUE, basket, border_radius=10)
    pygame.draw.rect(screen, WHITE, basket, 2, border_radius=10)

    # Draw balls
    for ball in balls:
        rect = ball["rect"]
        kind = ball["kind"]

        color = {
            "normal": ORANGE,
            "gold": GOLD,
            "bomb": RED
        }[kind]

        pygame.draw.circle(screen, color, rect.center, rect.width // 2)
        pygame.draw.circle(
            screen, WHITE,
            (rect.centerx - 4, rect.centery - 4), 4
        )

        if kind == "bomb":
            pygame.draw.line(
                screen, WHITE,
                (rect.centerx - 5, rect.centery - 5),
                (rect.centerx + 5, rect.centery + 5), 3
            )
            pygame.draw.line(
                screen, WHITE,
                (rect.centerx + 5, rect.centery - 5),
                (rect.centerx - 5, rect.centery + 5), 3
            )
        elif kind == "gold":
            pygame.draw.circle(screen, WHITE, rect.center, 5, 2)

    # Particle effects
    for p in particles[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["life"] -= 1

        if p["life"] <= 0:
            particles.remove(p)
        else:
            pygame.draw.circle(
                screen, p["color"],
                (int(p["x"]), int(p["y"])),
                max(1, p["life"] // 7)
            )

    # HUD
    screen.blit(font.render(f"SCORE: {score}", True, WHITE), (20, 18))
    screen.blit(font.render(f"LIVES: {'♥ ' * lives}", True, RED), (20, 55))
    screen.blit(font.render(f"COMBO: x{combo}", True, GOLD), (WIDTH - 190, 18))

    screen.blit(
        font.render("← → or A / D to move", True, (180, 190, 220)),
        (WIDTH // 2 - 145, HEIGHT - 30)
    )

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        title = big_font.render("GAME OVER!", True, RED)
        final_score = font.render(f"Final score: {score}", True, WHITE)
        restart = font.render("Press R to play again", True, GOLD)
        quit_text = font.render("Press ESC to quit", True, WHITE)

        screen.blit(title, title.get_rect(center=(WIDTH // 2, 220)))
        screen.blit(
            final_score,
            final_score.get_rect(center=(WIDTH // 2, 290))
        )
        screen.blit(
            restart,
            restart.get_rect(center=(WIDTH // 2, 350))
        )
        screen.blit(
            quit_text,
            quit_text.get_rect(center=(WIDTH // 2, 395))
        )

    pygame.display.flip()

pygame.quit()