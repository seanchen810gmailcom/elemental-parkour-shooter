######################載入套件######################
import pygame
import time
import random
from config import *
from element_system import ElementSystem

######################傷害數字顯示系統######################


class DamageNumber:
    """
    傷害數字顯示 - 在螢幕上顯示傷害數值和效果\n
    \n
    用於視覺反饋，讓玩家清楚看到：\n
    1. 造成的傷害數值\n
    2. 是否觸發弱點攻擊\n
    3. 狀態效果是否生效\n
    \n
    參數:\n
    x (float): 顯示位置 X 座標\n
    y (float): 顯示位置 Y 座標\n
    damage (int): 傷害數值\n
    damage_type (str): 傷害類型描述\n
    color (tuple): 顯示顏色\n
    size_multiplier (float): 字體大小倍率\n
    """

    def __init__(
        self, x, y, damage, damage_type="普通傷害", color=WHITE, size_multiplier=1.0
    ):
        self.x = x + random.uniform(-10, 10)  # 加入隨機偏移避免重疊
        self.y = y + random.uniform(-5, 5)
        self.start_x = self.x
        self.start_y = self.y

        self.damage = damage
        self.damage_type = damage_type
        self.color = color
        self.size_multiplier = size_multiplier

        # 動畫屬性
        self.lifetime = 2.0  # 顯示時間（秒）
        self.creation_time = time.time()
        self.velocity_y = -30  # 向上飄動速度
        self.alpha = 255  # 透明度

        # 字體設定
        self.font_size = max(16, int(24 * size_multiplier))
        self.font = pygame.font.Font(None, self.font_size)

    def update(self):
        """
        更新傷害數字的位置和透明度\n
        \n
        回傳:\n
        bool: True 表示還需要繼續顯示，False 表示可以移除\n
        """
        current_time = time.time()
        elapsed = current_time - self.creation_time

        if elapsed >= self.lifetime:
            return False  # 生命週期結束

        # 更新位置（向上飄動）
        self.y += self.velocity_y * (1 / 60)  # 假設60 FPS
        self.velocity_y *= 0.98  # 逐漸減速

        # 更新透明度（逐漸消失）
        fade_progress = elapsed / self.lifetime
        self.alpha = int(255 * (1 - fade_progress))

        return True

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製傷害數字\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 建立文字表面
        damage_text = self.font.render(str(self.damage), True, self.color)

        # 計算繪製位置（置中）
        text_rect = damage_text.get_rect()
        text_rect.center = (int(screen_x), int(screen_y))

        # 繪製傷害數字
        screen.blit(damage_text, text_rect)

        # 如果有特殊效果，在下方顯示類型
        if self.damage_type != "普通傷害":
            type_font = pygame.font.Font(None, max(12, int(16 * self.size_multiplier)))
            type_text = type_font.render(self.damage_type, True, self.color)
            type_rect = type_text.get_rect()
            type_rect.center = (int(screen_x), int(screen_y + text_rect.height))
            screen.blit(type_text, type_rect)


######################傷害顯示管理器######################


class DamageDisplayManager:
    """
    傷害顯示管理器 - 統一管理所有傷害數字的顯示\n
    \n
    負責：\n
    1. 建立新的傷害數字顯示\n
    2. 更新所有傷害數字的動畫\n
    3. 移除過期的傷害數字\n
    4. 提供方便的介面給其他系統使用\n
    """

    def __init__(self):
        self.damage_numbers = []  # 所有活躍的傷害數字

    def add_damage_number(self, x, y, damage, attacker_element=None, target_type=None):
        """
        加入新的傷害數字顯示\n
        \n
        參數:\n
        x (float): 顯示位置 X 座標\n
        y (float): 顯示位置 Y 座標\n
        damage (int): 基礎傷害值\n
        attacker_element (str): 攻擊者元素屬性\n
        target_type (str): 目標類型\n
        \n
        回傳:\n
        DamageNumber: 新建立的傷害數字物件\n
        """
        if attacker_element and target_type:
            # 使用屬性系統計算顯示資訊
            popup_info = ElementSystem.create_damage_popup_info(
                damage, attacker_element, target_type
            )

            damage_number = DamageNumber(
                x,
                y,
                popup_info["damage"],
                popup_info["description"],
                popup_info["color"],
                popup_info["size_multiplier"],
            )
        else:
            # 預設的傷害顯示
            damage_number = DamageNumber(x, y, damage)

        self.damage_numbers.append(damage_number)
        return damage_number

    def add_healing_number(self, x, y, heal_amount):
        """
        加入治療數字顯示\n
        \n
        參數:\n
        x (float): 顯示位置 X 座標\n
        y (float): 顯示位置 Y 座標\n
        heal_amount (int): 治療量\n
        """
        healing_number = DamageNumber(x, y, heal_amount, "恢復", GREEN, 1.2)
        self.damage_numbers.append(healing_number)
        return healing_number

    def add_status_effect_text(self, x, y, effect_name):
        """
        加入狀態效果文字顯示\n
        \n
        參數:\n
        x (float): 顯示位置 X 座標\n
        y (float): 顯示位置 Y 座標\n
        effect_name (str): 狀態效果名稱\n
        """
        effect_colors = {"減速": CYAN, "麻痺": YELLOW, "燃燒": RED, "冰凍": WHITE}

        color = effect_colors.get(effect_name, PURPLE)

        # 狀態效果顯示不使用數字，直接顯示效果名稱
        status_display = DamageNumber(x, y, 0, effect_name, color, 0.8)  # 不顯示數字

        # 修改顯示方式
        status_display.damage = ""  # 不顯示數字部分

        self.damage_numbers.append(status_display)
        return status_display

    def update(self):
        """
        更新所有傷害數字的狀態\n
        """
        # 更新每個傷害數字
        active_numbers = []

        for number in self.damage_numbers:
            if number.update():
                active_numbers.append(number)

        self.damage_numbers = active_numbers

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有傷害數字\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        for number in self.damage_numbers:
            number.draw(screen, camera_x, camera_y)

    def clear_all(self):
        """
        清除所有傷害數字顯示\n
        """
        self.damage_numbers.clear()

    def get_active_count(self):
        """
        獲取當前活躍的傷害數字數量\n
        \n
        回傳:\n
        int: 活躍傷害數字數量\n
        """
        return len(self.damage_numbers)
