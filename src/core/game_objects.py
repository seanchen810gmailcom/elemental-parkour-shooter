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
