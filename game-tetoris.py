import pygame
import sys
import random

# 設定
SCREEN_WIDTH, SCREEN_HEIGHT = 450, 600  # 右側にNextを表示するために幅を拡大
BLOCK_SIZE = 30
COLS, ROWS = 10, 20

SHAPES = [
    [[1, 1, 1, 1]], [[1, 1], [1, 1]], [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]], [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]], [[1, 1, 0], [0, 1, 1]]
]

pygame.init()
pygame.key.set_repeat(200, 150)
font = pygame.font.SysFont(None, 30)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
current_piece = random.choice(SHAPES)
next_piece = random.choice(SHAPES)
piece_x, piece_y = 3, 0
score = 0
game_over = False
fall_time = 0

# 落下速度をスコアに応じて加速
def get_fall_speed(score):
    return max(100, 500 - (score // 500) * 50)

def rotate(piece):
    return [list(row) for row in zip(*piece[::-1])]

def valid(px, py, piece):
    for y, row in enumerate(piece):
        for x, val in enumerate(row):
            if val:
                if px+x < 0 or px+x >= COLS or py+y >= ROWS or (py+y >= 0 and field[py+y][px+x]):
                    return False
    return True

while True:
    screen.fill((0, 0, 0))
    dt = clock.tick(60)
    fall_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and valid(piece_x-1, int(piece_y), current_piece): piece_x -= 1
            if event.key == pygame.K_RIGHT and valid(piece_x+1, int(piece_y), current_piece): piece_x += 1
            if event.key == pygame.K_DOWN and valid(piece_x, int(piece_y)+1, current_piece): piece_y += 1
            if event.key == pygame.K_UP:
                rotated = rotate(current_piece)
                if valid(piece_x, int(piece_y), rotated): current_piece = rotated

    if not game_over:
        if fall_time > get_fall_speed(score):
            if valid(piece_x, int(piece_y)+1, current_piece):
                piece_y += 1
            else:
                for y, row in enumerate(current_piece):
                    for x, val in enumerate(row):
                        if val: field[int(piece_y)+y][piece_x+x] = 1
                
                # 行消去
                for y in range(ROWS):
                    if all(field[y]):
                        del field[y]
                        field.insert(0, [0 for _ in range(COLS)])
                        score += 100
                
                current_piece = next_piece
                next_piece = random.choice(SHAPES)
                piece_x, piece_y = 3, 0
                if not valid(piece_x, int(piece_y), current_piece):
                    game_over = True
            fall_time = 0

    # 描画
    for y in range(ROWS):
        for x in range(COLS):
            if field[y][x]: pygame.draw.rect(screen, (255, 255, 255), (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1))
            else: pygame.draw.rect(screen, (30, 30, 30), (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    # 現在ピースとネクストピースの描画
    if not game_over:
        for y, row in enumerate(current_piece):
            for x, val in enumerate(row):
                if val: pygame.draw.rect(screen, (255, 0, 0), ((piece_x+x)*BLOCK_SIZE, (int(piece_y)+y)*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1))
    
    # UI表示
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    next_text = font.render("Next:", True, (255, 255, 255))
    screen.blit(score_text, (310, 20))
    screen.blit(next_text, (310, 80))
    for y, row in enumerate(next_piece):
        for x, val in enumerate(row):
            if val: pygame.draw.rect(screen, (0, 255, 255), (320 + x*20, 120 + y*20, 18, 18))

    if game_over:
        over_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(over_text, (70, 280))

    pygame.display.flip()