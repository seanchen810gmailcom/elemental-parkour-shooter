######################載入套件######################
import pygame
import math
import time

# 支援直接執行和模組執行兩種方式
try:
    from ..config import *
except ImportError:
    from src.config import *

######################基礎物件類別######################


class GameObject:
    """
    遊戲物件的基礎類別 - 所有遊戲元素的父類別\n
    \n
    提供所有遊戲物件的共通功能：\n
    1. 位置和尺寸管理\n
    2. 基本繪製功能\n
    3. 碰撞檢測用的矩形區域\n
    \n
    參數:\n
    x (float): 物件的 X 座標，範圍 0 ~ SCREEN_WIDTH\n
    y (float): 物件的 Y 座標，範圍 0 ~ SCREEN_HEIGHT\n
    width (int): 物件寬度，範圍 > 0\n
    height (int): 物件高度，範圍 > 0\n
    color (tuple): RGB 顏色值，格式 (r, g, b)，範圍 0-255\n
    \n
    屬性:\n
    rect (pygame.Rect): 碰撞檢測用的矩形區域\n
    """

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        # 建立碰撞檢測用的矩形，會跟著物件位置更新
        self.rect = pygame.Rect(x, y, width, height)

    def update_rect(self):
        """
        更新物件的碰撞矩形位置 - 當物件移動後必須呼叫\n
        \n
        確保 rect 屬性與實際的 x, y 座標同步，\n
        這對碰撞檢測非常重要。\n
        """
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        在螢幕上繪製物件 - 基本的矩形繪製\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        繪製方式:\n
        使用 pygame.draw.rect 繪製實心矩形\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        screen_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, self.color, screen_rect)


######################平台類別######################


class Platform(GameObject):
    """
    遊戲平台類別 - 玩家可以站立的地面或平台\n
    \n
    繼承自 GameObject，提供：\n
    1. 靜態平台功能（不會移動）\n
    2. 碰撞檢測支援\n
    3. 視覺化繪製\n
    \n
    參數:\n
    x (float): 平台左側 X 座標\n
    y (float): 平台頂部 Y 座標\n
    width (int): 平台寬度，範圍 > 0\n
    height (int): 平台高度，通常使用 PLATFORM_HEIGHT\n
    """

    def __init__(self, x, y, width, height=PLATFORM_HEIGHT):
        super().__init__(x, y, width, height, PLATFORM_COLOR)
        self.is_solid = True  # 標記這是實體平台，可以站立


######################狀態效果類別######################


class StatusEffect:
    """
    狀態效果系統 - 處理減速、麻痺等暫時性效果\n
    \n
    管理施加在怪物或玩家身上的各種狀態效果，\n
    包含效果類型、強度和持續時間。\n
    \n
    參數:\n
    effect_type (str): 效果類型，'slow' 或 'paralysis'\n
    duration (float): 效果持續時間（秒），範圍 > 0\n
    intensity (float): 效果強度，範圍 0.0-1.0\n
    \n
    回傳:\n
    bool: is_active() 回傳效果是否仍在作用中\n
    float: get_speed_modifier() 回傳移動速度修正值\n
    """

    def __init__(self, effect_type, duration, intensity):
        self.effect_type = effect_type  # 'slow', 'paralysis' 等
        self.duration = duration  # 持續時間（秒）
        self.intensity = intensity  # 效果強度 (0.0 - 1.0)
        self.start_time = time.time()  # 記錄開始時間

    def is_active(self):
        """
        檢查效果是否仍在作用中\n
        \n
        回傳:\n
        bool: True 表示效果還在持續，False 表示已經結束\n
        """
        return time.time() - self.start_time < self.duration

    def get_speed_modifier(self):
        """
        獲取移動速度的修正倍率\n
        \n
        根據狀態效果類型回傳對應的速度修正：\n
        - slow: 根據 intensity 減速\n
        - paralysis: 完全無法移動\n
        - 其他: 不影響速度\n
        \n
        回傳:\n
        float: 速度修正倍率，1.0 = 正常速度，0.0 = 完全停止\n
        """
        if not self.is_active():
            return 1.0  # 效果結束，恢復正常速度

        if self.effect_type == "slow":
            # 減速效果：速度變成原本的 (1 - intensity)
            return 1.0 - self.intensity
        elif self.effect_type == "paralysis":
            # 麻痺效果：完全無法移動
            return 0.0

        return 1.0  # 預設不影響速度


######################愛心道具類別######################


class HealthPickup(GameObject):
    """
    愛心道具類別 - 玩家可以拾取來恢復生命值\n
    \n
    提供生命值恢復功能：\n
    1. 玩家碰到後恢復生命值\n
    2. 閃爍動畫效果\n
    3. 拾取後消失\n
    \n
    參數:\n
    x (float): 愛心的 X 座標\n
    y (float): 愛心的 Y 座標\n
    heal_amount (int): 恢復的生命值，默認 10\n
    """

    def __init__(self, x, y, heal_amount=10):
        super().__init__(x, y, 20, 20, (255, 105, 180))  # 粉紅色愛心
        self.heal_amount = heal_amount
        self.collected = False
        self.animation_timer = 0
        self.pulse_scale = 1.0

    def update(self, dt):
        """
        更新愛心動畫效果

        參數:
        dt (float): 時間間隔
        """
        self.animation_timer += dt
        # 創建脈衝效果
        self.pulse_scale = 1.0 + 0.2 * math.sin(self.animation_timer * 4)

    def check_collision(self, player):
        """
        檢查玩家是否拾取了愛心

        參數:
        player (Player): 玩家物件

        回傳:
        bool: 是否被拾取
        """
        if self.collected:
            return False

        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        heart_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if player_rect.colliderect(heart_rect):
            # 恢復玩家生命值
            if player.health < player.max_health:
                old_health = player.health
                player.heal(self.heal_amount)
                print(f"💚 撿到愛心！生命值：{old_health} → {player.health}")
                self.collected = True
                return True

        return False

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製愛心道具

        參數:
        screen (pygame.Surface): 要繪製到的螢幕表面
        camera_x (int): 攝影機 x 偏移
        camera_y (int): 攝影機 y 偏移
        """
        if self.collected:
            return

        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 只在螢幕範圍內繪製
        if (
            -50 <= screen_x <= SCREEN_WIDTH + 50
            and -50 <= screen_y <= SCREEN_HEIGHT + 50
        ):

            # 計算縮放後的尺寸
            scaled_size = int(self.width * self.pulse_scale)
            center_x = int(screen_x + self.width // 2)
            center_y = int(screen_y + self.height // 2)

            # 繪製愛心形狀
            self.draw_heart(screen, center_x, center_y, scaled_size)

    def draw_heart(self, screen, center_x, center_y, size):
        """
        繪製愛心形狀

        參數:
        screen (pygame.Surface): 螢幕表面
        center_x (int): 中心 X 座標
        center_y (int): 中心 Y 座標
        size (int): 愛心大小
        """
        # 愛心顏色（亮粉紅色）
        heart_color = (255, 105, 180)

        # 繪製愛心的兩個圓
        radius = size // 4
        # 左上圓
        pygame.draw.circle(
            screen,
            heart_color,
            (center_x - radius // 2, center_y - radius // 2),
            radius,
        )
        # 右上圓
        pygame.draw.circle(
            screen,
            heart_color,
            (center_x + radius // 2, center_y - radius // 2),
            radius,
        )

        # 繪製愛心的下方三角形
        triangle_points = [
            (center_x - size // 2, center_y),
            (center_x + size // 2, center_y),
            (center_x, center_y + size // 2),
        ]
        pygame.draw.polygon(screen, heart_color, triangle_points)


######################尖刺陷阱類別######################


class SpikeHazard(GameObject):
    """
    尖刺陷阱類別 - 對玩家造成傷害的危險區域\n
    \n
    提供陷阱功能：\n
    1. 玩家碰到會受到傷害\n
    2. 尖銳的視覺效果\n
    3. 可設定傷害量\n
    \n
    參數:\n
    x (float): 尖刺的 X 座標\n
    y (float): 尖刺的 Y 座標\n
    width (int): 尖刺寬度\n
    height (int): 尖刺高度\n
    damage (int): 造成的傷害值，默認 15\n
    """

    def __init__(self, x, y, width=40, height=30, damage=15):
        super().__init__(x, y, width, height, (128, 128, 128))  # 灰色基底
        self.damage = damage
        self.spike_color = (64, 64, 64)  # 深灰色尖刺
        self.blood_color = (139, 0, 0)  # 暗紅色血跡

    def check_collision(self, player):
        """
        檢查玩家是否碰到尖刺

        參數:
        player (Player): 玩家物件

        回傳:
        int: 造成的傷害值，0 表示沒有碰撞
        """
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        spike_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if player_rect.colliderect(spike_rect):
            return self.damage

        return 0

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製尖刺陷阱

        參數:
        screen (pygame.Surface): 要繪製到的螢幕表面
        camera_x (int): 攝影機 x 偏移
        camera_y (int): 攝影機 y 偏移
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 只在螢幕範圍內繪製
        if (
            -50 <= screen_x <= SCREEN_WIDTH + 50
            and -50 <= screen_y <= SCREEN_HEIGHT + 50
        ):

            # 繪製尖刺基座
            base_rect = pygame.Rect(
                screen_x, screen_y + self.height - 10, self.width, 10
            )
            pygame.draw.rect(screen, self.color, base_rect)

            # 繪製多個尖刺
            spike_count = max(2, self.width // 15)  # 根據寬度決定尖刺數量
            spike_width = self.width // spike_count

            for i in range(spike_count):
                spike_x = screen_x + i * spike_width
                spike_points = [
                    (spike_x, screen_y + self.height - 10),  # 左下
                    (spike_x + spike_width, screen_y + self.height - 10),  # 右下
                    (spike_x + spike_width // 2, screen_y),  # 頂點
                ]
                pygame.draw.polygon(screen, self.spike_color, spike_points)

                # 在尖刺頂端添加血跡效果
                blood_points = [
                    (spike_x + spike_width // 2 - 2, screen_y + 2),
                    (spike_x + spike_width // 2 + 2, screen_y + 2),
                    (spike_x + spike_width // 2, screen_y),
                ]
                pygame.draw.polygon(screen, self.blood_color, blood_points)
