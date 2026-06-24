import pygame
import sys
import random

# 設定
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
FPS = 60
GRAVITY = 0.8

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

def reset_round(game):
    game["player"].update({"rect": pygame.Rect(100, 250, 50, 100), "hp": 100, "vel_y": 0, "is_jumping": False, "is_crouching": False, "attack_rect": None, "attack_timer": 0})
    game["enemy"].update({"rect": pygame.Rect(600, 250, 50, 100), "hp": 100, "vel_y": 0, "is_jumping": False, "is_crouching": False, "attack_rect": None, "attack_timer": 0})

game = {"player": {}, "enemy": {}, "round_wins": {"player": 0, "enemy": 0}, "current_round": 1}
reset_round(game)

while True:
    screen.fill((30, 30, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game["player"]["attack_rect"]:
            game["player"]["attack_rect"] = pygame.Rect(game["player"]["rect"].right, game["player"]["rect"].y + 20, 50, 30)
            game["player"]["attack_timer"] = 10

    # --- プレイヤー操作 ---
    p = game["player"]
    keys = pygame.key.get_pressed()
    
    # 衝突判定付き移動
    dx = (keys[pygame.K_d] - keys[pygame.K_a]) * 5
    next_p = p["rect"].move(dx, 0)
    if not next_p.colliderect(game["enemy"]["rect"]): p["rect"].x = next_p.x
    
    if keys[pygame.K_w] and not p["is_jumping"]: p["vel_y"] = -15; p["is_jumping"] = True
    p["is_crouching"] = keys[pygame.K_s]
    p["rect"].height = 50 if p["is_crouching"] else 100
    
    p["vel_y"] += GRAVITY; p["rect"].y += p["vel_y"]
    if p["rect"].bottom >= 350: p["rect"].bottom = 350; p["vel_y"] = 0; p["is_jumping"] = False

    # --- 敵AI行動（賢く） ---
    e = game["enemy"]
    dist = p["rect"].x - e["rect"].x
    
    # 1. ジャンプ攻撃と追尾
    if abs(dist) < 150 and not e["is_jumping"] and random.random() < 0.05:
        e["vel_y"] = -15; e["is_jumping"] = True
    elif abs(dist) > 80: # 接近
        e["rect"].x += (2 if dist > 0 else -2)
    
    # 2. しゃがみ回避・攻撃
    e["is_crouching"] = (p["attack_timer"] > 0 and random.random() < 0.5)
    if random.random() < 0.02 and not e["attack_rect"]:
        e["attack_rect"] = pygame.Rect(e["rect"].left - 50, e["rect"].y + 20, 50, 30)
        e["attack_timer"] = 10

    e["vel_y"] += GRAVITY; e["rect"].y += e["vel_y"]
    if e["rect"].bottom >= 350: e["rect"].bottom = 350; e["vel_y"] = 0; e["is_jumping"] = False
    e["rect"].height = 50 if e["is_crouching"] else 100

    # 攻撃処理
    for attacker, defender in [(p, e), (e, p)]:
        if attacker["attack_timer"] > 0:
            attacker["attack_timer"] -= 1
            if attacker["attack_rect"] and attacker["attack_rect"].colliderect(defender["rect"]) and not defender["is_crouching"]:
                defender["hp"] -= 0.5
        else: attacker["attack_rect"] = None

    # 描画
    pygame.draw.rect(screen, (0, 255, 0), p["rect"])
    pygame.draw.rect(screen, (255, 0, 0), e["rect"])
    if p["attack_rect"]: pygame.draw.rect(screen, (255, 255, 0), p["attack_rect"])
    if e["attack_rect"]: pygame.draw.rect(screen, (255, 255, 0), e["attack_rect"])

    # UI
    screen.blit(font.render(f"P HP:{int(p['hp'])} E HP:{int(e['hp'])}", True, (255, 255, 255)), (10, 10))
    if p["hp"] <= 0 or e["hp"] <= 0:
        if p["hp"] > 0: game["round_wins"]["player"] += 1
        else: game["round_wins"]["enemy"] += 1
        game["current_round"] += 1
        reset_round(game)
        if game["current_round"] > 3: pygame.quit(); sys.exit()

    pygame.display.flip()
    clock.tick(FPS)