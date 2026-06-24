import sys

try:
    import pygame
except ModuleNotFoundError:
    print("ERROR: pygame is not installed. Please install it with 'pip install pygame' or your system package manager.")
    sys.exit(1)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 10
PLAYER_SIZE = 40
BULLET_SIZE = 10


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
    player_y = SCREEN_HEIGHT - PLAYER_SIZE - 20
    bullets = []

    while True:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append([player_x + PLAYER_SIZE // 2 - BULLET_SIZE // 2, player_y])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            player_x += PLAYER_SPEED

        player_x = max(0, min(player_x, SCREEN_WIDTH - PLAYER_SIZE))

        pygame.draw.rect(screen, (0, 255, 0), (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))

        active_bullets = []
        for b in bullets:
            b[1] -= BULLET_SPEED
            if b[1] + BULLET_SIZE >= 0:
                active_bullets.append(b)
                pygame.draw.rect(screen, (255, 255, 0), (b[0], b[1], BULLET_SIZE, BULLET_SIZE))
        bullets = active_bullets

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
