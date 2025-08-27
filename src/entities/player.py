######################載入套件######################
import pygame
import time
import math
import random

# 嘗試相對導入，如果失敗則使用絕對導入
try:
    from ..config import *
    from ..core.game_objects import GameObject, StatusEffect
except ImportError:
    from src.config import *
    from src.core.game_objects import GameObject, StatusEffect

######################玩家類別######################


class Player(GameObject):
    """
    玩家角色類別 - 具備跑酷和戰鬥能力的主角\n
    \n
    提供完整的跑酷射擊功能：\n
    1. 基本移動（左右移動、跳躍）\n
    2. 進階跑酷（雙跳、爬牆、滑牆）\n
    3. 戰鬥系統（槍械射擊、近戰攻擊）\n
    4. 健康和狀態管理\n
    \n
    參數:\n
    x (float): 初始 X 座標\n
    y (float): 初始 Y 座標\n
    \n
    控制方式:\n
    - A/D 或 左右鍵: 左右移動\n
    - W 或 空白鍵: 跳躍\n
    - 滑鼠左鍵: 射擊\n
    - 滑鼠右鍵: 近戰攻擊\n
    - 1/2/3/4: 切換子彈類型\n
    """

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_COLOR)

        # 移動相關屬性
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.can_double_jump = True  # 是否還能二段跳
        self.is_wall_sliding = False  # 是否在滑牆
        self.wall_direction = 0  # 接觸的牆壁方向 (-1: 左牆, 1: 右牆, 0: 無牆)

        # 生命值系統
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.is_alive = True

        # 重生系統
        self.last_safe_x = x  # 上一個安全位置的x
        self.last_safe_y = y  # 上一個安全位置的y
        self.safe_position_timer = 0  # 安全位置更新計時器

        # 戰鬥相關屬性
        self.current_weapon = (
            "machine_gun"  # 當前武器類型：machine_gun, assault_rifle, shotgun, sniper
        )
        self.last_shot_time = 0  # 上次射擊時間
        self.last_melee_time = 0  # 上次近戰時間
        self.facing_direction = 1  # 面向方向 (1: 右, -1: 左)

        # 武器屬性配置
        self.weapon_configs = {
            "machine_gun": {
                "name": "機關槍",
                "fire_rate": 0.1,  # 發射率超級快
                "damage": 8,  # 大幅降低攻擊力從15到8
                "bullet_speed": 20,
                "spread": 0,  # 散布角度
                "bullets_per_shot": 1,
            },
            "assault_rifle": {
                "name": "衝鋒槍",
                "fire_rate": 0.4,  # 發射率不高
                "damage": 40,  # 攻擊力高
                "bullet_speed": 25,
                "spread": 0,
                "bullets_per_shot": 1,
            },
            "shotgun": {
                "name": "散彈槍",
                "fire_rate": 0.8,  # 發射率中等
                "damage": 25,  # 攻擊力中等
                "bullet_speed": 18,
                "spread": 1.0,  # 60度散射範圍
                "bullets_per_shot": 5,  # 一次射出5發
            },
            "sniper": {
                "name": "狙擊槍",
                "fire_rate": 1.5,  # 發射率低
                "damage": 100,  # 攻擊力超高
                "bullet_speed": 35,
                "spread": 0,
                "bullets_per_shot": 1,
                "has_crosshair": True,  # 有準心
            },
        }

        # 狀態效果管理
        self.status_effects = []

        # 輸入狀態追蹤
        self.keys_pressed = {
            "left": False,
            "right": False,
            "jump": False,
            "shoot": False,
            "melee": False,
        }

        # 射擊請求佇列
        self.pending_bullet = None

    def handle_input(self, keys, mouse_buttons, camera_x=0, camera_y=0):
        """
        處理玩家輸入 - 將鍵盤滑鼠輸入轉換為動作\n
        \n
        參數:\n
        keys (dict): pygame.key.get_pressed() 的結果\n
        mouse_buttons (tuple): pygame.mouse.get_pressed() 的結果\n
        camera_x (int): 攝影機 x 偏移，用於射擊方向計算\n
        camera_y (int): 攝影機 y 偏移，用於射擊方向計算\n
        \n
        處理的輸入:\n
        - 移動按鍵：更新 keys_pressed 狀態\n
        - 跳躍按鍵：立即觸發跳躍動作\n
        - 攻擊按鍵：觸發射擊或近戰\n
        - 子彈切換：改變當前子彈類型\n
        """
        # 記錄水平移動按鍵狀態
        self.keys_pressed["left"] = keys[pygame.K_a] or keys[pygame.K_LEFT]
        self.keys_pressed["right"] = keys[pygame.K_d] or keys[pygame.K_RIGHT]

        # 跳躍輸入（W 鍵或空白鍵）
        jump_input = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]
        if jump_input and not self.keys_pressed["jump"]:
            # 按鍵從沒按下變成按下，觸發跳躍
            self.jump()
        self.keys_pressed["jump"] = jump_input

        # 射擊輸入（滑鼠左鍵）- 支援連續射擊，現在傳遞攝影機偏移
        if mouse_buttons[0]:  # 按住滑鼠左鍵連續射擊
            bullet_info = self.shoot(camera_x, camera_y)
            if bullet_info:
                self.pending_bullet = bullet_info
        self.keys_pressed["shoot"] = mouse_buttons[0]

        # 近戰攻擊（滑鼠右鍵）
        if mouse_buttons[2] and not self.keys_pressed["melee"]:
            self.melee_attack()
        self.keys_pressed["melee"] = mouse_buttons[2]

        # 武器切換
        if keys[pygame.K_1]:
            self.current_weapon = "machine_gun"
        elif keys[pygame.K_2]:
            self.current_weapon = "assault_rifle"
        elif keys[pygame.K_3]:
            self.current_weapon = "shotgun"
        elif keys[pygame.K_4]:
            self.current_weapon = "sniper"

    def jump(self):
        """
        跳躍動作 - 包含一般跳躍、二段跳和爬牆跳\n
        \n
        跳躍邏輯：\n
        1. 在地面上：正常跳躍\n
        2. 在空中且有二段跳：二段跳躍\n
        3. 在牆邊滑行：爬牆跳躍（向反方向推開）\n
        \n
        每種跳躍有不同的力道和水平推力。\n
        """
        if self.on_ground:
            # 一般跳躍：在地面上時的跳躍
            self.velocity_y = PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.can_double_jump = True  # 跳躍後重新獲得二段跳能力

        elif self.can_double_jump:
            # 二段跳：在空中時的額外跳躍
            self.velocity_y = DOUBLE_JUMP_STRENGTH
            self.can_double_jump = False  # 用完二段跳

        elif self.is_wall_sliding:
            # 爬牆跳：從牆面推開並向上跳躍
            self.velocity_y = WALL_JUMP_STRENGTH
            self.velocity_x = -self.wall_direction * WALL_JUMP_PUSH  # 向相反方向推開
            self.is_wall_sliding = False
            self.can_double_jump = True  # 爬牆跳後重新獲得二段跳

    def shoot(self, camera_x=0, camera_y=0):
        """
        射擊動作 - 根據當前武器類型發射子彈\n
        \n
        支援四種武器：\n
        1. 機關槍：發射率超級快，攻擊力低，有 ±10 度隨機誤差\n
        2. 衝鋒槍：攻擊力高，發射率低，有 ±10 度隨機誤差\n
        3. 散彈槍：一次射出多發，60度散射，每發有 ±10 度隨機誤差\n
        4. 狙擊槍：攻擊力超高，有準心顯示，完全準確無誤差\n
        \n
        精度系統：\n
        - 狙擊槍：準心完全對準滑鼠位置，無任何隨機誤差\n
        - 其他武器：在瞄準方向基礎上添加 ±10 度的隨機誤差\n
        - 散彈槍：除了本身的散射外，每發子彈還有額外的隨機誤差\n
        \n
        參數:\n
        camera_x (int): 攝影機 x 偏移，用於正確計算滑鼠世界座標\n
        camera_y (int): 攝影機 y 偏移，用於正確計算滑鼠世界座標\n
        \n
        回傳:\n
        list or None: 成功射擊回傳子彈列表，冷卻中回傳 None\n
        """
        current_time = time.time()
        weapon_config = self.weapon_configs[self.current_weapon]

        # 檢查射擊冷卻時間
        if current_time - self.last_shot_time < weapon_config["fire_rate"]:
            return None  # 還在冷卻中，無法射擊

        # 獲取滑鼠位置來決定射擊方向
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # 將滑鼠的螢幕座標轉換為世界座標
        world_mouse_x = mouse_x + camera_x
        world_mouse_y = mouse_y + camera_y

        # 計算從玩家中心到滑鼠世界位置的方向向量
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2

        direction_x = world_mouse_x - player_center_x
        direction_y = world_mouse_y - player_center_y

        # 正規化方向向量（讓長度變成1）
        distance = math.sqrt(direction_x**2 + direction_y**2)
        if distance > 0:
            direction_x /= distance
            direction_y /= distance
        else:
            # 如果滑鼠就在玩家身上，預設向右射擊
            direction_x = self.facing_direction
            direction_y = 0

        # 更新面向方向
        if direction_x > 0:
            self.facing_direction = 1
        elif direction_x < 0:
            self.facing_direction = -1

        # 根據武器類型創建子彈
        bullets = []
        bullets_per_shot = weapon_config["bullets_per_shot"]
        spread = weapon_config.get("spread", 0)

        for i in range(bullets_per_shot):
            # 計算散射角度
            if bullets_per_shot > 1:
                # 散彈槍：在-30到+30度之間均勻分佈
                angle_offset = (i / (bullets_per_shot - 1) - 0.5) * spread
            else:
                angle_offset = 0

            # 計算最終射擊方向
            base_angle = math.atan2(direction_y, direction_x)

            # 根據武器類型添加隨機誤差
            if self.current_weapon == "sniper":
                # 狙擊槍：完全準確，不添加任何誤差
                final_angle = base_angle + angle_offset
            else:
                # 其他武器：添加 ±10 度的隨機誤差
                random_error = random.uniform(-10, 10) * (math.pi / 180)  # 轉換為弧度
                final_angle = base_angle + angle_offset + random_error

            final_direction_x = math.cos(final_angle)
            final_direction_y = math.sin(final_angle)

            bullet_info = {
                "type": self.current_weapon,
                "start_x": player_center_x,
                "start_y": player_center_y,
                "direction_x": final_direction_x,
                "direction_y": final_direction_y,
                "damage": weapon_config["damage"],
                "speed": weapon_config["bullet_speed"],
            }
            bullets.append(bullet_info)

        self.last_shot_time = current_time
        return bullets

    def melee_attack(self):
        """
        近戰攻擊 - 用槍身進行近距離揮擊\n
        \n
        近戰攻擊特點：\n
        1. 攻擊力比子彈高\n
        2. 有擊退效果\n
        3. 攻擊範圍有限\n
        4. 冷卻時間較短\n
        \n
        回傳:\n
        dict or None: 攻擊資訊或 None（冷卻中）\n
        """
        current_time = time.time()

        # 近戰攻擊的冷卻時間比射擊短
        melee_cooldown = 0.5  # 0.5秒冷卻

        if current_time - self.last_melee_time < melee_cooldown:
            return None  # 還在冷卻中

        self.last_melee_time = current_time

        # 計算近戰攻擊範圍（玩家前方的矩形區域）
        attack_x = self.x + (self.width if self.facing_direction > 0 else -MELEE_RANGE)
        attack_y = self.y
        attack_width = MELEE_RANGE
        attack_height = self.height

        return {
            "damage": MELEE_DAMAGE,
            "knockback": MELEE_KNOCKBACK,
            "attack_rect": pygame.Rect(attack_x, attack_y, attack_width, attack_height),
            "direction": self.facing_direction,
        }

    def update(self, platforms):
        """
        更新玩家狀態 - 每幀執行的更新邏輯\n
        \n
        參數:\n
        platforms (list): 所有平台物件的列表\n
        \n
        更新內容：\n
        1. 處理狀態效果\n
        2. 應用重力和移動\n
        3. 碰撞檢測和處理\n
        4. 邊界檢查\n
        5. 更新安全位置\n
        """
        # 更新狀態效果
        self.update_status_effects()

        # 計算移動速度修正（受狀態效果影響）
        speed_modifier = self.get_speed_modifier()

        # 處理水平移動
        if self.keys_pressed["left"] and not self.keys_pressed["right"]:
            self.velocity_x = -PLAYER_SPEED * speed_modifier
            self.facing_direction = -1
        elif self.keys_pressed["right"] and not self.keys_pressed["left"]:
            self.velocity_x = PLAYER_SPEED * speed_modifier
            self.facing_direction = 1
        else:
            # 沒有按移動鍵，應用摩擦力讓玩家逐漸停下
            self.velocity_x *= 0.8

        # 應用重力
        if not self.on_ground:
            self.velocity_y += GRAVITY
            # 限制最大下降速度
            if self.velocity_y > MAX_FALL_SPEED:
                self.velocity_y = MAX_FALL_SPEED

        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y

        # 處理碰撞
        self.handle_collisions(platforms)

        # 更新碰撞矩形
        self.update_rect()

        # 更新安全位置（如果玩家在地面上且位置合理）
        if self.on_ground and self.y < SCREEN_HEIGHT - 100:
            self.safe_position_timer += 1
            # 每60幀（1秒）更新一次安全位置
            if self.safe_position_timer >= 60:
                self.last_safe_x = self.x
                self.last_safe_y = self.y
                self.safe_position_timer = 0

        # 檢查是否掉出螢幕（需要重生）
        if self.y > SCREEN_HEIGHT + 200:
            self.respawn()

    def respawn(self):
        """
        重生玩家到上一個安全位置\n
        """
        self.x = self.last_safe_x
        self.y = self.last_safe_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.health = self.max_health  # 重生時恢復滿血
        self.is_alive = True
        print(f"🔄 玩家重生到位置: ({int(self.x)}, {int(self.y)})")

    def handle_collisions(self, platforms):
        """
        處理玩家與平台的碰撞 - 實現跑酷物理\n
        \n
        參數:\n
        platforms (list): 所有平台物件的列表\n
        \n
        碰撞處理：\n
        1. 垂直碰撞：站在平台上或撞到天花板\n
        2. 水平碰撞：撞到牆壁，進入滑牆狀態\n
        3. 邊界處理：不讓玩家跑出螢幕\n
        """
        # 重設碰撞狀態
        self.on_ground = False
        self.is_wall_sliding = False
        self.wall_direction = 0

        # 建立玩家的碰撞矩形
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                # 判斷碰撞方向

                # 計算重疊距離
                overlap_left = player_rect.right - platform.rect.left
                overlap_right = platform.rect.right - player_rect.left
                overlap_top = player_rect.bottom - platform.rect.top
                overlap_bottom = platform.rect.bottom - player_rect.top

                # 找出最小重疊距離，決定碰撞方向
                min_overlap = min(
                    overlap_left, overlap_right, overlap_top, overlap_bottom
                )

                if min_overlap == overlap_top and self.velocity_y > 0:
                    # 從上方撞到平台（落地）
                    self.y = platform.rect.top - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                    self.can_double_jump = True  # 落地後重新獲得二段跳

                elif min_overlap == overlap_bottom and self.velocity_y < 0:
                    # 從下方撞到平台（撞天花板）
                    self.y = platform.rect.bottom
                    self.velocity_y = 0

                elif min_overlap == overlap_left and self.velocity_x > 0:
                    # 從左側撞到平台（撞右牆）
                    self.x = platform.rect.left - self.width
                    if not self.on_ground and self.velocity_y > 0:
                        # 在空中撞到牆，進入滑牆狀態
                        self.is_wall_sliding = True
                        self.wall_direction = 1  # 右牆
                        self.velocity_y *= 0.7  # 減緩下降速度

                elif min_overlap == overlap_right and self.velocity_x < 0:
                    # 從右側撞到平台（撞左牆）
                    self.x = platform.rect.right
                    if not self.on_ground and self.velocity_y > 0:
                        # 在空中撞到牆，進入滑牆狀態
                        self.is_wall_sliding = True
                        self.wall_direction = -1  # 左牆
                        self.velocity_y *= 0.7  # 減緩下降速度

        # 螢幕邊界碰撞
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.velocity_x = 0

    def update_status_effects(self):
        """
        更新所有狀態效果 - 移除過期效果\n
        \n
        檢查每個狀態效果是否還在作用中，\n
        移除已經過期的效果。\n
        """
        # 使用列表推導式移除非活躍的狀態效果
        self.status_effects = [
            effect for effect in self.status_effects if effect.is_active()
        ]

    def get_speed_modifier(self):
        """
        計算當前的速度修正值 - 考慮所有狀態效果\n
        \n
        回傳:\n
        float: 速度修正倍率，1.0 = 正常速度\n
        """
        speed_modifier = 1.0

        for effect in self.status_effects:
            effect_modifier = effect.get_speed_modifier()
            # 取最低的速度修正值（最嚴重的減速效果）
            speed_modifier = min(speed_modifier, effect_modifier)

        return speed_modifier

    def add_status_effect(self, effect_type, duration, intensity):
        """
        加入新的狀態效果\n
        \n
        參數:\n
        effect_type (str): 效果類型 ('slow', 'paralysis')\n
        duration (float): 持續時間（秒）\n
        intensity (float): 效果強度 (0.0-1.0)\n
        """
        new_effect = StatusEffect(effect_type, duration, intensity)
        self.status_effects.append(new_effect)

    def take_damage(self, damage):
        """
        受到傷害 - 扣除生命值並檢查死亡\n
        \n
        參數:\n
        damage (int): 受到的傷害值\n
        \n
        回傳:\n
        bool: True 表示玩家死亡，False 表示還活著\n
        """
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            return True  # 玩家死亡
        return False  # 玩家還活著

    def get_pending_bullet(self):
        """
        取得待發射的子彈並清除

        回傳:
        list or None: 子彈資訊列表或 None
        """
        bullet_info = self.pending_bullet
        self.pending_bullet = None
        return bullet_info

    def heal(self, amount):
        """
        恢復生命值\n
        \n
        參數:\n
        amount (int): 恢復的生命值\n
        """
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製玩家角色 - 包含狀態指示\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        繪製內容：\n
        1. 玩家本體（矩形）\n
        2. 面向指示（小三角形）\n
        3. 狀態效果指示（顏色變化）\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 根據狀態效果改變顏色
        current_color = self.color

        # 如果有減速效果，變成紫色
        for effect in self.status_effects:
            if effect.effect_type == "slow":
                current_color = PURPLE
                break
            elif effect.effect_type == "paralysis":
                current_color = GRAY
                break

        # 繪製玩家主體（使用螢幕座標）
        player_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, current_color, player_rect)

        # 繪製面向指示（小三角形）
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2

        if self.facing_direction > 0:
            # 面向右邊的三角形
            triangle_points = [
                (center_x + 5, center_y),
                (center_x + 15, center_y - 5),
                (center_x + 15, center_y + 5),
            ]
        else:
            # 面向左邊的三角形
            triangle_points = [
                (center_x - 5, center_y),
                (center_x - 15, center_y - 5),
                (center_x - 15, center_y + 5),
            ]

        pygame.draw.polygon(screen, WHITE, triangle_points)

        # 移除滑牆白色邊框特效，保持簡潔外觀

    def draw_crosshair(self, screen, camera_x=0, camera_y=0):
        """
        繪製狙擊槍準心 - 顯示玩家準心位置\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        if self.current_weapon != "sniper":
            return

        # 獲取滑鼠位置
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # 繪製準心
        crosshair_size = 20
        crosshair_color = (255, 0, 0)  # 紅色準心

        # 水平線
        pygame.draw.line(
            screen,
            crosshair_color,
            (mouse_x - crosshair_size, mouse_y),
            (mouse_x + crosshair_size, mouse_y),
            2,
        )

        # 垂直線
        pygame.draw.line(
            screen,
            crosshair_color,
            (mouse_x, mouse_y - crosshair_size),
            (mouse_x, mouse_y + crosshair_size),
            2,
        )

        # 中心點
        pygame.draw.circle(screen, crosshair_color, (mouse_x, mouse_y), 3, 1)

    def draw_health_bar(self, screen):
        """
        繪製生命值條 - 顯示在螢幕上方\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        # 計算生命值比例
        health_ratio = self.health / self.max_health

        # 生命值條位置（螢幕左上角）
        bar_x = 10
        bar_y = 50

        # 繪製背景（紅色）
        bg_rect = pygame.Rect(bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        pygame.draw.rect(screen, HEALTH_BAR_BG_COLOR, bg_rect)

        # 繪製當前生命值（綠色）
        health_width = int(HEALTH_BAR_WIDTH * health_ratio)
        health_rect = pygame.Rect(bar_x, bar_y, health_width, HEALTH_BAR_HEIGHT)
        pygame.draw.rect(screen, HEALTH_BAR_COLOR, health_rect)

        # 繪製邊框
        pygame.draw.rect(screen, WHITE, bg_rect, 2)

        # 繪製生命值文字（調整位置避免重疊）
        font = get_chinese_font(FONT_SIZE_NORMAL)
        health_text = font.render(
            f"生命值: {self.health}/{self.max_health}", True, WHITE
        )
        screen.blit(health_text, (bar_x + 220, bar_y + 5))  # 向右移動避免重疊

    def draw_bullet_ui(self, screen):
        """
        繪製武器選擇介面 - 顯示當前武器和可切換的類型\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        weapons = ["machine_gun", "assault_rifle", "shotgun", "sniper"]
        weapon_colors = {
            "machine_gun": (255, 165, 0),  # 橘色
            "assault_rifle": (128, 0, 128),  # 紫色
            "shotgun": (255, 0, 0),  # 紅色
            "sniper": (0, 255, 255),  # 青色
        }
        weapon_names = {
            "machine_gun": "機關槍",
            "assault_rifle": "衝鋒槍",
            "shotgun": "散彈槍",
            "sniper": "狙擊槍",
        }

        start_x = SCREEN_WIDTH - 300
        start_y = BULLET_UI_Y

        for i, weapon in enumerate(weapons):
            # 計算位置
            ui_x = start_x + i * BULLET_UI_SPACING
            ui_y = start_y

            # 繪製武器圖示
            ui_rect = pygame.Rect(ui_x, ui_y, BULLET_UI_SIZE, BULLET_UI_SIZE)
            pygame.draw.rect(screen, weapon_colors[weapon], ui_rect)

            # 如果是當前選中的武器，畫更粗的白色邊框
            if weapon == self.current_weapon:
                pygame.draw.rect(screen, WHITE, ui_rect, 4)

            # 繪製按鍵提示
            font = get_chinese_font(FONT_SIZE_SMALL)
            key_text = font.render(str(i + 1), True, WHITE)
            text_rect = key_text.get_rect(
                center=(ui_x + BULLET_UI_SIZE // 2, ui_y + BULLET_UI_SIZE + 15)
            )
            screen.blit(key_text, text_rect)

            # 繪製武器名稱
            name_text = font.render(weapon_names[weapon], True, WHITE)
            name_rect = name_text.get_rect(
                center=(ui_x + BULLET_UI_SIZE // 2, ui_y + BULLET_UI_SIZE + 35)
            )
            screen.blit(name_text, name_rect)
