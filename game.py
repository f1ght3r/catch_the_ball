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
       
if game_state == "start":
    screen.fill((30, 35, 50))

    font = pygame.font.SysFont(None, 50)
    text = font.render("PRINDE MINGEA!", True, (255, 180, 60))
    screen.blit(text, (160, 100))

    font = pygame.font.SysFont(None, 30)
    text = font.render("ENTER - Incepe jocul", True, (255, 255, 255))
    screen.blit(text, (190, 180))

    text = font.render("I - Instructiuni", True, (255, 255, 255))
    screen.blit(text, (210, 220))


# 6. instructiuni
elif game_state == "instructions":
    screen.fill((30, 35, 50))

    font = pygame.font.SysFont(None, 35)

    instructions = [
        "INSTRUCTIUNI:",
        "SAGETI STANGA/DREAPTA - misca cosul",
        "Prinde mingea pentru puncte!",
        "P - Pauza",
        "ESC - Inapoi la meniu"
    ]

    for i, line in enumerate(instructions):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (50, 80 + i * 50))


# 7. pauza
elif game_state == "pause":
    screen.fill((30, 35, 50))

    font = pygame.font.SysFont(None, 50)
    text = font.render("JOCUL ESTE IN PAUZA", True, (255, 180, 60))
    screen.blit(text, (110, 130))

    font = pygame.font.SysFont(None, 30)
    text = font.render("Apasa P pentru a continua", True, (255, 255, 255))
    screen.blit(text, (150, 200))


    

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
