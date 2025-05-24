# -*- coding: utf-8 -*-
import pygame
import sys
import random
import time

# Pygameの初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("だるまさんが転んだ")

# 色の定義
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# フォント設定
# システムで利用可能な日本語フォントを使用
def get_japanese_font():
    # まずシステムフォントを試す
    japanese_fonts = [
        'hiraginosansgb',      # macOSの標準日本語フォント
        'applesdgothicneo',    # macOSの標準日本語フォント
        'yugothic',            # Windows/Linux
        'meiryo',              # Windows
        'notosanscjk',         # Linux
    ]
    
    for font_name in japanese_fonts:
        try:
            test_font = pygame.font.SysFont(font_name, 36)
            # 日本語が正しく描画できるかテスト
            test_surface = test_font.render('あ', True, (0, 0, 0))
            if test_surface.get_width() > 10:  # 文字が描画されているかチェック
                print(f"日本語フォント '{font_name}' を使用します")
                return test_font
        except Exception as e:
            continue
    
    # システムの標準的な日本語フォントパスを試す
    font_paths = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/AssetsV2/com_apple_MobileAsset_Font6/AppleSDGothicNeo-Regular.otf",
    ]
    
    for font_path in font_paths:
        try:
            if pygame.font.get_init():
                test_font = pygame.font.Font(font_path, 36)
                test_surface = test_font.render('あ', True, (0, 0, 0))
                if test_surface.get_width() > 10:
                    print(f"TTFフォント '{font_path}' を使用します")
                    return test_font
        except:
            continue
    
    # フォールバック
    print("Warning: 適切な日本語フォントが見つかりませんでした。デフォルトフォントを使用します。")
    return pygame.font.Font(None, 36)

font = get_japanese_font()

# プレイヤークラス
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 50
        self.speed = 5
        self.color = BLUE
        self.moving = False
        self.eliminated = False
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def move(self, keys):
        self.moving = False
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
            self.moving = True
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed
            self.moving = True
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
            self.moving = True
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
            self.moving = True
    
    def check_goal(self, goal_x):
        return self.x + self.width >= goal_x

# だるまクラス
class Daruma:
    def __init__(self):
        self.x = WIDTH - 100
        self.y = HEIGHT // 2 - 75
        self.width = 50
        self.height = 150
        self.color = RED
        self.facing_back = True
        self.turn_timer = 0
        self.turn_duration = random.uniform(2.0, 5.0)
        self.back_duration = random.uniform(1.0, 3.0)
        self.saying_text = "だるまさんが"
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # 向きを表示（簡易的に）
        eye_color = BLACK if not self.facing_back else self.color
        pygame.draw.circle(screen, eye_color, (self.x + 10, self.y + 30), 5)
        pygame.draw.circle(screen, eye_color, (self.x + 40, self.y + 30), 5)
        
        # テキスト表示
        text = font.render(self.saying_text, True, BLACK)
        screen.blit(text, (self.x - 150, self.y - 50))
    
    def update(self, dt):
        self.turn_timer += dt
        
        if self.facing_back:
            self.saying_text = "だるまさんが"
            if self.turn_timer >= self.turn_duration:
                self.facing_back = False
                self.turn_timer = 0
                self.turn_duration = random.uniform(2.0, 5.0)
                self.saying_text = "転んだ！"
        else:
            self.saying_text = "転んだ！"
            if self.turn_timer >= self.back_duration:
                self.facing_back = True
                self.turn_timer = 0
                self.back_duration = random.uniform(1.0, 3.0)
                self.saying_text = "だるまさんが"

# ゲームクラス
class Game:
    def __init__(self):
        self.player = Player(50, HEIGHT // 2)
        self.daruma = Daruma()
        self.goal_x = WIDTH - 150
        self.game_over = False
        self.win = False
        self.clock = pygame.time.Clock()
    
    def check_caught(self):
        if not self.daruma.facing_back and self.player.moving:
            self.game_over = True
            self.player.color = (100, 100, 100)  # グレーに変更
    
    def check_win(self):
        if self.player.check_goal(self.goal_x):
            self.win = True
            self.game_over = True
    
    def draw(self):
        screen.fill(WHITE)
        
        # ゴールラインを描画
        pygame.draw.line(screen, GREEN, (self.goal_x, 0), (self.goal_x, HEIGHT), 5)
        
        self.player.draw()
        self.daruma.draw()
        
        if self.game_over:
            if self.win:
                text = font.render("ゴール！あなたの勝ちです！", True, GREEN)
            else:
                text = font.render("動いているところを見られました！あなたの負けです！", True, RED)
            screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2))
            
            restart_text = font.render("Rキーでリスタート", True, BLACK)
            screen.blit(restart_text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
    
    def reset(self):
        self.__init__()
    
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0  # デルタタイム（秒）
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset()
            
            keys = pygame.key.get_pressed()
            
            if not self.game_over:
                self.player.move(keys)
                self.daruma.update(dt)
                self.check_caught()
                self.check_win()
            
            self.draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

# ゲーム実行
if __name__ == "__main__":
    game = Game()
    game.run()
