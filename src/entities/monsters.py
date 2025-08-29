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
        damage_result = player.take_damage(self.damage)
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

        # 載入怪物圖片
        self.image = self.load_monster_image()

    def load_monster_image(self):
        """
        載入岩漿怪圖片\n
        \n
        回傳:\n
        pygame.Surface or None: 圖片表面，載入失敗則返回 None\n
        """
        try:
            # 檢查是否為Boss（根據當前尺寸判斷）
            is_boss = (
                self.width > LAVA_MONSTER_WIDTH or self.height > LAVA_MONSTER_HEIGHT
            )

            if is_boss:
                # Boss使用專用的岩漿Boss圖片
                image = pygame.image.load(LAVA_BOSS_IMAGE_PATH).convert_alpha()
                image = pygame.transform.scale(image, LAVA_BOSS_IMAGE_SIZE)
                print(f"✅ 成功載入岩漿Boss圖片: {LAVA_BOSS_IMAGE_PATH}")
            else:
                # 普通岩漿怪使用小火怪圖片
                image = pygame.image.load(LAVA_MONSTER_IMAGE_PATH).convert_alpha()
                image = pygame.transform.scale(image, LAVA_MONSTER_IMAGE_SIZE)
                print(f"✅ 成功載入岩漿怪圖片: {LAVA_MONSTER_IMAGE_PATH}")

            return image
        except (pygame.error, FileNotFoundError) as e:
            # 圖片載入失敗，使用預設顏色繪製
            print(f"⚠️ 載入岩漿怪圖片失敗: {e}")
            print("🎨 將使用預設顏色矩形繪製")
            return None

    def reload_image_if_boss(self):
        """
        當怪物成為Boss時重新載入適當大小的圖片\n
        這個方法會在Monster被設定為Boss後呼叫\n
        """
        self.image = self.load_monster_image()

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

    def auto_heal(self):
        """
        自動回血機制（僅限Boss模式）\n
        """
        # 只有當怪物被設定為Boss時才會回血
        if not hasattr(self, "heal_cooldown") or not hasattr(self, "is_boss"):
            return

        current_time = time.time()
        if current_time - self.last_heal_time >= self.heal_cooldown:
            if self.health < self.max_health:
                old_health = self.health
                self.health = min(self.max_health, self.health + self.heal_amount)
                if self.health > old_health:
                    print(f"💚 岩漿Boss回血：{old_health} → {self.health}")

            self.last_heal_time = current_time

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

            # 如果是Boss模式，執行自動回血
            self.auto_heal()

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製岩漿怪和熔岩球\n
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

        # 根據狀態效果決定繪製方式
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

        # 繪製岩漿怪本體
        if self.image is not None:
            # 使用圖片繪製
            image_to_draw = self.image

            # 如果有狀態效果，需要調整圖片顏色（簡化處理：在圖片上疊加半透明色塊）
            if current_color != self.color:
                # 建立顏色覆蓋層
                color_overlay = pygame.Surface(
                    (self.width, self.height), pygame.SRCALPHA
                )
                color_overlay.fill((*current_color, 100))  # 半透明覆蓋

                # 複製原圖並疊加顏色
                image_to_draw = self.image.copy()
                image_to_draw.blit(
                    color_overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2
                )

            # 根據方向翻轉圖片
            if self.direction < 0:
                image_to_draw = pygame.transform.flip(image_to_draw, True, False)

            # 檢查是否為Boss（根據當前尺寸判斷）
            is_boss = (
                self.width > LAVA_MONSTER_WIDTH or self.height > LAVA_MONSTER_HEIGHT
            )

            # 如果是Boss，確保圖片底部對齊Boss的碰撞體積底部
            if is_boss:
                # 計算Boss圖片繪製位置，確保圖片底部與碰撞體積底部對齊
                boss_image_y = screen_y + self.height - image_to_draw.get_height()
                screen.blit(image_to_draw, (screen_x, boss_image_y))
            else:
                # 普通岩漿怪直接在位置上繪製
                screen.blit(image_to_draw, (screen_x, screen_y))
        else:
            # 圖片載入失敗，使用矩形繪製
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

        # 載入怪物圖片
        self.image = self.load_monster_image()

    def load_monster_image(self):
        """
        載入水怪圖片\n
        \n
        回傳:\n
        pygame.Surface or None: 圖片表面，載入失敗則返回 None\n
        """
        try:
            # 載入圖片檔案
            image = pygame.image.load(WATER_MONSTER_IMAGE_PATH).convert_alpha()
            # 縮放到指定大小
            image = pygame.transform.scale(image, WATER_MONSTER_IMAGE_SIZE)
            print(f"✅ 成功載入水怪圖片: {WATER_MONSTER_IMAGE_PATH}")
            return image
        except (pygame.error, FileNotFoundError) as e:
            # 圖片載入失敗，使用預設顏色繪製
            print(f"⚠️ 載入水怪圖片失敗: {e}")
            print("🎨 將使用預設顏色矩形繪製")
            return None

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
        if not self.is_alive:
            return

        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 根據狀態效果決定繪製方式
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

        # 繪製水怪本體
        if self.image is not None:
            # 使用圖片繪製
            image_to_draw = self.image

            # 如果有狀態效果，需要調整圖片顏色（簡化處理：在圖片上疊加半透明色塊）
            if current_color != self.color:
                # 建立顏色覆蓋層
                color_overlay = pygame.Surface(
                    (self.width, self.height), pygame.SRCALPHA
                )
                color_overlay.fill((*current_color, 100))  # 半透明覆蓋

                # 複製原圖並疊加顏色
                image_to_draw = self.image.copy()
                image_to_draw.blit(
                    color_overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2
                )

            # 根據方向翻轉圖片
            if self.direction < 0:
                image_to_draw = pygame.transform.flip(image_to_draw, True, False)

            screen.blit(image_to_draw, (screen_x, screen_y))
        else:
            # 圖片載入失敗，使用矩形繪製
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


######################狙擊Boss類別######################


class SniperBoss(Monster):
    """
    狙擊Boss - 超強戰術型Boss，擁有自動追蹤子彈、震波攻擊和躲避能力\n
    \n
    特殊能力：\n
    1. 自動追蹤子彈：每5秒發射會自動追蹤玩家的子彈，隨時間消失\n
    2. 震波攻擊：跳躍後落地產生震波，擊退並傷害玩家\n
    3. 躲避AI：能檢測玩家子彈並進行閃避移動\n
    4. 自動回血：每5秒回復1點生命值\n
    5. 超高血量：比普通怪物高1/3倍\n
    \n
    參數:\n
    x (float): 初始 X 座標\n
    y (float): 初始 Y 座標\n
    """

    def __init__(self, x, y):
        # 基於龍捲風怪的基礎屬性，但大幅增強
        super().__init__(
            x,
            y,
            SNIPER_BOSS_WIDTH,
            SNIPER_BOSS_HEIGHT,
            SNIPER_BOSS_COLOR,
            "sniper_boss",
            SNIPER_BOSS_HEALTH,
            SNIPER_BOSS_DAMAGE,
            SNIPER_BOSS_SPEED,
        )

        # Boss標記
        self.is_boss = True

        # 提升Boss的攻擊範圍和檢測範圍
        self.detection_range = 300  # 大幅增加檢測範圍
        self.attack_range = 250  # 大幅增加攻擊範圍

        # 自動追蹤子彈系統
        self.tracking_bullet_cooldown = 2.0  # 每2秒發射一次追蹤子彈（提高頻率）
        self.last_tracking_bullet_time = 0
        self.tracking_bullets = []

        # 震波攻擊系統
        self.shockwave_cooldown = 6.0  # 震波攻擊冷卻時間（降低冷卻）
        self.last_shockwave_time = 0
        self.is_jumping = False  # 是否在跳躍狀態
        self.jump_phase = "prepare"  # 跳躍階段：prepare, jumping, landing
        self.jump_timer = 0
        self.shockwaves = []  # 當前活躍震波列表

        # 自動回血系統
        self.heal_cooldown = 5.0  # 每5秒回血一次
        self.last_heal_time = 0
        self.heal_amount = 2  # 每次回血量，從1點提升到2點

        # 躲避AI系統
        self.dodge_detection_range = 150  # 子彈檢測範圍
        self.dodge_speed_multiplier = 2.0  # 躲避時的速度倍數
        self.is_dodging = False
        self.dodge_timer = 0
        self.dodge_direction = 0  # 躲避方向

        # 載入狙擊Boss圖片
        self.load_sniper_images()

        print(f"🎯 狙擊Boss已生成！具備追蹤子彈、震波攻擊和躲避能力！")

    def load_sniper_images(self):
        """
        載入狙擊Boss的左右朝向圖片\n
        """
        try:
            # 載入往左看的圖片
            self.image_left = pygame.image.load(
                SNIPER_BOSS_LEFT_IMAGE_PATH
            ).convert_alpha()
            self.image_left = pygame.transform.scale(
                self.image_left, SNIPER_BOSS_IMAGE_SIZE
            )
            print(f"✅ 成功載入狙擊Boss往左圖片: {SNIPER_BOSS_LEFT_IMAGE_PATH}")

            # 載入往右看的圖片
            self.image_right = pygame.image.load(
                SNIPER_BOSS_RIGHT_IMAGE_PATH
            ).convert_alpha()
            self.image_right = pygame.transform.scale(
                self.image_right, SNIPER_BOSS_IMAGE_SIZE
            )
            print(f"✅ 成功載入狙擊Boss往右圖片: {SNIPER_BOSS_RIGHT_IMAGE_PATH}")

        except (pygame.error, FileNotFoundError) as e:
            # 圖片載入失敗，使用預設顏色繪製
            print(f"⚠️ 載入狙擊Boss圖片失敗: {e}")
            print("🎨 將使用預設顏色矩形繪製")
            self.image_left = None
            self.image_right = None

    def get_current_image(self):
        """
        根據朝向獲取當前應該使用的圖片\n
        \n
        回傳:\n
        pygame.Surface or None: 當前方向的圖片\n
        """
        if self.direction < 0 and self.image_left is not None:
            return self.image_left
        elif self.direction >= 0 and self.image_right is not None:
            return self.image_right
        else:
            return None

    def create_tracking_bullet(self, target_x, target_y):
        """
        創建自動追蹤子彈\n
        \n
        參數:\n
        target_x (float): 目標 X 座標\n
        target_y (float): 目標 Y 座標\n
        \n
        回傳:\n
        dict or None: 追蹤子彈資訊\n
        """
        current_time = time.time()
        if (
            current_time - self.last_tracking_bullet_time
            < self.tracking_bullet_cooldown
        ):
            return None

        # 計算發射起點
        start_x = self.x + self.width // 2
        start_y = self.y + self.height // 2

        tracking_bullet = {
            "x": start_x,
            "y": start_y,
            "target_x": target_x,  # 追蹤目標座標
            "target_y": target_y,
            "speed": 8,  # 追蹤子彈速度
            "damage": self.damage,
            "lifetime": 7.0,  # 7秒後消失
            "created_time": current_time,
            "tracking_strength": 0.1,  # 追蹤強度，控制轉彎靈敏度
        }

        self.tracking_bullets.append(tracking_bullet)
        self.last_tracking_bullet_time = current_time
        print(f"🎯 狙擊Boss發射追蹤子彈！")
        return tracking_bullet

    def update_tracking_bullets(self, player):
        """
        更新所有追蹤子彈的狀態\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        current_time = time.time()
        active_bullets = []

        for bullet in self.tracking_bullets:
            # 檢查生存時間
            if current_time - bullet["created_time"] > bullet["lifetime"]:
                continue

            # 更新追蹤目標（玩家位置）
            bullet["target_x"] = player.x + player.width // 2
            bullet["target_y"] = player.y + player.height // 2

            # 計算朝向目標的方向
            dx = bullet["target_x"] - bullet["x"]
            dy = bullet["target_y"] - bullet["y"]
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0:
                # 計算追蹤移動
                direction_x = dx / distance
                direction_y = dy / distance

                # 移動子彈朝向目標
                bullet["x"] += direction_x * bullet["speed"]
                bullet["y"] += direction_y * bullet["speed"]

            # 檢查是否超出螢幕邊界
            if 0 <= bullet["x"] <= SCREEN_WIDTH and 0 <= bullet["y"] <= SCREEN_HEIGHT:
                active_bullets.append(bullet)

        self.tracking_bullets = active_bullets

    def check_tracking_bullet_collision(self, player):
        """
        檢查追蹤子彈與玩家的碰撞\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: True 表示有追蹤子彈擊中玩家\n
        """
        bullets_to_remove = []
        hit = False

        for i, bullet in enumerate(self.tracking_bullets):
            bullet_rect = pygame.Rect(bullet["x"] - 8, bullet["y"] - 8, 16, 16)

            if bullet_rect.colliderect(player.rect):
                # 追蹤子彈擊中玩家
                player.take_damage(bullet["damage"])
                bullets_to_remove.append(i)
                hit = True
                print(f"🎯 追蹤子彈擊中玩家！造成 {bullet['damage']} 點傷害")

        # 移除擊中的追蹤子彈
        for i in reversed(bullets_to_remove):
            del self.tracking_bullets[i]

        return hit

    def perform_shockwave_attack(self, player):
        """
        執行震波攻擊 - 跳躍然後落地產生震波\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        \n
        回傳:\n
        bool: True 表示成功發動震波攻擊\n
        """
        current_time = time.time()
        if current_time - self.last_shockwave_time < self.shockwave_cooldown:
            return False

        # 計算與玩家的距離
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        # 只在合適距離內發動震波攻擊（調整距離範圍）
        if 50 <= distance <= 300:  # 擴大震波攻擊範圍
            self.is_jumping = True
            self.jump_phase = "prepare"
            self.jump_timer = 0.5  # 準備時間

            # 給Boss強大的跳躍力
            self.velocity_y = -25  # 超強跳躍力

            self.last_shockwave_time = current_time
            print(f"💥 狙擊Boss準備震波攻擊！")
            return True

        return False

    def create_shockwave(self):
        """
        在Boss落地位置創建震波\n
        \n
        回傳:\n
        dict: 震波資訊\n
        """
        shockwave = {
            "x": self.x + self.width // 2,  # 震波中心
            "y": self.y + self.height,  # 在Boss腳下
            "radius": 0,  # 初始半徑
            "max_radius": 150,  # 最大擴散半徑
            "expansion_speed": 8,  # 擴散速度
            "damage": int(self.damage * 1.2),  # 震波傷害
            "knockback_force": 200,  # 擊退力道
            "lifetime": 2.0,  # 震波持續時間
            "created_time": time.time(),
            "hit_player": False,  # 防止重複傷害
        }

        self.shockwaves.append(shockwave)
        print(f"💥 震波產生！半徑將擴散至 {shockwave['max_radius']} 像素")
        return shockwave

    def update_shockwaves(self, player):
        """
        更新所有震波的狀態並檢查碰撞\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        current_time = time.time()
        active_shockwaves = []

        for shockwave in self.shockwaves:
            # 檢查震波是否過期
            if current_time - shockwave["created_time"] > shockwave["lifetime"]:
                continue

            # 擴散震波
            shockwave["radius"] += shockwave["expansion_speed"]

            # 檢查是否達到最大半徑
            if shockwave["radius"] <= shockwave["max_radius"]:
                # 檢查與玩家的碰撞（只傷害一次）
                if not shockwave["hit_player"]:
                    player_center_x = player.x + player.width // 2
                    player_center_y = player.y + player.height // 2

                    dx = player_center_x - shockwave["x"]
                    dy = player_center_y - shockwave["y"]
                    distance_to_player = math.sqrt(dx**2 + dy**2)

                    # 如果玩家在震波範圍內
                    if distance_to_player <= shockwave["radius"] + 20:  # 添加一些容錯
                        # 對玩家造成傷害
                        player.take_damage(shockwave["damage"])

                        # 計算擊退方向
                        if distance_to_player > 0:
                            knockback_x = (dx / distance_to_player) * shockwave[
                                "knockback_force"
                            ]
                            knockback_y = -50  # 向上推一點

                            # 應用擊退效果
                            if hasattr(player, "velocity_x") and hasattr(
                                player, "velocity_y"
                            ):
                                player.velocity_x += knockback_x * 0.1
                                player.velocity_y += knockback_y * 0.1

                        shockwave["hit_player"] = True
                        print(
                            f"💥 震波擊中玩家！造成 {shockwave['damage']} 點傷害並擊退"
                        )

                active_shockwaves.append(shockwave)

        self.shockwaves = active_shockwaves

    def detect_and_dodge_bullets(self, bullets):
        """
        檢測玩家子彈並執行躲避動作\n
        \n
        參數:\n
        bullets (list): 玩家子彈列表\n
        \n
        回傳:\n
        bool: True 表示檢測到子彈並開始躲避\n
        """
        if self.is_dodging:
            return False

        boss_center_x = self.x + self.width // 2
        boss_center_y = self.y + self.height // 2

        for bullet in bullets:
            # 支援子彈物件和字典格式
            if hasattr(bullet, "x"):
                bullet_x, bullet_y = bullet.x, bullet.y
                bullet_velocity_x = getattr(bullet, "velocity_x", 0)
                bullet_velocity_y = getattr(bullet, "velocity_y", 0)
            else:
                bullet_x, bullet_y = bullet.get("x", 0), bullet.get("y", 0)
                bullet_velocity_x = bullet.get("velocity_x", 0)
                bullet_velocity_y = bullet.get("velocity_y", 0)

            # 計算子彈與Boss的距離
            dx = bullet_x - boss_center_x
            dy = bullet_y - boss_center_y
            distance = math.sqrt(dx**2 + dy**2)

            # 如果子彈在檢測範圍內
            if distance <= self.dodge_detection_range:

                # 預測子彈會朝Boss方向移動
                if abs(bullet_velocity_x) > 0:
                    time_to_impact = abs(dx / bullet_velocity_x)
                    predicted_y = bullet_y + bullet_velocity_y * time_to_impact

                    # 如果預測軌跡會經過Boss位置
                    if abs(predicted_y - boss_center_y) < self.height:
                        # 決定躲避方向（垂直於子彈方向）
                        if bullet_velocity_x > 0:  # 子彈向右，Boss向左或上下躲
                            self.dodge_direction = -1
                        else:  # 子彈向左，Boss向右或上下躲
                            self.dodge_direction = 1

                        # 開始躲避
                        self.is_dodging = True
                        self.dodge_timer = 0.8  # 躲避持續時間
                        print(f"🛡️ 狙擊Boss檢測到子彈，開始躲避！")
                        return True

        return False

    def update_dodge_state(self):
        """
        更新躲避狀態\n
        """
        if self.is_dodging:
            self.dodge_timer -= 1 / 60  # 假設60 FPS

            # 執行躲避移動
            dodge_speed = self.current_speed * self.dodge_speed_multiplier
            self.velocity_x = self.dodge_direction * dodge_speed

            # 結束躲避
            if self.dodge_timer <= 0:
                self.is_dodging = False
                self.dodge_direction = 0
                print(f"🛡️ 狙擊Boss躲避結束")

    def auto_heal(self):
        """
        自動回血機制\n
        """
        current_time = time.time()
        if current_time - self.last_heal_time >= self.heal_cooldown:
            if self.health < self.max_health:
                old_health = self.health
                self.health = min(self.max_health, self.health + self.heal_amount)
                if self.health > old_health:
                    print(f"💚 狙擊Boss回血：{old_health} → {self.health}")

            self.last_heal_time = current_time

    def update_jump_state(self):
        """
        更新跳躍震波攻擊狀態\n
        """
        if not self.is_jumping:
            return

        if self.jump_phase == "prepare":
            self.jump_timer -= 1 / 60
            if self.jump_timer <= 0:
                self.jump_phase = "jumping"

        elif self.jump_phase == "jumping":
            # 檢查是否落地
            if self.on_ground and self.velocity_y >= 0:
                self.jump_phase = "landing"
                # 產生震波
                self.create_shockwave()

        elif self.jump_phase == "landing":
            # 震波攻擊完成
            self.is_jumping = False
            self.jump_phase = "prepare"

    def attack_player(self, player):
        """
        狙擊Boss的綜合攻擊方式\n
        \n
        參數:\n
        player (Player): 目標玩家\n
        \n
        回傳:\n
        bool: True 表示攻擊成功\n
        """
        # 優先使用追蹤子彈
        if self.create_tracking_bullet(player.x, player.y):
            return True

        # 嘗試震波攻擊
        if self.perform_shockwave_attack(player):
            return True

        # 最後嘗試近戰攻擊
        return super().attack_player(player)

    def update_ai(self, player, platforms):
        """
        狙擊Boss的AI行為 - 更複雜的戰術行為\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        """
        if not self.is_alive:
            return

        # 檢測玩家
        player_detected = self.detect_player(player)

        # 計算與玩家的距離
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        # 更積極的攻擊邏輯
        if player_detected:
            # 優先考慮追蹤子彈攻擊
            current_time = time.time()
            if (
                current_time - self.last_tracking_bullet_time
                >= self.tracking_bullet_cooldown
            ):
                self.ai_state = "attack"
                self.create_tracking_bullet(player.x, player.y)

            # 如果距離合適，考慮震波攻擊
            elif (
                distance <= 300
                and current_time - self.last_shockwave_time >= self.shockwave_cooldown
            ):
                self.ai_state = "attack"
                self.perform_shockwave_attack(player)

            # 一般攻擊檢查
            elif self.can_attack_player(player):
                self.ai_state = "attack"
                self.attack_player(player)

            # 追擊玩家
            else:
                self.ai_state = "chase"
                self.move_towards_player(player)
        else:
            # 巡邏模式
            self.ai_state = "patrol"
            self.patrol_movement()

        # 保持與玩家的戰術距離（如果太近就後退）
        if distance < 80 and not self.is_jumping:
            retreat_direction = -1 if dx > 0 else 1
            self.velocity_x = retreat_direction * self.current_speed * 0.8

    def update(self, player, platforms, bullets=None):
        """
        狙擊Boss的更新方法\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        bullets (list): 玩家子彈列表（可選）\n
        """
        super().update(player, platforms)

        if self.is_alive:
            # 更新追蹤子彈
            self.update_tracking_bullets(player)

            # 檢查追蹤子彈碰撞
            self.check_tracking_bullet_collision(player)

            # 更新震波
            self.update_shockwaves(player)

            # 更新跳躍狀態
            self.update_jump_state()

            # 更新躲避狀態
            self.update_dodge_state()

            # 執行自動回血
            self.auto_heal()

            # 檢測子彈並躲避
            if bullets:
                self.detect_and_dodge_bullets(bullets)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製狙擊Boss和所有特效\n
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

        # 根據狀態改變Boss顏色（如果使用預設繪製）
        current_color = self.color
        if self.is_dodging:
            # 躲避時變成藍色
            current_color = CYAN
        elif self.is_jumping:
            # 跳躍時變成橙色
            current_color = ORANGE

        # 繪製Boss本體
        current_image = self.get_current_image()

        if current_image is not None:
            # 使用圖片繪製
            image_to_draw = current_image

            # 如果有特殊狀態，添加色彩效果
            if current_color != self.color:
                # 建立顏色覆蓋層
                color_overlay = pygame.Surface(
                    (self.width, self.height), pygame.SRCALPHA
                )
                color_overlay.fill((*current_color, 100))  # 半透明覆蓋

                # 複製原圖並疊加顏色
                image_to_draw = current_image.copy()
                image_to_draw.blit(
                    color_overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2
                )

            screen.blit(image_to_draw, (screen_x, screen_y))
        else:
            # 圖片載入失敗，使用矩形繪製
            boss_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
            pygame.draw.rect(screen, current_color, boss_rect)

        # 繪製Boss標記邊框
        boss_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, YELLOW, boss_rect, 4)

        # 繪製生命值條（更大的生命值條）
        bar_width = self.width + 20
        bar_height = 8
        bar_x = screen_x - 10
        bar_y = screen_y - bar_height - 15

        # 背景（紅色）
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, RED, bg_rect)

        # 當前生命值（綠色）
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
        pygame.draw.rect(screen, GREEN, health_rect)

        # 繪製"SNIPER BOSS"標籤
        font = get_chinese_font(FONT_SIZE_SMALL)
        boss_text = font.render("🎯 SNIPER BOSS", True, RED)
        text_rect = boss_text.get_rect()
        text_rect.centerx = screen_x + self.width // 2
        text_rect.bottom = bar_y - 5
        screen.blit(boss_text, text_rect)

        # 繪製追蹤子彈
        for bullet in self.tracking_bullets:
            bullet_screen_x = bullet["x"] - camera_x
            bullet_screen_y = bullet["y"] - camera_y
            # 只繪製在螢幕範圍內的追蹤子彈
            if (
                -20 <= bullet_screen_x <= SCREEN_WIDTH + 20
                and -20 <= bullet_screen_y <= SCREEN_HEIGHT + 20
            ):
                # 繪製追蹤子彈：紫色外圈和白色內圈
                pygame.draw.circle(
                    screen, PURPLE, (int(bullet_screen_x), int(bullet_screen_y)), 8
                )
                pygame.draw.circle(
                    screen, WHITE, (int(bullet_screen_x), int(bullet_screen_y)), 4
                )

        # 繪製震波
        for shockwave in self.shockwaves:
            shockwave_screen_x = shockwave["x"] - camera_x
            shockwave_screen_y = shockwave["y"] - camera_y

            # 只繪製在螢幕範圍內的震波
            if (
                -200 <= shockwave_screen_x <= SCREEN_WIDTH + 200
                and -200 <= shockwave_screen_y <= SCREEN_HEIGHT + 200
            ):
                # 繪製震波圓圈（透明效果用多層圓圈模擬）
                for i in range(3):
                    alpha_factor = 1.0 - (i * 0.3)
                    wave_color = tuple(int(c * alpha_factor) for c in YELLOW)
                    pygame.draw.circle(
                        screen,
                        wave_color,
                        (int(shockwave_screen_x), int(shockwave_screen_y)),
                        int(shockwave["radius"] - i * 5),
                        3,
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
