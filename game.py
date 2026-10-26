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

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        basket.x -= 5
    if keys[pygame.K_RIGHT]:
        basket.x += 5

    if basket.x < 0:
        basket.x = 0
    if basket.x > 500:
        basket.x = 500

    # 2. Fa mingea sa cada
    ball.y += 5

    # 3. Verifica daca mingea a fost prinsa de cos
    if basket.colliderect(ball):
        ball.y = -20
        ball.x = random.randint(0, 500)
    # 4. Reseteaza mingea daca a cazut jos
    if ball.y > 600:
        ball.y = -20
        ball.x = random.randint(0, 500)

        # 5. start screen

        # 6. instructiuni (mods + comenzi de joc)

        # 7. pauza

        # 8. 3 vieti

        # 9. game over

        # 10. modifiers

        # 11. high score
    screen.fill((30, 35, 50))
    pygame.draw.rect(screen, (70, 160, 240), basket)
    pygame.draw.ellipse(screen, (255, 180, 60), ball)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
