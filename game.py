import random
import pygame

pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Prinde mingea!")
clock = pygame.time.Clock()

basket = pygame.Rect(250, 350, 100, 20)
ball = pygame.Rect(290, 0, 20, 20)

score = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Muta cosul
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and basket.left > 0:
        basket.x -= 5

    if keys[pygame.K_RIGHT] and basket.right < 600:
        basket.x += 5

    # 2. Fa mingea sa cada
    ball.y += 4

    # 3. Verifica daca mingea a fost prinsa de cos
    if ball.colliderect(basket):
        score += 1
        ball.x = random.randint(0, 580)
        ball.y = 0

    # 4. Reseteaza mingea daca ajunge jos
    if ball.top > 400:
        ball.x = random.randint(0, 580)
        ball.y = 0

    screen.fill((30, 35, 50))

    pygame.draw.rect(screen, (70, 160, 240), basket)
    pygame.draw.ellipse(screen, (255, 180, 60), ball)

    # Afiseaza scorul
    font = pygame.font.SysFont(None, 30)
    text = font.render("Scor: " + str(score), True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
