import random
import pygame

pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Prinde mingea!")
clock = pygame.time.Clock()

basket = pygame.Rect(250, 350, 100, 20)
ball = pygame.Rect(290, 0, 20, 20)

score = 0
speed = 4
running = True

font = pygame.font.SysFont(None, 30)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Muta cosul
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        basket.x -= 5

    if keys[pygame.K_RIGHT]:
        basket.x += 5

    # Nu lasa cosul sa iasa din ecran
    basket.x = max(0, min(500, basket.x))

    # 2. Fa mingea sa cada
    ball.y += speed

    # 3. Verifica daca mingea a fost prinsa de cos
    if ball.colliderect(basket):
        score += 1
        ball.x = random.randint(0, 580)
        ball.y = 0

    # 4. Reseteaza mingea daca a cazut jos
    if ball.y > 400:
        ball.x = random.randint(0, 580)
        ball.y = 0

    screen.fill((30, 35, 50))

    pygame.draw.rect(screen, (70, 160, 240), basket)
    pygame.draw.ellipse(screen, (255, 180, 60), ball)

    # Afiseaza scorul
    text = font.render("Scor: " + str(score), True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

