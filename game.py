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

    # 2. Fa mingea sa cada
    ball.y += 4
    # 3. Verifica daca mingea a fost prinsa de cos

    # 4. Resball.y 

    screen.fill((30, 35, 50))
    pygame.draw.rect(screen, (70, 160, 240), basket)
    pygame.draw.ellipse(screen, (255, 180, 60), ball)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()