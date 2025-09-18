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
    3. 戰鬥系統（槍械射擊、甩槍攻擊）\n
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
    - 滑鼠右鍵: 甩槍攻擊\n
    - 1/2/3/4: 切換子彈類型\n
    """

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_COLOR)

        # 移動相關屬性
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.remaining_jumps = 2  # 剩餘空中跳躍次數（二段跳和三段跳）
        self.is_wall_sliding = False  # 是否在滑牆
        self.wall_direction = 0  # 接觸的牆壁方向 (-1: 左牆, 1: 右牆, 0: 無牆)

        # 生命值系統
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.is_alive = True

        # 玩家圖片相關
        self.player_right_image = None  # 向右看的圖片
        self.player_left_image = None  # 向左看的圖片
        self.load_player_images()  # 載入圖片

        self.death_time = 0  # 死亡時間記錄
        self.is_dead = False  # 是否已經死亡（區別於 is_alive）

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
                "damage": 8,  # 攻擊力降低從15到8
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
                "fire_rate": 1,  # 發射率低
                "damage": 90,  # 攻擊力降低10%（100->90）
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
            "ultimate": False,  # 新增必殺技按鍵狀態追蹤
        }

        # 武器切換鍵的前一幀狀態追蹤
        self.prev_key_1 = False
        self.prev_key_2 = False
        self.prev_key_3 = False
        self.prev_key_4 = False

        # 射擊請求佇列
        self.pending_bullet = None

        # 狙擊槍準心圖片載入
        self.crosshair_image = None
        self.load_crosshair_image()

        # 機關槍圖片載入
        self.machine_gun_image = None
        self.machine_gun_reverse_image = None
        self.load_machine_gun_image()

        # 狙擊槍圖片載入
        self.sniper_rifle_image = None
        self.sniper_rifle_reverse_image = None
        self.load_sniper_rifle_image()

        # 散彈槍圖片載入
        self.shotgun_image = None
        self.shotgun_reverse_image = None
        self.shotgun_left_image = None  # 專門用於往左射擊的圖片（180度旋轉）
        self.load_shotgun_image()

        # 衝鋒槍圖片載入
        self.assault_rifle_image = None
        self.assault_rifle_reverse_image = None
        self.load_assault_rifle_image()

        # 必殺技系統
        self.last_ultimate_time = 0  # 上次使用必殺技的時間
        self.ultimate_cooldown = 20.0  # 必殺技冷卻時間：20秒
        self.pending_ultimate = None  # 待發射的必殺技

        # 甩槍動畫系統
        self.is_melee_attacking = False  # 是否正在進行甩槍攻擊
        self.melee_animation_time = 0  # 甩槍動畫時間
        self.melee_animation_duration = 1.2  # 甩槍動畫持續時間（1.2秒）
        self.weapon_swing_angle = 0  # 武器甩動角度

        # 飛槍動畫系統 - 武器飛離玩家轉圈再回來
        self.weapon_flying = False  # 武器是否在飛行中
        self.weapon_fly_distance = 0  # 武器飛離玩家的距離
        self.weapon_spin_angle = 0  # 武器旋轉角度
        self.weapon_max_fly_distance = 120  # 武器最遠飛行距離

        # 回血系統
        self.heal_cooldown = 20.0  # 每20秒回血一次
        self.last_heal_time = time.time()  # 上次回血時間
        self.heal_amount = 10  # 每次回血量

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
        - 攻擊按鍵：觸發射擊或甩槍攻擊\n
        - 子彈切換：改變當前子彈類型\n
        """
        # 記錄水平移動按鍵狀態
        self.keys_pressed["left"] = keys[pygame.K_a] or keys[pygame.K_LEFT]
        self.keys_pressed["right"] = keys[pygame.K_d] or keys[pygame.K_RIGHT]

        # 跳躍輸入（W 鍵或空白鍵）- 修正按鍵檢測邏輯
        jump_input = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]
        if jump_input and not self.keys_pressed["jump"]:
            # 按鍵從沒按下變成按下，觸發跳躍
            self.jump()
        self.keys_pressed["jump"] = jump_input

        # 射擊輸入（滑鼠左鍵）- 支援連續射擊，現在傳遞攝影機偏移
        shoot_input = mouse_buttons[0]  # 滑鼠左鍵狀態
        if shoot_input:  # 按住滑鼠左鍵連續射擊
            bullet_info = self.shoot(camera_x, camera_y)
            if bullet_info:
                self.pending_bullet = bullet_info
        self.keys_pressed["shoot"] = shoot_input

        # 甩槍攻擊（滑鼠右鍵）- 修正按鍵檢測邏輯
        melee_input = mouse_buttons[2]  # 滑鼠右鍵狀態
        if melee_input and not self.keys_pressed["melee"]:
            # 按鍵從沒按下變成按下，觸發甩槍攻擊
            self.melee_attack()
        self.keys_pressed["melee"] = melee_input

        # 武器切換 - 修正按鍵檢測，避免重複觸發
        if keys[pygame.K_1] and not getattr(self, "prev_key_1", False):
            self.current_weapon = "machine_gun"
        elif keys[pygame.K_2] and not getattr(self, "prev_key_2", False):
            self.current_weapon = "assault_rifle"
        elif keys[pygame.K_3] and not getattr(self, "prev_key_3", False):
            self.current_weapon = "shotgun"
        elif keys[pygame.K_4] and not getattr(self, "prev_key_4", False):
            self.current_weapon = "sniper"

        # 記錄武器切換鍵的前一幀狀態
        self.prev_key_1 = keys[pygame.K_1]
        self.prev_key_2 = keys[pygame.K_2]
        self.prev_key_3 = keys[pygame.K_3]
        self.prev_key_4 = keys[pygame.K_4]

        # 必殺技（X鍵）- 修正按鍵檢測邏輯
        ultimate_input = keys[pygame.K_x]
        if ultimate_input and not self.keys_pressed["ultimate"]:
            # 按鍵從沒按下變成按下，觸發必殺技
            ultimate_info = self.use_ultimate()
            if ultimate_info:
                self.pending_ultimate = ultimate_info
        self.keys_pressed["ultimate"] = ultimate_input

    def jump(self):
        """
        跳躍動作 - 包含一般跳躍、二段跳、三段跳和爬牆跳\n
        \n
        跳躍邏輯：\n
        1. 在地面上：正常跳躍\n
        2. 在空中且還有剩餘跳躍次數：二段跳或三段跳\n
        3. 在牆邊滑行：爬牆跳躍（向反方向推開）\n
        \n
        每種跳躍都有相同的高度，確保三段跳每次跳躍力道一致。\n
        """
        if self.on_ground:
            # 一般跳躍：在地面上時的跳躍
            self.velocity_y = PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.remaining_jumps = 2  # 跳躍後重新獲得2次空中跳躍能力（二段跳和三段跳）

        elif self.remaining_jumps > 0:
            # 空中跳躍：二段跳或三段跳，使用相同的跳躍力道
            self.velocity_y = PLAYER_JUMP_STRENGTH  # 與一般跳躍相同的高度
            self.remaining_jumps -= 1  # 減少一次空中跳躍次數

        elif self.is_wall_sliding:
            # 爬牆跳：從牆面推開並向上跳躍
            self.velocity_y = WALL_JUMP_STRENGTH
            self.velocity_x = -self.wall_direction * WALL_JUMP_PUSH  # 向相反方向推開
            self.is_wall_sliding = False
            self.remaining_jumps = 2  # 爬牆跳後重新獲得2次空中跳躍能力

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

            # 計算子彈發射位置 - 機關槍、散彈槍和狙擊槍從槍口發射，其他武器從玩家中心發射
            if self.current_weapon == "machine_gun":
                # 機關槍：計算槍口位置作為發射點
                gun_muzzle_x, gun_muzzle_y = self.get_gun_muzzle_position(
                    camera_x, camera_y
                )
                bullet_start_x = gun_muzzle_x
                bullet_start_y = gun_muzzle_y
            elif self.current_weapon == "shotgun":
                # 散彈槍：計算槍口位置作為發射點
                shotgun_muzzle_x, shotgun_muzzle_y = self.get_shotgun_muzzle_position(
                    camera_x, camera_y
                )
                bullet_start_x = shotgun_muzzle_x
                bullet_start_y = shotgun_muzzle_y
            elif self.current_weapon == "sniper":
                # 狙擊槍：計算槍口位置作為發射點
                sniper_muzzle_x, sniper_muzzle_y = (
                    self.get_sniper_rifle_muzzle_position(camera_x, camera_y)
                )
                bullet_start_x = sniper_muzzle_x
                bullet_start_y = sniper_muzzle_y
            else:
                # 其他武器：從玩家中心發射
                bullet_start_x = player_center_x
                bullet_start_y = player_center_y

            bullet_info = {
                "type": self.current_weapon,
                "start_x": bullet_start_x,
                "start_y": bullet_start_y,
                "direction_x": final_direction_x,
                "direction_y": final_direction_y,
                "damage": weapon_config["damage"],
                "speed": weapon_config["bullet_speed"],
            }
            bullets.append(bullet_info)

        self.last_shot_time = current_time
        return bullets

    def get_gun_muzzle_position(self, camera_x=0, camera_y=0):
        """
        計算機關槍槍口位置 - 根據玩家面向方向和瞄準角度\n
        \n
        參數:\n
        camera_x (int): 攝影機 x 偏移，用於正確計算滑鼠世界座標\n
        camera_y (int): 攝影機 y 偏移，用於正確計算滑鼠世界座標\n
        \n
        回傳:\n
        tuple: (槍口x座標, 槍口y座標)\n
        """
        # 獲取滑鼠位置來決定槍的角度
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + camera_x
        world_mouse_y = mouse_y + camera_y

        # 計算玩家中心位置
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2

        # 計算瞄準角度
        direction_x = world_mouse_x - player_center_x
        direction_y = world_mouse_y - player_center_y

        # 正規化方向向量
        distance = math.sqrt(direction_x**2 + direction_y**2)
        if distance > 0:
            direction_x /= distance
            direction_y /= distance
        else:
            direction_x = self.facing_direction
            direction_y = 0

        # 計算射擊角度，判斷使用哪種圖片的槍口偏移
        angle = math.atan2(direction_y, direction_x)
        angle_degrees = math.degrees(angle)

        # 根據角度選擇槍口偏移參數（判斷是否為反向射擊）
        if angle_degrees > 90 or angle_degrees < -90:
            # 往後射擊，使用反向圖片的槍口偏移
            muzzle_offset_x = MACHINE_GUN_REVERSE_MUZZLE_OFFSET_X
            muzzle_offset_y = MACHINE_GUN_REVERSE_MUZZLE_OFFSET_Y
        else:
            # 往前射擊，使用正向圖片的槍口偏移
            muzzle_offset_x = MACHINE_GUN_MUZZLE_OFFSET_X
            muzzle_offset_y = MACHINE_GUN_MUZZLE_OFFSET_Y

        # 根據槍的旋轉角度計算槍口位置偏移
        cos_angle = direction_x
        sin_angle = direction_y

        # 根據槍的旋轉角度調整槍口位置
        rotated_offset_x = muzzle_offset_x * cos_angle - muzzle_offset_y * sin_angle
        rotated_offset_y = muzzle_offset_x * sin_angle + muzzle_offset_y * cos_angle

        # 計算最終槍口位置
        muzzle_x = player_center_x + rotated_offset_x
        muzzle_y = player_center_y + rotated_offset_y

        return muzzle_x, muzzle_y

    def get_sniper_rifle_muzzle_position(self, camera_x=0, camera_y=0):
        """
        計算狙擊槍槍口位置 - 根據玩家面向方向和瞄準角度\n
        \n
        參數:\n
        camera_x (int): 攝影機 x 偏移，用於正確計算滑鼠世界座標\n
        camera_y (int): 攝影機 y 偏移，用於正確計算滑鼠世界座標\n
        \n
        回傳:\n
        tuple: (槍口x座標, 槍口y座標)\n
        """
        # 獲取滑鼠位置來決定槍的角度
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + camera_x
        world_mouse_y = mouse_y + camera_y

        # 計算玩家中心位置
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2

        # 計算瞄準角度
        direction_x = world_mouse_x - player_center_x
        direction_y = world_mouse_y - player_center_y

        # 正規化方向向量
        distance = math.sqrt(direction_x**2 + direction_y**2)
        if distance > 0:
            direction_x /= distance
            direction_y /= distance
        else:
            direction_x = self.facing_direction
            direction_y = 0

        # 計算射擊角度，判斷使用哪種圖片的槍口偏移
        angle = math.atan2(direction_y, direction_x)
        angle_degrees = math.degrees(angle)

        # 根據角度選擇槍口偏移參數（判斷是否為反向射擊）
        if angle_degrees > 90 or angle_degrees < -90:
            # 往後射擊，使用反向圖片的槍口偏移
            muzzle_offset_x = SNIPER_RIFLE_REVERSE_MUZZLE_OFFSET_X
            muzzle_offset_y = SNIPER_RIFLE_REVERSE_MUZZLE_OFFSET_Y
        else:
            # 往前射擊，使用正向圖片的槍口偏移
            muzzle_offset_x = SNIPER_RIFLE_MUZZLE_OFFSET_X
            muzzle_offset_y = SNIPER_RIFLE_MUZZLE_OFFSET_Y

        # 根據槍的旋轉角度計算槍口位置偏移
        cos_angle = direction_x
        sin_angle = direction_y

        # 根據槍的旋轉角度調整槍口位置
        rotated_offset_x = muzzle_offset_x * cos_angle - muzzle_offset_y * sin_angle
        rotated_offset_y = muzzle_offset_x * sin_angle + muzzle_offset_y * cos_angle

        # 計算最終槍口位置
        muzzle_x = player_center_x + rotated_offset_x
        muzzle_y = player_center_y + rotated_offset_y

        return muzzle_x, muzzle_y

    def get_shotgun_muzzle_position(self, camera_x=0, camera_y=0):
        """
        計算散彈槍槍口位置 - 根據玩家面向方向和瞄準角度\n
        \n
        參數:\n
        camera_x (int): 攝影機 x 偏移，用於正確計算滑鼠世界座標\n
        camera_y (int): 攝影機 y 偏移，用於正確計算滑鼠世界座標\n
        \n
        回傳:\n
        tuple: (槍口x座標, 槍口y座標)\n
        \n
        槍口位置計算:\n
        - 正向射擊：使用 SHOTGUN_MUZZLE_OFFSET_X/Y\n
        - 反向射擊：使用 SHOTGUN_REVERSE_MUZZLE_OFFSET_X/Y\n
        - 支援圖片旋轉和鏡像後的精確槍口定位\n
        """
        # 獲取滑鼠位置來決定槍的角度
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + camera_x
        world_mouse_y = mouse_y + camera_y

        # 計算玩家中心位置
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2

        # 計算瞄準角度
        direction_x = world_mouse_x - player_center_x
        direction_y = world_mouse_y - player_center_y

        # 正規化方向向量
        distance = math.sqrt(direction_x**2 + direction_y**2)
        if distance > 0:
            direction_x /= distance
            direction_y /= distance
        else:
            direction_x = self.facing_direction
            direction_y = 0

        # 計算射擊角度，判斷使用哪種圖片的槍口偏移
        angle = math.atan2(direction_y, direction_x)
        angle_degrees = math.degrees(angle)

        # 根據角度選擇槍口偏移參數（判斷是否為反向射擊）
        if angle_degrees > 90 or angle_degrees < -90:
            # 往後射擊，使用反向圖片的槍口偏移（鏡像後的位置）
            muzzle_offset_x = SHOTGUN_REVERSE_MUZZLE_OFFSET_X
            muzzle_offset_y = SHOTGUN_REVERSE_MUZZLE_OFFSET_Y
        else:
            # 往前射擊，使用正向圖片的槍口偏移
            muzzle_offset_x = SHOTGUN_MUZZLE_OFFSET_X
            muzzle_offset_y = SHOTGUN_MUZZLE_OFFSET_Y

        # 根據槍的旋轉角度計算槍口位置偏移
        cos_angle = direction_x
        sin_angle = direction_y

        # 根據槍的旋轉角度調整槍口位置
        rotated_offset_x = muzzle_offset_x * cos_angle - muzzle_offset_y * sin_angle
        rotated_offset_y = muzzle_offset_x * sin_angle + muzzle_offset_y * cos_angle

        # 計算最終槍口位置
        muzzle_x = player_center_x + rotated_offset_x
        muzzle_y = player_center_y + rotated_offset_y

        return muzzle_x, muzzle_y

    def melee_attack(self):
        """
        甩槍攻擊 - 用槍械進行高威力的近距離攻擊\n
        \n
        甩槍攻擊特點：\n
        1. 攻擊力比對應武器的射擊傷害高2-3.5倍\n
        2. 有強力的擊退效果（根據武器類型調整）\n
        3. 攻擊範圍根據武器類型調整\n
        4. 冷卻時間根據武器威力調整\n
        \n
        各武器甩槍特性：\n
        - 機關槍：傷害25，擊退100，範圍70，冷卻0.8秒\n
        - 衝鋒槍：傷害120，擊退180，範圍85，冷卻1.2秒\n
        - 散彈槍：傷害90，擊退220，範圍95，冷卻1.5秒\n
        - 狙擊槍：傷害200，擊退250，範圍100，冷卻2.0秒\n
        \n
        攻擊機制：\n
        - 使用當前裝備的武器進行甩擊\n
        - 攻擊範圍為玩家前方的矩形區域\n
        - 造成高傷害並擊退敵人\n
        - 適合近距離戰鬥和突破敵人包圍\n
        \n
        回傳:\n
        dict or None: 甩槍攻擊資訊或 None（冷卻中）\n
        """
        current_time = time.time()

        # 獲取當前武器的甩槍攻擊配置
        swing_config = WEAPON_SWING_CONFIGS.get(self.current_weapon)
        if not swing_config:
            # 如果沒有找到配置，使用預設值
            swing_config = {
                "damage": 120,
                "knockback": 150,
                "range": 80,
                "cooldown": 1.0,
            }

        # 移除冷卻時間限制，讓玩家可以連續使用甩槍攻擊
        # 檢查甩槍攻擊的冷卻時間
        # if current_time - self.last_melee_time < swing_config["cooldown"]:
        #     return None  # 還在冷卻中

        self.last_melee_time = current_time

        # 啟動甩槍動畫
        self.is_melee_attacking = True
        self.melee_animation_time = 0
        self.weapon_swing_angle = 0

        # 初始化飛槍動畫
        self.weapon_flying = True
        self.weapon_fly_distance = 0
        self.weapon_spin_angle = 0

        # 計算甩槍攻擊範圍（玩家前方的矩形區域）
        attack_range = swing_config["range"]
        attack_x = self.x + (self.width if self.facing_direction > 0 else -attack_range)
        attack_y = self.y
        attack_width = attack_range
        attack_height = self.height

        return {
            "success": True,  # 攻擊成功標記
            "damage": swing_config["damage"],
            "knockback": swing_config["knockback"],
            "range": swing_config["range"],  # 新增：攻擊範圍
            "attack_rect": pygame.Rect(attack_x, attack_y, attack_width, attack_height),
            "direction": self.facing_direction,
            "attack_type": "gun_swing",  # 攻擊類型標記
            "weapon_type": self.current_weapon,  # 新增：記錄使用的武器類型
            "weapon_name": {  # 新增：武器名稱對照
                "machine_gun": "機關槍",
                "assault_rifle": "突擊步槍",
                "shotgun": "散彈槍",
                "sniper": "狙擊槍",
            }.get(self.current_weapon, "未知武器"),
        }

    def use_ultimate(self):
        """
        使用必殺技 - 雷電追蹤攻擊\n
        \n
        必殺技特點：\n
        1. 發射五顆自動追蹤子彈\n
        2. 傷害與狙擊槍相同（100%）\n
        3. 冷卻時間 20 秒\n
        \n
        回傳:\n
        list or None: 五顆必殺技子彈資訊列表或 None（冷卻中）\n
        """
        current_time = time.time()

        # 檢查冷卻時間
        if current_time - self.last_ultimate_time < self.ultimate_cooldown:
            return None  # 還在冷卻中

        self.last_ultimate_time = current_time

        # 必殺技傷害與狙擊槍相同（100%）
        sniper_damage = self.weapon_configs["sniper"]["damage"]
        ultimate_damage = sniper_damage  # 100%

        # 創建五顆追蹤子彈
        ultimate_bullets = []
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2

        for i in range(5):
            # 每顆子彈有稍微不同的初始方向，避免重疊
            angle_offset = (i - 2) * 0.2  # -0.4 到 +0.4 弧度的偏移

            bullet_info = {
                "type": "lightning_tracking",
                "start_x": player_center_x,
                "start_y": player_center_y,
                "damage": ultimate_damage,
                "speed": 20,  # 提升速度讓子彈更快到達目標
                "angle_offset": angle_offset,  # 初始角度偏移
                "bullet_id": i,  # 子彈編號，用於區分
            }
            ultimate_bullets.append(bullet_info)

        return ultimate_bullets

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
        6. 自動回血\n
        \n
        回傳:\n
        dict or None: 如果玩家死亡則返回死亡狀態，否則返回 None\n
        """
        # 檢查玩家是否已經死亡，如果是則返回遊戲結束狀態
        if not self.is_alive:
            return {"died": True, "game_over": True}
        # 更新狀態效果
        self.update_status_effects()

        # 自動回血 (已關閉)
        # self.auto_heal()

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

        # 更新甩槍動畫
        self.update_melee_animation()

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

        # 檢查是否掉出螢幕（視為死亡）
        if self.y > SCREEN_HEIGHT + 200:
            # 掉出螢幕視為死亡，直接遊戲結束
            damage_result = self.take_damage(self.health)  # 造成致命傷害
            return damage_result  # 回傳遊戲結束資訊

        # 正常情況下返回 None
        return None

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
                    self.remaining_jumps = 2  # 落地後重新獲得2次空中跳躍能力

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

        # 螢幕邊界碰撞 - 移除右邊界限制，允許無限向右移動
        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        # 移除右邊界檢查，允許玩家在無限寬度地圖中移動

    def update_melee_animation(self):
        """
        更新甩槍攻擊動畫 - 武器飛離玩家、轉圈、然後回來\n
        \n
        動畫分為三個階段：\n
        1. 飛出階段（0-0.4秒）：武器飛離玩家，同時旋轉\n
        2. 停留階段（0.4-0.8秒）：武器在最遠處旋轉\n
        3. 回歸階段（0.8-1.2秒）：武器飛回玩家身邊\n
        \n
        飛槍動畫原理：\n
        1. 使用時間分段控制飛行軌跡\n
        2. 武器持續旋轉營造動感\n
        3. 距離計算讓武器平滑飛出再飛回\n
        """
        if not self.is_melee_attacking:
            return

        # 更新動畫時間
        self.melee_animation_time += 1 / 60  # 假設60FPS

        # 計算動畫進度（0到1）
        progress = min(self.melee_animation_time / self.melee_animation_duration, 1.0)

        # 武器持續旋轉，營造飛行中的動感
        self.weapon_spin_angle += 12  # 每幀轉12度，很快的旋轉
        if self.weapon_spin_angle >= 360:
            self.weapon_spin_angle -= 360

        # 動畫分三個階段：飛出、停留、飛回
        if progress <= 0.33:  # 飛出階段（前1/3時間）
            # 武器從玩家身邊飛向最遠點
            fly_progress = progress / 0.33
            self.weapon_fly_distance = self.weapon_max_fly_distance * fly_progress

        elif progress <= 0.67:  # 停留階段（中間1/3時間）
            # 武器在最遠處停留，持續旋轉
            self.weapon_fly_distance = self.weapon_max_fly_distance

        else:  # 回歸階段（最後1/3時間）
            # 武器從最遠點飛回玩家身邊
            return_progress = (progress - 0.67) / 0.33
            self.weapon_fly_distance = self.weapon_max_fly_distance * (
                1 - return_progress
            )

        # 動畫結束檢查
        if progress >= 1.0:
            self.is_melee_attacking = False
            self.melee_animation_time = 0
            self.weapon_swing_angle = 0
            self.weapon_flying = False
            self.weapon_fly_distance = 0
            self.weapon_spin_angle = 0

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
        dict: 傷害結果資訊 {\n
            'health_lost': bool - 是否失去生命值\n
            'died': bool - 是否死亡（這一次受傷）\n
            'game_over': bool - 是否遊戲結束（沒有生命次數）\n
        }\n
        """
        self.health -= damage
        result = {"health_lost": True, "died": False, "game_over": False}

        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.is_dead = True
            self.death_time = time.time()
            result["died"] = True
            result["game_over"] = True  # 玩家死亡直接遊戲結束
            print("💀 玩家死亡！遊戲結束")

        return result

    def get_pending_bullet(self):
        """
        取得待發射的子彈並清除

        回傳:
        list or None: 子彈資訊列表或 None
        """
        bullet_info = self.pending_bullet
        self.pending_bullet = None
        return bullet_info

    def get_pending_ultimate(self):
        """
        取得待發射的必殺技並清除

        回傳:
        dict or None: 必殺技資訊或 None
        """
        ultimate_info = self.pending_ultimate
        self.pending_ultimate = None
        return ultimate_info

    def get_ultimate_cooldown_ratio(self):
        """
        取得必殺技冷卻比例

        回傳:
        float: 冷卻比例 (0.0-1.0)，1.0表示可以使用
        """
        current_time = time.time()
        elapsed = current_time - self.last_ultimate_time
        cooldown_ratio = min(1.0, elapsed / self.ultimate_cooldown)
        return cooldown_ratio

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

    def auto_heal(self):
        """
        自動回血機制 - 每20秒回復10點生命值\n
        """
        current_time = time.time()
        if current_time - self.last_heal_time >= self.heal_cooldown:
            if self.health < self.max_health and self.is_alive:
                old_health = self.health
                self.health = min(self.max_health, self.health + self.heal_amount)
                if self.health > old_health:
                    print(f"💚 玩家自動回血：{old_health} → {self.health}")

                self.last_heal_time = current_time

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
        1. 玩家本體（圖片或矩形）\n
        2. 狀態效果指示（顏色變化）\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 創建玩家矩形
        player_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)

        if self.facing_direction > 0 and self.player_right_image:
            # 使用向右的圖片
            screen.blit(self.player_right_image, player_rect)
        elif self.facing_direction < 0 and self.player_left_image:
            # 使用向左的圖片
            screen.blit(self.player_left_image, player_rect)
        else:
            # 如果圖片載入失敗，使用顏色矩形備用
            current_color = self.color

            # 根據狀態效果改變顏色
            for effect in self.status_effects:
                if effect.effect_type == "slow":
                    current_color = PURPLE
                    break
                elif effect.effect_type == "paralysis":
                    current_color = GRAY
                    break

            # 繪製玩家矩形
            pygame.draw.rect(screen, current_color, player_rect)

        # 繪製機關槍（當使用機關槍時）
        if self.current_weapon == "machine_gun":
            self.draw_machine_gun(screen, camera_x, camera_y)

        # 繪製衝鋒槍（當使用衝鋒槍時）
        if self.current_weapon == "assault_rifle":
            self.draw_assault_rifle(screen, camera_x, camera_y)

        # 繪製散彈槍（當使用散彈槍時）
        if self.current_weapon == "shotgun":
            self.draw_shotgun(screen, camera_x, camera_y)

        # 繪製狙擊槍（當使用狙擊槍時）
        if self.current_weapon == "sniper":
            self.draw_sniper_rifle(screen, camera_x, camera_y)

        # 移除滑牆白色邊框特效，保持簡潔外觀

    def load_player_images(self):
        """
        載入玩家角色圖片 - 包含面向左右的兩種狀態\n
        \n
        功能:\n
        1. 載入面向右方的圖片\n
        2. 載入面向左方的圖片\n
        3. 將圖片縮放到玩家尺寸\n
        4. 如果載入失敗，使用預設顏色矩形\n
        \n
        圖片處理:\n
        - 支援 PNG 格式的透明背景圖片\n
        - 自動縮放到 PLAYER_IMAGE_SIZE 尺寸\n
        - 保持圖片原始比例並居中\n
        """
        try:
            # 載入向右看的圖片
            self.player_right_image = pygame.image.load(
                PLAYER_RIGHT_IMAGE_PATH
            ).convert_alpha()
            self.player_right_image = pygame.transform.scale(
                self.player_right_image, PLAYER_IMAGE_SIZE
            )
            print(f"成功載入玩家向右圖片: {PLAYER_RIGHT_IMAGE_PATH}")

            # 載入向左看的圖片
            self.player_left_image = pygame.image.load(
                PLAYER_LEFT_IMAGE_PATH
            ).convert_alpha()
            self.player_left_image = pygame.transform.scale(
                self.player_left_image, PLAYER_IMAGE_SIZE
            )
            print(f"成功載入玩家向左圖片: {PLAYER_LEFT_IMAGE_PATH}")

        except (pygame.error, FileNotFoundError) as e:
            # 圖片載入失敗，將使用預設顏色矩形
            print(f"玩家圖片載入失敗: {e}")
            self.player_right_image = None
            self.player_left_image = None

    def load_crosshair_image(self):
        """
        載入狙擊槍準心圖片 - 處理圖片載入和縮放\n
        \n
        功能:\n
        1. 嘗試載入指定的準心圖片檔案\n
        2. 將圖片縮放到適當大小\n
        3. 如果載入失敗，使用預設的十字準心\n
        \n
        圖片處理:\n
        - 支援 PNG 格式的透明背景圖片\n
        - 自動縮放到 CROSSHAIR_SIZE 尺寸\n
        - 保持圖片原始比例並居中\n
        """
        try:
            # 載入準心圖片
            self.crosshair_image = pygame.image.load(
                CROSSHAIR_IMAGE_PATH
            ).convert_alpha()
            # 縮放到指定大小，保持比例
            self.crosshair_image = pygame.transform.scale(
                self.crosshair_image, (CROSSHAIR_SIZE, CROSSHAIR_SIZE)
            )
            print(f"成功載入狙擊槍準心圖片: {CROSSHAIR_IMAGE_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            # 圖片載入失敗，將使用預設十字準心
            print(f"準心圖片載入失敗: {e}")
            self.crosshair_image = None

    def load_sniper_rifle_image(self):
        """
        載入狙擊槍圖片 - 處理正向和反向圖片載入和縮放\n
        \n
        功能:\n
        1. 嘗試載入指定的狙擊槍正向圖片檔案（往右射擊）\n
        2. 嘗試載入指定的狙擊槍反向圖片檔案（往左射擊）\n
        3. 將圖片縮放到適當大小\n
        4. 如果載入失敗，使用預設的矩形顯示\n
        \n
        圖片處理:\n
        - 支援 PNG 格式的透明背景圖片\n
        - 自動縮放到 SNIPER_RIFLE_IMAGE_SIZE 尺寸\n
        - 槍口位置在圖片的槍管尖端\n
        """
        try:
            # 載入狙擊槍正向圖片（往右射擊）
            self.sniper_rifle_image = pygame.image.load(
                SNIPER_RIFLE_IMAGE_PATH
            ).convert_alpha()
            # 縮放到指定大小
            self.sniper_rifle_image = pygame.transform.scale(
                self.sniper_rifle_image, SNIPER_RIFLE_IMAGE_SIZE
            )
            print(f"成功載入狙擊槍正向圖片: {SNIPER_RIFLE_IMAGE_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            # 圖片載入失敗，將使用預設矩形顯示
            print(f"狙擊槍正向圖片載入失敗: {e}")
            self.sniper_rifle_image = None

        try:
            # 載入狙擊槍反向圖片（往左射擊）
            self.sniper_rifle_reverse_image = pygame.image.load(
                SNIPER_RIFLE_REVERSE_IMAGE_PATH
            ).convert_alpha()
            # 縮放到指定大小
            self.sniper_rifle_reverse_image = pygame.transform.scale(
                self.sniper_rifle_reverse_image, SNIPER_RIFLE_IMAGE_SIZE
            )
            print(f"成功載入狙擊槍反向圖片: {SNIPER_RIFLE_REVERSE_IMAGE_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            # 反向圖片載入失敗，將使用預設顯示
            print(f"狙擊槍反向圖片載入失敗: {e}")
            self.sniper_rifle_reverse_image = None

    def load_shotgun_image(self):
        """
        載入散彈槍圖片 - 處理正向圖片載入和反向鏡像生成\n
        \n
        功能:\n
        1. 嘗試載入指定的散彈槍正向圖片檔案（槍口朝右）\n
        2. 通過水平翻轉自動生成反向圖片（槍口朝左）\n
        3. 將圖片縮放到適當大小\n
        4. 如果載入失敗，使用預設的矩形顯示\n
        \n
        圖片處理:\n
        - 支援 PNG 格式的透明背景圖片\n
        - 自動縮放到 SHOTGUN_IMAGE_SIZE 尺寸\n
        - 原圖槍口朝右，鏡像後槍口朝左\n
        - 反向圖片通過 pygame.transform.flip 自動生成\n
        """
        try:
            # 載入散彈槍正向圖片（槍口朝右）
            self.shotgun_image = pygame.image.load(SHOTGUN_IMAGE_PATH).convert_alpha()
            # 縮放到指定大小
            self.shotgun_image = pygame.transform.scale(
                self.shotgun_image, SHOTGUN_IMAGE_SIZE
            )
            print(f"成功載入散彈槍正向圖片: {SHOTGUN_IMAGE_PATH}")

            # 通過水平翻轉生成反向圖片（槍口朝左）
            self.shotgun_reverse_image = pygame.transform.flip(
                self.shotgun_image, True, False
            )  # True=水平翻轉, False=不垂直翻轉

            # 為往左射擊生成 180 度旋轉的圖片（解決上下左右都顛倒的問題）
            self.shotgun_left_image = pygame.transform.flip(
                self.shotgun_image, True, True
            )  # True=水平翻轉, True=垂直翻轉（相當於 180 度旋轉）
            print("成功生成散彈槍反向圖片（鏡像）和左射圖片")

        except (pygame.error, FileNotFoundError) as e:
            # 圖片載入失敗，將使用預設矩形顯示
            print(f"散彈槍圖片載入失敗: {e}")
            self.shotgun_image = None
            self.shotgun_reverse_image = None
            self.shotgun_left_image = None

    def load_machine_gun_image(self):
        """
        載入機關槍圖片 - 處理正向和反向圖片載入和縮放\n
        \n
        功能:\n
        1. 嘗試載入指定的機關槍正向圖片檔案\n
        2. 嘗試載入指定的機關槍反向圖片檔案（往後射擊時使用）\n
        3. 將圖片縮放到適當大小\n
        4. 如果載入失敗，使用預設的矩形顯示\n
        \n
        圖片處理:\n
        - 支援 PNG 格式的透明背景圖片\n
        - 自動縮放到 MACHINE_GUN_IMAGE_SIZE 尺寸\n
        - 槍口位置在圖片的右上角下面一點\n
        """
        try:
            # 載入機關槍正向圖片
            self.machine_gun_image = pygame.image.load(
                MACHINE_GUN_IMAGE_PATH
            ).convert_alpha()
            # 縮放到指定大小
            self.machine_gun_image = pygame.transform.scale(
                self.machine_gun_image, MACHINE_GUN_IMAGE_SIZE
            )
            print(f"成功載入機關槍圖片: {MACHINE_GUN_IMAGE_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            # 圖片載入失敗，將使用預設矩形顯示
            print(f"機關槍圖片載入失敗: {e}")
            self.machine_gun_image = None

        try:
            # 載入機關槍反向圖片（往後射擊時使用）
            self.machine_gun_reverse_image = pygame.image.load(
                MACHINE_GUN_REVERSE_IMAGE_PATH
            ).convert_alpha()
            # 縮放到指定大小
            self.machine_gun_reverse_image = pygame.transform.scale(
                self.machine_gun_reverse_image, MACHINE_GUN_IMAGE_SIZE
            )
            print(f"成功載入機關槍反向圖片: {MACHINE_GUN_REVERSE_IMAGE_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            # 反向圖片載入失敗，將使用預設顯示
            print(f"機關槍反向圖片載入失敗: {e}")
            self.machine_gun_reverse_image = None

    def load_assault_rifle_image(self):
        """
        載入衝鋒槍圖片 - 處理正向和反向圖片載入和縮放\n
        \n
        功能:\n
        1. 嘗試載入指定的衝鋒槍正向圖片檔案（往右射擊）\n
        2. 嘗試載入指定的衝鋒槍反向圖片檔案（往左射擊）\n
        3. 將圖片縮放到適當大小\n
        4. 如果載入失敗，使用預設的矩形顯示\n
        \n
        圖片處理:\n
        - 支援 PNG 格式的透明背景圖片\n
        - 自動縮放到 ASSAULT_RIFLE_IMAGE_SIZE 尺寸\n
        """
        try:
            # 載入衝鋒槍正向圖片（往右射擊）
            self.assault_rifle_image = pygame.image.load(
                ASSAULT_RIFLE_IMAGE_PATH
            ).convert_alpha()
            # 縮放到指定大小
            self.assault_rifle_image = pygame.transform.scale(
                self.assault_rifle_image, ASSAULT_RIFLE_IMAGE_SIZE
            )
            print(f"成功載入衝鋒槍正向圖片: {ASSAULT_RIFLE_IMAGE_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            # 圖片載入失敗，將使用預設矩形顯示
            print(f"衝鋒槍正向圖片載入失敗: {e}")
            self.assault_rifle_image = None

        try:
            # 載入衝鋒槍反向圖片（往左射擊）
            self.assault_rifle_reverse_image = pygame.image.load(
                ASSAULT_RIFLE_REVERSE_IMAGE_PATH
            ).convert_alpha()
            # 縮放到指定大小
            self.assault_rifle_reverse_image = pygame.transform.scale(
                self.assault_rifle_reverse_image, ASSAULT_RIFLE_IMAGE_SIZE
            )
            print(f"成功載入衝鋒槍反向圖片: {ASSAULT_RIFLE_REVERSE_IMAGE_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            # 反向圖片載入失敗，將使用預設顯示
            print(f"衝鋒槍反向圖片載入失敗: {e}")
            self.assault_rifle_reverse_image = None

    def draw_machine_gun(self, screen, camera_x=0, camera_y=0):
        """
        繪製機關槍 - 根據瞄準方向旋轉機關槍圖片\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        繪製邏輯:\n
        1. 只有當使用機關槍且圖片載入成功時才繪製\n
        2. 計算瞄準角度並旋轉槍的圖片\n
        3. 槍的中心位置跟隨玩家\n
        4. 圖片載入失敗時繪製簡單的矩形代替\n
        """
        if self.machine_gun_image is not None:
            # 獲取滑鼠位置來決定槍的角度
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y

            # 計算玩家中心位置（世界座標）
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2

            # 計算瞄準角度
            direction_x = world_mouse_x - player_center_x
            direction_y = world_mouse_y - player_center_y

            # 如果在甩槍攻擊中，武器會飛離玩家
            if self.is_melee_attacking and self.weapon_flying:
                # 計算武器飛行後的位置
                fly_direction_x = math.cos(math.radians(self.weapon_spin_angle))
                fly_direction_y = math.sin(math.radians(self.weapon_spin_angle))

                # 武器飛到指定距離的位置
                weapon_x = player_center_x + fly_direction_x * self.weapon_fly_distance
                weapon_y = player_center_y + fly_direction_y * self.weapon_fly_distance

                # 使用旋轉角度作為武器的朝向
                angle_degrees = self.weapon_spin_angle + MACHINE_GUN_ROTATION_OFFSET
            else:
                # 正常情況下，武器在玩家身邊並朝向滑鼠
                weapon_x = player_center_x
                weapon_y = player_center_y

                # 計算角度（弧度轉角度）
                angle = math.atan2(direction_y, direction_x)
                angle_degrees = math.degrees(angle) + MACHINE_GUN_ROTATION_OFFSET

            # 根據角度選擇使用哪個圖片
            if angle_degrees > 90 or angle_degrees < -90:
                # 往後射擊時使用反向圖片（啊哈.png）
                if self.machine_gun_reverse_image is not None:
                    gun_image = self.machine_gun_reverse_image
                    # 調整角度使反向圖片正確朝向
                    angle_degrees = (
                        angle_degrees - 180
                        if angle_degrees > 0
                        else angle_degrees + 180
                    )
                else:
                    # 沒有反向圖片時，使用翻轉的正向圖片
                    gun_image = pygame.transform.flip(
                        self.machine_gun_image, False, True
                    )
                    angle_degrees = (
                        angle_degrees - 180
                        if angle_degrees > 0
                        else angle_degrees + 180
                    )
            else:
                # 往前射擊時使用正常圖片
                gun_image = self.machine_gun_image

            # 旋轉機關槍圖片
            rotated_gun = pygame.transform.rotate(gun_image, -angle_degrees)

            # 計算旋轉後圖片的新中心位置（螢幕座標）
            gun_rect = rotated_gun.get_rect()
            gun_rect.center = (weapon_x - camera_x, weapon_y - camera_y)

            # 繪製旋轉後的機關槍
            screen.blit(rotated_gun, gun_rect)
        else:
            # 圖片載入失敗，繪製簡單的槍械矩形代替
            # 計算槍的位置和角度
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y

            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2

            # 計算方向
            direction_x = world_mouse_x - player_center_x
            direction_y = world_mouse_y - player_center_y
            distance = math.sqrt(direction_x**2 + direction_y**2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance
            else:
                direction_x = self.facing_direction
                direction_y = 0

            # 繪製簡單的槍械線段（從玩家中心向滑鼠方向）
            gun_length = 30
            end_x = player_center_x - camera_x + direction_x * gun_length
            end_y = player_center_y - camera_y + direction_y * gun_length

            pygame.draw.line(
                screen,
                MACHINE_GUN_COLOR,
                (player_center_x - camera_x, player_center_y - camera_y),
                (int(end_x), int(end_y)),
                4,
            )

    def draw_sniper_rifle(self, screen, camera_x=0, camera_y=0):
        """
        繪製狙擊槍 - 根據瞄準方向旋轉狙擊槍圖片\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        繪製邏輯:\n
        1. 只有當使用狙擊槍且圖片載入成功時才繪製\n
        2. 計算瞄準角度並旋轉槍的圖片\n
        3. 槍的中心位置跟隨玩家\n
        4. 圖片載入失敗時繪製簡單的矩形代替\n
        """
        if self.sniper_rifle_image is not None:
            # 獲取滑鼠位置來決定槍的角度
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y

            # 計算玩家中心位置（世界座標）
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2

            # 計算瞄準角度
            direction_x = world_mouse_x - player_center_x
            direction_y = world_mouse_y - player_center_y

            # 如果在甩槍攻擊中，武器會飛離玩家
            if self.is_melee_attacking and self.weapon_flying:
                # 計算武器飛行後的位置
                fly_direction_x = math.cos(math.radians(self.weapon_spin_angle))
                fly_direction_y = math.sin(math.radians(self.weapon_spin_angle))

                # 武器飛到指定距離的位置
                weapon_x = player_center_x + fly_direction_x * self.weapon_fly_distance
                weapon_y = player_center_y + fly_direction_y * self.weapon_fly_distance

                # 使用旋轉角度作為武器的朝向
                angle_degrees = self.weapon_spin_angle + SNIPER_RIFLE_ROTATION_OFFSET
            else:
                # 正常情況下，武器在玩家身邊並朝向滑鼠
                weapon_x = player_center_x
                weapon_y = player_center_y

                # 計算角度（弧度轉角度）
                angle = math.atan2(direction_y, direction_x)
                angle_degrees = math.degrees(angle) + SNIPER_RIFLE_ROTATION_OFFSET

            # 根據角度選擇使用哪個圖片
            if angle_degrees > 90 or angle_degrees < -90:
                # 往後射擊時使用反向圖片（哈哈哈.png）
                if self.sniper_rifle_reverse_image is not None:
                    rifle_image = self.sniper_rifle_reverse_image
                    # 調整角度使反向圖片正確朝向
                    angle_degrees = (
                        angle_degrees - 180
                        if angle_degrees > 0
                        else angle_degrees + 180
                    )
                else:
                    # 沒有反向圖片時，使用翻轉的正向圖片
                    rifle_image = pygame.transform.flip(
                        self.sniper_rifle_image, False, True
                    )
                    angle_degrees = (
                        angle_degrees - 180
                        if angle_degrees > 0
                        else angle_degrees + 180
                    )
            else:
                # 往前射擊時使用正常圖片
                rifle_image = self.sniper_rifle_image

            # 旋轉狙擊槍圖片
            rotated_rifle = pygame.transform.rotate(rifle_image, -angle_degrees)

            # 計算旋轉後圖片的新中心位置（螢幕座標）
            rifle_rect = rotated_rifle.get_rect()
            rifle_rect.center = (weapon_x - camera_x, weapon_y - camera_y)

            # 繪製旋轉後的狙擊槍
            screen.blit(rotated_rifle, rifle_rect)
        else:
            # 圖片載入失敗，繪製簡單的槍械矩形代替
            # 計算槍的位置和角度
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y

            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2

            # 計算方向
            direction_x = world_mouse_x - player_center_x
            direction_y = world_mouse_y - player_center_y
            distance = math.sqrt(direction_x**2 + direction_y**2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance
            else:
                direction_x = self.facing_direction
                direction_y = 0

            # 繪製簡單的槍械線段（從玩家中心向滑鼠方向）
            rifle_length = 40  # 比機關槍稍長
            end_x = player_center_x - camera_x + direction_x * rifle_length
            end_y = player_center_y - camera_y + direction_y * rifle_length

            pygame.draw.line(
                screen,
                SNIPER_RIFLE_COLOR,
                (player_center_x - camera_x, player_center_y - camera_y),
                (int(end_x), int(end_y)),
                6,  # 比機關槍稍粗
            )

    def draw_shotgun(self, screen, camera_x=0, camera_y=0):
        """
        繪製散彈槍 - 根據瞄準方向旋轉散彈槍圖片，支援鏡像顯示\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        繪製邏輯:\n
        1. 只有當使用散彈槍且圖片載入成功時才繪製\n
        2. 計算瞄準角度並旋轉槍的圖片\n
        3. 根據瞄準方向自動選擇正向或鏡像圖片\n
        4. 槍的中心位置跟隨玩家\n
        5. 圖片載入失敗時繪製簡單的矩形代替\n
        """
        if self.shotgun_image is not None:
            # 獲取滑鼠位置來決定槍的角度
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y

            # 計算玩家中心位置（世界座標）
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2

            # 計算瞄準角度
            direction_x = world_mouse_x - player_center_x
            direction_y = world_mouse_y - player_center_y

            # 如果在甩槍攻擊中，武器會飛離玩家
            if self.is_melee_attacking and self.weapon_flying:
                # 計算武器飛行後的位置
                fly_direction_x = math.cos(math.radians(self.weapon_spin_angle))
                fly_direction_y = math.sin(math.radians(self.weapon_spin_angle))

                # 武器飛到指定距離的位置
                weapon_x = player_center_x + fly_direction_x * self.weapon_fly_distance
                weapon_y = player_center_y + fly_direction_y * self.weapon_fly_distance

                # 使用旋轉角度作為武器的朝向
                angle_degrees = self.weapon_spin_angle + SHOTGUN_ROTATION_OFFSET
            else:
                # 正常情況下，武器在玩家身邊並朝向滑鼠
                weapon_x = player_center_x
                weapon_y = player_center_y

                # 計算角度（弧度轉角度）
                angle = math.atan2(direction_y, direction_x)
                angle_degrees = math.degrees(angle) + SHOTGUN_ROTATION_OFFSET

            # 根據角度選擇使用哪個圖片
            # 往右射擊正常，所以原圖應該是槍口朝右的
            if angle_degrees > 90 or angle_degrees < -90:
                # 往左射擊時使用180度旋轉的圖片（修正上下左右都顛倒的問題）
                if self.shotgun_left_image is not None:
                    shotgun_image = self.shotgun_left_image
                else:
                    shotgun_image = self.shotgun_image
                adjusted_angle = angle_degrees
            else:
                # 往右射擊時使用鏡像圖片（因為往右是正常的，要保持這個狀態）
                if self.shotgun_reverse_image is not None:
                    shotgun_image = self.shotgun_reverse_image
                else:
                    shotgun_image = self.shotgun_image
                adjusted_angle = angle_degrees

            # 旋轉散彈槍圖片
            rotated_shotgun = pygame.transform.rotate(shotgun_image, -adjusted_angle)

            # 計算旋轉後圖片的新中心位置（螢幕座標）
            shotgun_rect = rotated_shotgun.get_rect()
            shotgun_rect.center = (
                weapon_x - camera_x,
                weapon_y - camera_y,
            )

            # 繪製旋轉後的散彈槍
            screen.blit(rotated_shotgun, shotgun_rect)
        else:
            # 圖片載入失敗，繪製簡單的槍械矩形代替
            # 計算槍的位置和角度
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y

            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2

            # 計算方向
            direction_x = world_mouse_x - player_center_x
            direction_y = world_mouse_y - player_center_y
            distance = math.sqrt(direction_x**2 + direction_y**2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance
            else:
                direction_x = self.facing_direction
                direction_y = 0

            # 繪製簡單的槍械線段（從玩家中心向滑鼠方向）
            shotgun_length = 35  # 散彈槍長度介於機關槍和狙擊槍之間
            end_x = player_center_x - camera_x + direction_x * shotgun_length
            end_y = player_center_y - camera_y + direction_y * shotgun_length

            pygame.draw.line(
                screen,
                SHOTGUN_COLOR,
                (player_center_x - camera_x, player_center_y - camera_y),
                (int(end_x), int(end_y)),
                5,  # 散彈槍粗細介於機關槍和狙擊槍之間
            )

    def draw_assault_rifle(self, screen, camera_x=0, camera_y=0):
        """
        繪製衝鋒槍 - 根據瞄準方向旋轉衝鋒槍圖片，支援左右朝向圖片\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        繪製邏輯:\n
        1. 只有當使用衝鋒槍且圖片載入成功時才繪製\n
        2. 計算瞄準角度並旋轉槍的圖片\n
        3. 根據瞄準方向自動選擇正向或反向圖片\n
        4. 槍的中心位置跟隨玩家\n
        5. 圖片載入失敗時繪製簡單的矩形代替\n
        """
        if self.assault_rifle_image is not None:
            # 獲取滑鼠位置來決定槍的角度
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y

            # 計算玩家中心位置（世界座標）
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2

            # 計算瞄準角度
            direction_x = world_mouse_x - player_center_x
            direction_y = world_mouse_y - player_center_y

            # 如果在甩槍攻擊中，武器會飛離玩家
            if self.is_melee_attacking and self.weapon_flying:
                # 計算武器飛行後的位置
                fly_direction_x = math.cos(math.radians(self.weapon_spin_angle))
                fly_direction_y = math.sin(math.radians(self.weapon_spin_angle))

                # 武器飛到指定距離的位置
                weapon_x = player_center_x + fly_direction_x * self.weapon_fly_distance
                weapon_y = player_center_y + fly_direction_y * self.weapon_fly_distance

                # 使用旋轉角度作為武器的朝向
                angle_degrees = self.weapon_spin_angle + ASSAULT_RIFLE_ROTATION_OFFSET
            else:
                # 正常情況下，武器在玩家身邊並朝向滑鼠
                weapon_x = player_center_x
                weapon_y = player_center_y

                # 計算角度（弧度轉角度）
                angle = math.atan2(direction_y, direction_x)
                angle_degrees = math.degrees(angle) + ASSAULT_RIFLE_ROTATION_OFFSET

            # 根據角度選擇使用哪個圖片
            # 修正圖片方向：往右打使用B&T_APC_9_K_side_profile.png，往左打使用B&T_APC_9_K_side_profile拷貝.png
            if angle_degrees > 90 or angle_degrees < -90:
                # 往左射擊時使用正向圖片（B&T_APC_9_K_side_profile.png）
                if self.assault_rifle_image is not None:
                    rifle_image = self.assault_rifle_image
                    # 調整角度使圖片正確朝向
                    angle_degrees = (
                        angle_degrees - 180
                        if angle_degrees > 0
                        else angle_degrees + 180
                    )
                else:
                    # 沒有圖片時，使用翻轉的備用圖片
                    rifle_image = pygame.transform.flip(
                        self.assault_rifle_reverse_image, True, False
                    )
                    angle_degrees = (
                        angle_degrees - 180
                        if angle_degrees > 0
                        else angle_degrees + 180
                    )
            else:
                # 往右射擊時使用反向圖片（B&T_APC_9_K_side_profile拷貝.png）
                rifle_image = self.assault_rifle_reverse_image

            # 旋轉衝鋒槍圖片
            rotated_rifle = pygame.transform.rotate(rifle_image, -angle_degrees)

            # 計算旋轉後圖片的新中心位置（螢幕座標）
            rifle_rect = rotated_rifle.get_rect()
            rifle_rect.center = (weapon_x - camera_x, weapon_y - camera_y)

            # 繪製旋轉後的衝鋒槍
            screen.blit(rotated_rifle, rifle_rect)
        else:
            # 圖片載入失敗，繪製簡單的槍械矩形代替
            # 計算槍的位置和角度
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + camera_x
            world_mouse_y = mouse_y + camera_y

            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2

            # 計算方向
            direction_x = world_mouse_x - player_center_x
            direction_y = world_mouse_y - player_center_y
            distance = math.sqrt(direction_x**2 + direction_y**2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance
            else:
                direction_x = self.facing_direction
                direction_y = 0

            # 繪製簡單的槍械線段（從玩家中心向滑鼠方向）
            rifle_length = 33  # 衝鋒槍長度
            end_x = player_center_x - camera_x + direction_x * rifle_length
            end_y = player_center_y - camera_y + direction_y * rifle_length

            pygame.draw.line(
                screen,
                ASSAULT_RIFLE_COLOR,
                (player_center_x - camera_x, player_center_y - camera_y),
                (int(end_x), int(end_y)),
                4,  # 衝鋒槍粗細
            )

    def draw_crosshair(self, screen, camera_x=0, camera_y=0):
        """
        繪製狙擊槍準心 - 使用自訂圖片或預設十字準心\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        繪製邏輯:\n
        1. 只在使用狙擊槍時顯示準心\n
        2. 優先使用載入的圖片準心\n
        3. 圖片載入失敗時使用預設十字準心\n
        4. 準心位置跟隨滑鼠游標\n
        """
        if self.current_weapon != "sniper":
            return

        # 獲取滑鼠位置
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.crosshair_image is not None:
            # 使用圖片準心
            # 計算圖片繪製位置，讓圖片中心對齊滑鼠位置
            image_rect = self.crosshair_image.get_rect()
            image_rect.center = (mouse_x, mouse_y)

            # 繪製準心圖片
            screen.blit(self.crosshair_image, image_rect)
        else:
            # 圖片載入失敗，使用預設十字準心
            crosshair_size = 20
            crosshair_color = CROSSHAIR_COLOR

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

    def draw_ultimate_ui(self, screen):
        """
        繪製必殺技UI - 顯示冷卻狀態\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        """
        # 必殺技UI位置（在武器UI下方）
        ui_x = SCREEN_WIDTH - 100
        ui_y = BULLET_UI_Y + 100
        ui_size = 60

        # 獲取冷卻比例
        cooldown_ratio = self.get_ultimate_cooldown_ratio()

        # 繪製背景圓圈
        center_x = ui_x + ui_size // 2
        center_y = ui_y + ui_size // 2
        pygame.draw.circle(screen, GRAY, (center_x, center_y), ui_size // 2, 3)

        # 繪製冷卻進度
        if cooldown_ratio < 1.0:
            # 冷卻中 - 繪製進度扇形
            start_angle = -math.pi / 2  # 從頂部開始
            end_angle = start_angle + (2 * math.pi * cooldown_ratio)

            # 繪製扇形（需要多個線段來模擬）
            points = [(center_x, center_y)]
            for i in range(int(cooldown_ratio * 32) + 1):  # 32個分段
                angle = start_angle + (2 * math.pi * cooldown_ratio * i / 32)
                x = center_x + math.cos(angle) * (ui_size // 2 - 3)
                y = center_y + math.sin(angle) * (ui_size // 2 - 3)
                points.append((x, y))

            if len(points) > 2:
                pygame.draw.polygon(screen, YELLOW, points)
        else:
            # 可使用 - 繪製完整圓圈
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), ui_size // 2 - 3)

        # 繪製閃電符號
        lightning_points = [
            (center_x - 8, center_y - 12),
            (center_x + 4, center_y - 4),
            (center_x - 2, center_y),
            (center_x + 8, center_y + 12),
            (center_x - 4, center_y + 4),
            (center_x + 2, center_y),
        ]
        pygame.draw.polygon(screen, WHITE, lightning_points)

        # 繪製按鍵提示
        font = get_chinese_font(FONT_SIZE_SMALL)
        key_text = font.render("X", True, WHITE)
        key_rect = key_text.get_rect(center=(center_x, center_y + ui_size // 2 + 15))
        screen.blit(key_text, key_rect)

        # 繪製冷卻時間文字
        if cooldown_ratio < 1.0:
            remaining_time = self.ultimate_cooldown * (1.0 - cooldown_ratio)
            time_text = font.render(f"{remaining_time:.1f}s", True, WHITE)
            time_rect = time_text.get_rect(
                center=(center_x, center_y + ui_size // 2 + 35)
            )
            screen.blit(time_text, time_rect)
        else:
            ready_text = font.render("準備好！", True, GREEN)
            ready_rect = ready_text.get_rect(
                center=(center_x, center_y + ui_size // 2 + 35)
            )
            screen.blit(ready_text, ready_rect)
