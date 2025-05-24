# -*- coding: utf-8 -*-
import pygame
import sys
import random
import time

# Pygameの初期化
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

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

# 音声ファイルの読み込み
def load_voice_files():
    """音声ファイルを読み込む"""
    voice_files = []
    for i in range(1, 4):
        try:
            voice_file = f"Voice{i}.mp3"
            sound = pygame.mixer.Sound(voice_file)
            voice_files.append(sound)
            print(f"{voice_file} を読み込みました")
        except Exception as e:
            print(f"Error loading {voice_file}: {e}")
    return voice_files

# 音声ファイルを読み込み
voice_sounds = load_voice_files()

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
        self.saying_text = "だるまさんが"
        
        # 音声関連
        self.current_voice = None
        self.voice_channel = None
        self.voice_start_time = 0
        self.voice_duration = 0
        self.playback_speed = 1.0  # 再生速度
        self.is_playing_voice = False
        
        # 次の振り返りまでの時間を設定
        self.schedule_next_turn()
    
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
            
            # 音声がまだ再生されていない場合は開始
            if not self.is_playing_voice and self.turn_timer > 0.1:  # 少し遅延を入れる
                self.start_voice()
            
            # 音声が終了したか、時間が経過したら振り返る
            if (self.is_voice_finished() and self.turn_timer >= self.turn_duration) or \
               (not voice_sounds and self.turn_timer >= self.turn_duration):
                self.facing_back = False
                self.turn_timer = 0
                self.saying_text = "転んだ！"
                self.stop_voice()
        else:
            self.saying_text = "転んだ！"
            if self.turn_timer >= self.back_duration:
                self.facing_back = True
                self.turn_timer = 0
                self.saying_text = "だるまさんが"
                self.schedule_next_turn()  # 次の振り返りをスケジュール
    
    def schedule_next_turn(self):
        """次の振り返りタイミングをスケジュール"""
        if voice_sounds:
            # ランダムに音声ファイルを選択
            self.current_voice = random.choice(voice_sounds)
            # 音声の長さを取得（秒）
            self.voice_duration = self.current_voice.get_length()
            # 再生速度をランダムに設定（0.8〜1.2倍）
            self.playback_speed = random.uniform(0.8, 1.2)
            # 速度調整後の実際の再生時間
            self.actual_duration = self.voice_duration / self.playback_speed
            # 振り返るまでの時間を音声の長さより0.02秒早く設定
            self.turn_duration = max(0.1, self.actual_duration - 0.02)
        else:
            # 音声ファイルがない場合は従来通り
            self.turn_duration = random.uniform(2.0, 5.0)
        
        self.back_duration = random.uniform(1.0, 3.0)
    
    def start_voice(self):
        """音声再生を開始"""
        if self.current_voice and voice_sounds:
            try:
                # 再生速度を調整して再生
                # Pygameでは直接速度調整できないので、音声の周波数を調整
                self.voice_channel = self.current_voice.play()
                self.voice_start_time = time.time()
                self.is_playing_voice = True
                print(f"音声再生開始 - 速度: {self.playback_speed:.2f}x, 長さ: {self.actual_duration:.2f}秒")
            except Exception as e:
                print(f"音声再生エラー: {e}")
    
    def stop_voice(self):
        """音声再生を停止"""
        if self.voice_channel and self.voice_channel.get_busy():
            self.voice_channel.stop()
        self.is_playing_voice = False
    
    def is_voice_finished(self):
        """音声が終了したかチェック"""
        if not self.is_playing_voice:
            return True
        
        if self.voice_channel and not self.voice_channel.get_busy():
            return True
        
        # 時間ベースでもチェック
        elapsed = time.time() - self.voice_start_time
        return elapsed >= self.actual_duration

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
        # 音声を停止
        if hasattr(self.daruma, 'stop_voice'):
            self.daruma.stop_voice()
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
