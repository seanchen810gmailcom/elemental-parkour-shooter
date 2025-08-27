######################載入套件######################
import pygame
import math
import random
import time

# 支援直接執行和模組執行兩種方式
try:
    from ..config import *
    from ..core.game_objects import GameObject, StatusEffect
except ImportError:
    from src.config import *
    from src.core.game_objects import GameObject, StatusEffect

######################基礎怪物類別######################


class Monster(GameObject):
    """
    怪物基礎類別 - 所有怪物的共同父類別\n
    \n
    提供所有怪物的共通功能：\n
    1. 基本屬性（生命值、攻擊力、移動速度）\n
    2. AI 行為框架\n
    3. 狀態效果管理\n
    4. 攻擊和受傷處理\n
    \n
    參數:\n
    x (float): 怪物初始 X 座標\n
    y (float): 怪物初始 Y 座標\n
    width (int): 怪物寬度\n
    height (int): 怪物高度\n
    color (tuple): 怪物顏色\n
    monster_type (str): 怪物類型標識\n
    health (int): 初始生命值\n
    damage (int): 攻擊力\n
    speed (float): 移動速度\n
    """

    def __init__(self, x, y, width, height, color, monster_type, health, damage, speed):
        super().__init__(x, y, width, height, color)

        # 怪物基本屬性
        self.monster_type = monster_type
        self.max_health = health
        self.health = health
        self.damage = damage
        self.base_speed = speed
        self.current_speed = speed

        # 移動相關
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = random.choice([-1, 1])  # 隨機初始方向
        self.on_ground = False

        # 平台相關（防止掉落）
        self.home_platform = None  # 怪物所屬的平台
        self.platform_margin = 20  # 距離平台邊緣的安全距離

        # AI 狀態
        self.ai_state = "patrol"  # 'patrol', 'chase', 'attack', 'stunned'
        self.target_player = None
        self.detection_range = 200
        self.attack_range = 60
        self.attack_cooldown = 2.0  # 攻擊冷卻時間（秒）
        self.last_attack_time = 0

        # 狀態效果管理
        self.status_effects = []
        self.knockback_velocity = 0
        self.knockback_direction = 0

        # 生存狀態
        self.is_alive = True
        self.death_animation_time = 0

    def update_status_effects(self):
        """
        更新所有狀態效果 - 移除過期效果並計算當前速度\n
        """
        # 移除過期的狀態效果
        self.status_effects = [
            effect for effect in self.status_effects if effect.is_active()
        ]

        # 計算當前速度修正
        speed_modifier = 1.0
        for effect in self.status_effects:
            effect_modifier = effect.get_speed_modifier()
            speed_modifier = min(speed_modifier, effect_modifier)

        self.current_speed = self.base_speed * speed_modifier

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

    def detect_player(self, player):
        """
        檢測玩家是否在偵測範圍內\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: True 表示玩家在偵測範圍內\n
        """
        if not player.is_alive:
            return False

        # 計算與玩家的距離
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        return distance <= self.detection_range

    def can_attack_player(self, player):
        """
        檢查是否可以攻擊玩家\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: True 表示可以攻擊\n
        """
        if not player.is_alive:
            return False

        # 檢查攻擊冷卻
        current_time = time.time()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False

        # 檢查攻擊距離
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        return distance <= self.attack_range

    def move_towards_player(self, player):
        """
        朝玩家方向移動\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        if not player.is_alive:
            return

        # 計算朝向玩家的方向
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            # 正規化方向向量
            direction_x = dx / distance
            direction_y = dy / distance

            # 設定移動速度
            self.velocity_x = direction_x * self.current_speed

            # 如果玩家在上方且距離不遠，嘗試跳躍
            if dy < -50 and abs(dx) < 100 and self.on_ground:
                self.velocity_y = -12  # 跳躍力道

    def patrol_movement(self):
        """
        巡邏移動模式 - 左右來回移動\n
        """
        self.velocity_x = self.direction * self.current_speed

        # 隨機改變方向的機率
        if random.random() < 0.01:  # 1% 機率每幀改變方向
            self.direction *= -1

    def apply_knockback(self, force, direction):
        """
        應用擊退效果\n
        \n
        參數:\n
        force (float): 擊退力道\n
        direction (int): 擊退方向 (1: 右, -1: 左)\n
        """
        self.knockback_velocity = force
        self.knockback_direction = direction

    def take_damage(self, damage):
        """
        受到傷害\n
        \n
        參數:\n
        damage (int): 受到的傷害值\n
        \n
        回傳:\n
        bool: True 表示怪物死亡\n
        """
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            return True
        return False

    def attack_player(self, player):
        """
        攻擊玩家 - 基礎攻擊行為\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        \n
        回傳:\n
        bool: True 表示攻擊成功\n
        """
        if not self.can_attack_player(player):
            return False

        # 對玩家造成傷害
        player.take_damage(self.damage)
        self.last_attack_time = time.time()

        # 給玩家一個小的擊退效果
        direction = 1 if player.x > self.x else -1
        if hasattr(player, "apply_knockback"):
            player.apply_knockback(20, direction)

        return True

    def update_ai(self, player, platforms):
        """
        更新 AI 行為 - 基礎 AI 狀態機\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        """
        if not self.is_alive:
            return

        # 檢測玩家
        player_detected = self.detect_player(player)
        can_attack = self.can_attack_player(player)

        # AI 狀態機
        if can_attack:
            self.ai_state = "attack"
            self.attack_player(player)
        elif player_detected:
            self.ai_state = "chase"
            self.move_towards_player(player)
        else:
            self.ai_state = "patrol"
            self.patrol_movement()

    def update_physics(self, platforms):
        """
        更新物理狀態 - 重力、碰撞、移動\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        """
        # 應用擊退效果
        if self.knockback_velocity > 0:
            self.velocity_x += self.knockback_direction * self.knockback_velocity
            self.knockback_velocity *= 0.8  # 逐漸減弱
            if self.knockback_velocity < 1:
                self.knockback_velocity = 0

        # 應用重力
        if not self.on_ground:
            self.velocity_y += GRAVITY
            if self.velocity_y > MAX_FALL_SPEED:
                self.velocity_y = MAX_FALL_SPEED

        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y

        # 檢查是否即將掉出所屬平台
        self.check_platform_boundary()

        # 處理碰撞
        self.handle_collisions(platforms)

        # 螢幕邊界處理
        if self.x < 0:
            self.x = 0
            self.direction = 1
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.direction = -1

        # 如果掉出螢幕底部就死亡
        if self.y > SCREEN_HEIGHT + 100:
            self.is_alive = False

        # 更新碰撞矩形
        self.update_rect()

    def check_platform_boundary(self):
        """
        檢查怪物是否即將掉出所屬平台，如果是則調頭\n
        """
        if self.home_platform is None:
            return

        # 檢查左邊界
        if self.x <= self.home_platform.x + self.platform_margin:
            self.x = self.home_platform.x + self.platform_margin
            self.direction = 1  # 向右轉
            self.velocity_x = 0

        # 檢查右邊界
        elif (
            self.x + self.width
            >= self.home_platform.x + self.home_platform.width - self.platform_margin
        ):
            self.x = (
                self.home_platform.x
                + self.home_platform.width
                - self.platform_margin
                - self.width
            )
            self.direction = -1  # 向左轉
            self.velocity_x = 0

    def handle_collisions(self, platforms):
        """
        處理與平台的碰撞\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        """
        self.on_ground = False
        monster_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        for platform in platforms:
            if monster_rect.colliderect(platform.rect):
                # 計算重疊距離
                overlap_left = monster_rect.right - platform.rect.left
                overlap_right = platform.rect.right - monster_rect.left
                overlap_top = monster_rect.bottom - platform.rect.top
                overlap_bottom = platform.rect.bottom - monster_rect.top

                # 找出最小重疊距離，決定碰撞方向
                min_overlap = min(
                    overlap_left, overlap_right, overlap_top, overlap_bottom
                )

                if min_overlap == overlap_top and self.velocity_y > 0:
                    # 從上方落到平台上
                    self.y = platform.rect.top - self.height
                    self.velocity_y = 0
                    self.on_ground = True

                elif min_overlap == overlap_bottom and self.velocity_y < 0:
                    # 從下方撞到平台
                    self.y = platform.rect.bottom
                    self.velocity_y = 0

                elif min_overlap == overlap_left and self.velocity_x > 0:
                    # 從左側撞到平台
                    self.x = platform.rect.left - self.width
                    self.direction = -1  # 改變巡邏方向

                elif min_overlap == overlap_right and self.velocity_x < 0:
                    # 從右側撞到平台
                    self.x = platform.rect.right
                    self.direction = 1  # 改變巡邏方向

    def update(self, player, platforms):
        """
        怪物的主要更新方法\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        """
        if not self.is_alive:
            return

        # 更新狀態效果
        self.update_status_effects()

        # 更新 AI 行為
        self.update_ai(player, platforms)

        # 更新物理狀態
        self.update_physics(platforms)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製怪物 - 包含生命值條和狀態指示\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        if not self.is_alive:
            return

        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 根據狀態效果改變顏色
        current_color = self.color
        for effect in self.status_effects:
            if effect.effect_type == "slow":
                # 減速狀態：顏色變暗
                current_color = tuple(max(0, c - 50) for c in self.color)
                break
            elif effect.effect_type == "paralysis":
                # 麻痺狀態：變成灰色
                current_color = GRAY
                break

        # 繪製怪物本體（使用螢幕座標）
        monster_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, current_color, monster_rect)

        # 繪製生命值條（在怪物上方）
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 6
            bar_x = screen_x
            bar_y = screen_y - bar_height - 5

            # 背景（紅色）
            bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(screen, RED, bg_rect)

            # 當前生命值（綠色）
            health_ratio = self.health / self.max_health
            health_width = int(bar_width * health_ratio)
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            pygame.draw.rect(screen, GREEN, health_rect)

        # 繪製方向指示（小箭頭）
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2

        if self.direction > 0:
            # 面向右邊的箭頭
            arrow_points = [
                (center_x + 5, center_y),
                (center_x + 10, center_y - 3),
                (center_x + 10, center_y + 3),
            ]
        else:
            # 面向左邊的箭頭
            arrow_points = [
                (center_x - 5, center_y),
                (center_x - 10, center_y - 3),
                (center_x - 10, center_y + 3),
            ]

        pygame.draw.polygon(screen, WHITE, arrow_points)


######################岩漿怪類別######################


class LavaMonster(Monster):
    """
    岩漿怪 - 防禦力高，能噴出熔岩球的火屬性怪物\n
    \n
    特殊能力：\n
    1. 對火屬性攻擊有抗性\n
    2. 對水屬性攻擊脆弱\n
    3. 能噴射熔岩球進行遠程攻擊\n
    4. 移動時會在地面留下短暫的熔岩痕跡\n
    \n
    參數:\n
    x (float): 初始 X 座標\n
    y (float): 初始 Y 座標\n
    """

    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            LAVA_MONSTER_WIDTH,
            LAVA_MONSTER_HEIGHT,
            LAVA_MONSTER_COLOR,
            "lava_monster",
            LAVA_MONSTER_HEALTH,
            LAVA_MONSTER_DAMAGE,
            LAVA_MONSTER_SPEED,
        )

        # 岩漿怪特殊屬性
        self.lava_ball_cooldown = 3.0  # 熔岩球攻擊冷卻時間
        self.last_lava_ball_time = 0
        self.lava_balls = []  # 噴射的熔岩球列表

    def create_lava_ball(self, target_x, target_y):
        """
        建立熔岩球攻擊\n
        \n
        參數:\n
        target_x (float): 目標 X 座標\n
        target_y (float): 目標 Y 座標\n
        \n
        回傳:\n
        dict: 熔岩球資訊\n
        """
        current_time = time.time()
        if current_time - self.last_lava_ball_time < self.lava_ball_cooldown:
            return None

        # 計算發射方向
        start_x = self.x + self.width // 2
        start_y = self.y + self.height // 2

        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            direction_x = dx / distance
            direction_y = dy / distance

            lava_ball = {
                "x": start_x,
                "y": start_y,
                "velocity_x": direction_x * 8,  # 熔岩球速度
                "velocity_y": direction_y * 8,
                "damage": self.damage,
                "lifetime": 3.0,  # 3秒後消失
                "created_time": current_time,
            }

            self.lava_balls.append(lava_ball)
            self.last_lava_ball_time = current_time
            return lava_ball

        return None

    def update_lava_balls(self):
        """
        更新所有熔岩球的狀態\n
        """
        current_time = time.time()
        active_balls = []

        for ball in self.lava_balls:
            # 檢查生存時間
            if current_time - ball["created_time"] > ball["lifetime"]:
                continue

            # 更新位置
            ball["x"] += ball["velocity_x"]
            ball["y"] += ball["velocity_y"]

            # 檢查是否超出螢幕
            if 0 <= ball["x"] <= SCREEN_WIDTH and 0 <= ball["y"] <= SCREEN_HEIGHT:
                active_balls.append(ball)

        self.lava_balls = active_balls

    def attack_player(self, player):
        """
        岩漿怪的攻擊方式 - 近戰 + 遠程熔岩球\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        \n
        回傳:\n
        bool: True 表示攻擊成功\n
        """
        # 先嘗試近戰攻擊
        if super().attack_player(player):
            return True

        # 如果玩家在中距離範圍，使用熔岩球攻擊
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if 60 < distance <= 150:  # 中距離攻擊範圍
            lava_ball = self.create_lava_ball(player.x, player.y)
            return lava_ball is not None

        return False

    def check_lava_ball_collision(self, player):
        """
        檢查熔岩球與玩家的碰撞\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: True 表示有熔岩球擊中玩家\n
        """
        balls_to_remove = []
        hit = False

        for i, ball in enumerate(self.lava_balls):
            ball_rect = pygame.Rect(ball["x"] - 8, ball["y"] - 8, 16, 16)

            if ball_rect.colliderect(player.rect):
                # 熔岩球擊中玩家
                player.take_damage(ball["damage"])
                balls_to_remove.append(i)
                hit = True

        # 移除擊中的熔岩球
        for i in reversed(balls_to_remove):
            del self.lava_balls[i]

        return hit

    def update(self, player, platforms):
        """
        岩漿怪的更新方法\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        """
        super().update(player, platforms)

        if self.is_alive:
            # 更新熔岩球
            self.update_lava_balls()

            # 檢查熔岩球碰撞
            self.check_lava_ball_collision(player)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製岩漿怪和熔岩球\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        super().draw(screen, camera_x, camera_y)

        # 繪製熔岩球（考慮攝影機偏移）
        for ball in self.lava_balls:
            ball_screen_x = ball["x"] - camera_x
            ball_screen_y = ball["y"] - camera_y
            # 只繪製在螢幕範圍內的熔岩球
            if (
                -20 <= ball_screen_x <= SCREEN_WIDTH + 20
                and -20 <= ball_screen_y <= SCREEN_HEIGHT + 20
            ):
                pygame.draw.circle(
                    screen, LAVA_COLOR, (int(ball_screen_x), int(ball_screen_y)), 8
                )
                pygame.draw.circle(
                    screen, YELLOW, (int(ball_screen_x), int(ball_screen_y)), 4
                )


######################水怪類別######################


class WaterMonster(Monster):
    """
    水怪 - 靈活快速，能潑灑大範圍水彈的水屬性怪物\n
    \n
    特殊能力：\n
    1. 移動速度快\n
    2. 對雷屬性和火屬性攻擊脆弱\n
    3. 能潑灑多發水彈進行範圍攻擊\n
    4. 在水中（如果有）移動更快\n
    \n
    參數:\n
    x (float): 初始 X 座標\n
    y (float): 初始 Y 座標\n
    """

    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            WATER_MONSTER_WIDTH,
            WATER_MONSTER_HEIGHT,
            WATER_MONSTER_COLOR,
            "water_monster",
            WATER_MONSTER_HEALTH,
            WATER_MONSTER_DAMAGE,
            WATER_MONSTER_SPEED,
        )

        # 水怪特殊屬性
        self.splash_cooldown = 2.5  # 水彈攻擊冷卻時間
        self.last_splash_time = 0
        self.water_bullets = []  # 水彈列表
        self.dash_cooldown = 4.0  # 衝刺冷卻時間
        self.last_dash_time = 0

    def create_water_splash(self, player):
        """
        建立水彈散射攻擊\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        \n
        回傳:\n
        list: 建立的水彈列表\n
        """
        current_time = time.time()
        if current_time - self.last_splash_time < self.splash_cooldown:
            return []

        new_bullets = []
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        # 朝玩家方向發射5發水彈（扇形散射）
        dx = player.x - center_x
        dy = player.y - center_y
        base_angle = math.atan2(dy, dx)

        for i in range(5):
            # 每發子彈都有些微的角度偏移
            angle_offset = (i - 2) * 0.3  # -0.6 到 +0.6 弧度
            angle = base_angle + angle_offset

            bullet = {
                "x": center_x,
                "y": center_y,
                "velocity_x": math.cos(angle) * 6,
                "velocity_y": math.sin(angle) * 6,
                "damage": self.damage // 2,  # 每發水彈傷害較低
                "lifetime": 2.0,
                "created_time": current_time,
            }

            new_bullets.append(bullet)

        self.water_bullets.extend(new_bullets)
        self.last_splash_time = current_time
        return new_bullets

    def dash_towards_player(self, player):
        """
        朝玩家衝刺\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        \n
        回傳:\n
        bool: True 表示成功發動衝刺\n
        """
        current_time = time.time()
        if current_time - self.last_dash_time < self.dash_cooldown:
            return False

        # 計算衝刺方向
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0 and distance <= 200:  # 衝刺有效距離
            direction_x = dx / distance

            # 給予強大的水平衝刺力
            self.velocity_x = direction_x * 15

            self.last_dash_time = current_time
            return True

        return False

    def update_water_bullets(self):
        """
        更新所有水彈的狀態\n
        """
        current_time = time.time()
        active_bullets = []

        for bullet in self.water_bullets:
            # 檢查生存時間
            if current_time - bullet["created_time"] > bullet["lifetime"]:
                continue

            # 更新位置
            bullet["x"] += bullet["velocity_x"]
            bullet["y"] += bullet["velocity_y"]

            # 檢查是否超出螢幕
            if 0 <= bullet["x"] <= SCREEN_WIDTH and 0 <= bullet["y"] <= SCREEN_HEIGHT:
                active_bullets.append(bullet)

        self.water_bullets = active_bullets

    def attack_player(self, player):
        """
        水怪的攻擊方式 - 近戰、水彈散射、衝刺\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        \n
        回傳:\n
        bool: True 表示攻擊成功\n
        """
        # 先嘗試近戰攻擊
        if super().attack_player(player):
            return True

        # 計算與玩家的距離
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        # 中距離使用水彈散射
        if 60 < distance <= 120:
            bullets = self.create_water_splash(player)
            return len(bullets) > 0

        # 遠距離嘗試衝刺
        if 120 < distance <= 200:
            return self.dash_towards_player(player)

        return False

    def check_water_bullet_collision(self, player):
        """
        檢查水彈與玩家的碰撞\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: True 表示有水彈擊中玩家\n
        """
        bullets_to_remove = []
        hit = False

        for i, bullet in enumerate(self.water_bullets):
            bullet_rect = pygame.Rect(bullet["x"] - 6, bullet["y"] - 6, 12, 12)

            if bullet_rect.colliderect(player.rect):
                # 水彈擊中玩家
                player.take_damage(bullet["damage"])
                bullets_to_remove.append(i)
                hit = True

        # 移除擊中的水彈
        for i in reversed(bullets_to_remove):
            del self.water_bullets[i]

        return hit

    def update(self, player, platforms):
        """
        水怪的更新方法\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        """
        super().update(player, platforms)

        if self.is_alive:
            # 更新水彈
            self.update_water_bullets()

            # 檢查水彈碰撞
            self.check_water_bullet_collision(player)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製水怪和水彈\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        super().draw(screen, camera_x, camera_y)

        # 繪製水彈（考慮攝影機偏移）
        for bullet in self.water_bullets:
            bullet_screen_x = bullet["x"] - camera_x
            bullet_screen_y = bullet["y"] - camera_y
            # 只繪製在螢幕範圍內的水彈
            if (
                -20 <= bullet_screen_x <= SCREEN_WIDTH + 20
                and -20 <= bullet_screen_y <= SCREEN_HEIGHT + 20
            ):
                pygame.draw.circle(
                    screen, CYAN, (int(bullet_screen_x), int(bullet_screen_y)), 6
                )
                pygame.draw.circle(
                    screen, WHITE, (int(bullet_screen_x), int(bullet_screen_y)), 3
                )


######################龍捲風怪類別######################


class TornadoMonster(Monster):
    """
    龍捲風怪 - 移動極快，可以捲走玩家造成位移干擾的風屬性怪物\n
    \n
    特殊能力：\n
    1. 移動速度極快\n
    2. 對冰屬性攻擊脆弱（減速效果強）\n
    3. 血量較低但難以命中\n
    4. 能產生旋風攻擊，推開玩家\n
    5. 隨機瞬移能力\n
    \n
    參數:\n
    x (float): 初始 X 座標\n
    y (float): 初始 Y 座標\n
    """

    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            TORNADO_MONSTER_WIDTH,
            TORNADO_MONSTER_HEIGHT,
            TORNADO_MONSTER_COLOR,
            "tornado_monster",
            TORNADO_MONSTER_HEALTH,
            TORNADO_MONSTER_DAMAGE,
            TORNADO_MONSTER_SPEED,
        )

        # 龍捲風怪特殊屬性
        self.whirlwind_cooldown = 3.0  # 旋風攻擊冷卻時間
        self.last_whirlwind_time = 0
        self.teleport_cooldown = 8.0  # 瞬移冷卻時間
        self.last_teleport_time = 0
        self.is_spinning = False  # 是否在旋轉狀態
        self.spin_timer = 0

    def create_whirlwind(self, player):
        """
        建立旋風攻擊\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        \n
        回傳:\n
        dict or None: 旋風攻擊資訊\n
        """
        current_time = time.time()
        if current_time - self.last_whirlwind_time < self.whirlwind_cooldown:
            return None

        # 計算與玩家的距離
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance <= 80:  # 旋風攻擊範圍
            # 啟動旋轉狀態
            self.is_spinning = True
            self.spin_timer = 1.5  # 旋轉1.5秒

            # 計算推開玩家的力道和方向
            if distance > 0:
                push_x = (dx / distance) * 150  # 推開力道
                push_y = -50  # 向上推一點

                # 對玩家施加推力（如果玩家有相應方法）
                if hasattr(player, "velocity_x") and hasattr(player, "velocity_y"):
                    player.velocity_x += push_x * 0.3
                    player.velocity_y += push_y * 0.3

                # 造成傷害
                player.take_damage(self.damage)

                self.last_whirlwind_time = current_time
                return {
                    "type": "whirlwind",
                    "push_x": push_x,
                    "push_y": push_y,
                    "damage": self.damage,
                }

        return None

    def attempt_teleport(self, player, platforms):
        """
        嘗試瞬移到玩家附近\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        bool: True 表示成功瞬移\n
        """
        current_time = time.time()
        if current_time - self.last_teleport_time < self.teleport_cooldown:
            return False

        # 計算與玩家的距離
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        # 只在距離較遠時瞬移
        if distance > 200:
            # 嘗試瞬移到玩家附近（但不要太近）
            for _ in range(10):  # 最多嘗試10次找到合適位置
                # 在玩家周圍100-150像素範圍內隨機選擇位置
                angle = random.uniform(0, 2 * math.pi)
                teleport_distance = random.uniform(100, 150)

                new_x = player.x + math.cos(angle) * teleport_distance
                new_y = player.y + math.sin(angle) * teleport_distance

                # 檢查新位置是否在螢幕內
                if (
                    0 <= new_x <= SCREEN_WIDTH - self.width
                    and 0 <= new_y <= SCREEN_HEIGHT - self.height
                ):

                    # 瞬移
                    self.x = new_x
                    self.y = new_y
                    self.last_teleport_time = current_time
                    return True

        return False

    def update_spin_state(self):
        """
        更新旋轉狀態\n
        """
        if self.is_spinning:
            self.spin_timer -= 1 / 60  # 假設60 FPS
            if self.spin_timer <= 0:
                self.is_spinning = False
                self.spin_timer = 0

    def attack_player(self, player):
        """
        龍捲風怪的攻擊方式 - 近戰、旋風、瞬移\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        \n
        回傳:\n
        bool: True 表示攻擊成功\n
        """
        # 先嘗試近戰攻擊
        if super().attack_player(player):
            return True

        # 嘗試旋風攻擊
        whirlwind = self.create_whirlwind(player)
        if whirlwind:
            return True

        return False

    def update_ai(self, player, platforms):
        """
        龍捲風怪的 AI - 更激進的追擊行為\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        """
        if not self.is_alive:
            return

        # 嘗試瞬移
        self.attempt_teleport(player, platforms)

        # 基礎 AI 行為
        super().update_ai(player, platforms)

        # 龍捲風怪移動時有額外的隨機性
        if self.ai_state == "chase":
            # 增加一些隨機的左右搖擺
            self.velocity_x += random.uniform(-2, 2)

    def update(self, player, platforms):
        """
        龍捲風怪的更新方法\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        """
        super().update(player, platforms)

        if self.is_alive:
            # 更新旋轉狀態
            self.update_spin_state()

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製龍捲風怪\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        參數:\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if self.is_spinning:
            # 旋轉狀態：繪製旋風效果
            center_x = screen_x + self.width // 2
            center_y = screen_y + self.height // 2

            # 繪製多層圓圈表示旋風
            for i in range(3):
                radius = 30 + i * 15
                alpha = 100 - i * 30
                # pygame 沒有直接的透明度支持，用較淺的顏色代替
                wind_color = tuple(min(255, c + alpha) for c in TORNADO_MONSTER_COLOR)
                pygame.draw.circle(screen, wind_color, (center_x, center_y), radius, 3)

        # 繪製基本怪物
        super().draw(screen, camera_x, camera_y)

        # 如果在旋轉，在邊緣加上白色光暈
        if self.is_spinning:
            tornado_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
            pygame.draw.rect(screen, WHITE, tornado_rect, 3)
