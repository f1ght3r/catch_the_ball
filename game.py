import random
import pygame

pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Prinde mingea!")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
large_font = pygame.font.SysFont(None, 52)

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

    if state == "playing" and not paused:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            basket.x -= 5
        if keys[pygame.K_RIGHT]:
            basket.x += 5

        if basket.x < 0:
            basket.x = 0
        if basket.x > 500:
            basket.x = 500

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
                    basket.width = min(150, basket.width + 20)
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
        controls = font.render("Controls: LEFT / RIGHT arrows | P = pause | R = restart", True, (200, 200, 200))
        info = font.render("Modifiers: slow, wide, extra life, bonus", True, (255, 200, 100))
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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

