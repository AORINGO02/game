import pygame
import random
import sys

pygame.init()
screen = pygame.display.set_mode((400, 600))
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 30)

# --- ゲーム設定・定数 ---
player_rect = pygame.Rect(200, 550, 40, 40)
bullets = []
enemies = []  # [Rect, hp, score_value] の形式で管理
hp = 3
score = 0
spawn_timer = 0
game_over = False

# 難易度調整用定数
BASE_SPEED = 3.0
SPEED_INCREASE_RATE = 0.2
SPEED_THRESHOLD = 500
MAX_SPEED = 8.0

while True:
    screen.fill((0, 0, 0))
    
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player_rect.x + 15, player_rect.y, 10, 10))

    if not game_over:
        # プレイヤー移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.x > 0: player_rect.x -= 5
        if keys[pygame.K_RIGHT] and player_rect.x < 360: player_rect.x += 5

        # 難易度計算
        speed_increment = (score // SPEED_THRESHOLD) * SPEED_INCREASE_RATE
        enemy_speed = min(BASE_SPEED + speed_increment, MAX_SPEED)

        # 敵生成
        spawn_timer += 1
        if spawn_timer > max(10, 60 - (score // 200)):
            spawn_timer = 0
            # スコア2000以上で強敵を出現 [Rect, HP, SCORE_VALUE]
            if score >= 2000 and random.random() < 0.2:
                enemies.append([pygame.Rect(random.randint(0, 360), 0, 30, 30), 2, 300])
            else:
                enemies.append([pygame.Rect(random.randint(0, 360), 0, 30, 30), 1, 100])

        # 弾の処理
        for b in bullets[:]:
            b.y -= 10
            if b.y < 0:
                bullets.remove(b); continue
            for e_data in enemies[:]:
                e, e_hp, e_score = e_data
                if b.colliderect(e):
                    bullets.remove(b)
                    e_hp -= 1
                    if e_hp <= 0:
                        score += e_score
                        enemies.remove(e_data)
                    else:
                        e_data[1] = e_hp
                    break

        # 敵の処理
        for e_data in enemies[:]:
            e, e_hp, e_score = e_data
            e.y += enemy_speed
            if e.colliderect(player_rect):
                enemies.remove(e_data)
                hp -= 1
                if hp <= 0: game_over = True
            elif e.y > 600:
                enemies.remove(e_data)

        # 描画
        for e_data in enemies:
            color = (255, 100, 100) if e_data[1] == 2 else (255, 0, 0)
            pygame.draw.rect(screen, color, e_data[0])
        for b in bullets: pygame.draw.rect(screen, (255, 255, 0), b)
        pygame.draw.rect(screen, (0, 255, 0), player_rect)
    
    # UI表示
    score_text = font.render(f"Score: {score} Speed: {enemy_speed:.1f}", True, (255, 255, 255))
    hp_text = font.render(f"HP: {hp}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(hp_text, (10, 40))

    if game_over:
        screen.fill((255, 0, 0))
        over_text = font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(over_text, (130, 300))

    pygame.display.flip()
    clock.tick(60)