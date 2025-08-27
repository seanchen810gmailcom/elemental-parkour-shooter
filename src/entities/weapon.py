######################載入套件######################
import pygame
import math
import time

# 支援直接執行和模組執行兩種方式
try:
    from ..config import *
    from ..core.game_objects import GameObject
except ImportError:
    from src.config import *
    from src.core.game_objects import GameObject

######################子彈類別######################


class Bullet(GameObject):
    """
    子彈類別 - 處理各種屬性子彈的飛行和效果\n
    \n
    支援四種武器子彈：\n
    1. 機關槍 - 黑色圓形子彈\n
    2. 衝鋒槍 - 紫色矩形子彈\n
    3. 散彈槍 - 紅色三角形子彈\n
    4. 狙擊槍 - 紅色大圓形子彈\n
    5. 雷電必殺技 - 黃色追蹤子彈\n
    \n
    參數:\n
    x (float): 子彈初始 X 座標\n
    y (float): 子彈初始 Y 座標\n
    direction_x (float): X 方向的移動向量\n
    direction_y (float): Y 方向的移動向量\n
    bullet_type (str): 子彈屬性類型\n
    """

    def __init__(self, x, y, direction_x, direction_y, bullet_type):
        # 根據武器類型設定顏色
        weapon_colors = {
            "machine_gun": BLACK,  # 機關槍子彈改為黑色
            "assault_rifle": (128, 0, 128),  # 紫色
            "shotgun": (255, 0, 0),  # 紅色
            "sniper": (255, 0, 0),  # 狙擊槍子彈改為紅色
            "lightning_tracking": YELLOW,  # 雷電追蹤子彈為黃色
        }

        color = weapon_colors.get(bullet_type, WHITE)
        super().__init__(x, y, BULLET_SIZE, BULLET_SIZE, color)

        # 移動屬性
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = BULLET_SPEED

        # 子彈屬性
        self.bullet_type = bullet_type
        self.damage = self.get_base_damage()

        # 狀態管理
        self.is_active = True
        self.max_distance = 9999  # 讓子彈飛得超級遠，永遠不會因為距離而消失
        self.distance_traveled = 0

        # 記錄初始位置（用來計算飛行距離）
        self.start_x = x
        self.start_y = y

        # 新增武器類型支援
        self.weapon_type = bullet_type  # 武器類型：machine_gun, assault_rifle, shotgun, sniper, lightning_tracking

        # 雷電追蹤特殊屬性
        if bullet_type == "lightning_tracking":
            self.tracking_target = None  # 追蹤目標
            self.tracking_range = 300  # 追蹤範圍
            self.turn_speed = 5.0  # 轉向速度
            self.bullet_id = 0  # 子彈編號，用於目標分配

    def get_base_damage(self):
        """
        獲取子彈的基礎傷害值\n
        \n
        回傳:\n
        int: 根據武器類型回傳對應的基礎傷害\n
        """
        damage_values = {
            "machine_gun": 8,  # 機關槍：攻擊力降低
            "assault_rifle": 40,  # 衝鋒槍：攻擊力高
            "shotgun": 25,  # 散彈槍：攻擊力中等
            "sniper": 90,  # 狙擊槍：攻擊力降低10%（100->90）
            "lightning_tracking": 90,  # 雷電追蹤：與調整後的狙擊槍相同
        }
        return damage_values.get(self.bullet_type, 20)

    def update(self, targets=None):
        """
        更新子彈位置和狀態 - 每幀執行的移動邏輯\n
        \n
        參數:\n
        targets (list): 可能的追蹤目標列表（用於雷電追蹤）\n
        \n
        處理：\n
        1. 根據方向和速度移動子彈\n
        2. 計算飛行距離\n
        3. 檢查是否超出射程\n
        4. 雷電追蹤邏輯\n
        """
        if not self.is_active:
            return

        # 雷電追蹤邏輯
        if self.bullet_type == "lightning_tracking" and targets:
            self.update_tracking(targets)

        # 根據方向向量移動子彈
        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed

        # 計算已飛行的距離
        distance_x = self.x - self.start_x
        distance_y = self.y - self.start_y
        self.distance_traveled = math.sqrt(distance_x**2 + distance_y**2)

        # 檢查是否超出最大射程（已設為9999，基本不會觸發）
        if self.distance_traveled > self.max_distance:
            self.is_active = False

        # 更新碰撞矩形
        self.update_rect()

    def update_tracking(self, targets):
        """
        更新雷電追蹤邏輯 - 使用分配的目標進行追蹤\n
        \n
        參數:\n
        targets (list): 可能的追蹤目標列表\n
        """
        # 優先使用分配的目標
        target_to_track = None

        if hasattr(self, "assigned_target") and self.assigned_target:
            # 檢查分配的目標是否還在目標列表中（還活著）
            if self.assigned_target in targets:
                target_to_track = self.assigned_target

        # 如果沒有分配目標或分配目標已死亡，找最近的目標
        if not target_to_track and targets:
            closest_target = None
            closest_distance = float("inf")

            for target in targets:
                # 計算到目標的距離
                target_center_x = target.x + getattr(target, "width", 0) // 2
                target_center_y = target.y + getattr(target, "height", 0) // 2

                dx = target_center_x - self.x
                dy = target_center_y - self.y
                distance = math.sqrt(dx**2 + dy**2)

                # 在追蹤範圍內且是最近的目標
                if distance <= self.tracking_range and distance < closest_distance:
                    closest_target = target
                    closest_distance = distance

            target_to_track = closest_target

        # 如果找到目標，進行積極追蹤
        if target_to_track:
            self.tracking_target = target_to_track
            target_center_x = (
                target_to_track.x + getattr(target_to_track, "width", 0) // 2
            )
            target_center_y = (
                target_to_track.y + getattr(target_to_track, "height", 0) // 2
            )

            # 計算到目標的方向
            dx = target_center_x - self.x
            dy = target_center_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0:
                # 標準化目標方向
                target_dir_x = dx / distance
                target_dir_y = dy / distance

                # 計算強烈的轉向 - 直接設定方向而不是漸進式轉向
                turn_intensity = 0.8  # 高轉向強度，讓子彈快速調整方向

                # 如果距離很近，直接指向目標
                if distance < 80:
                    self.direction_x = target_dir_x
                    self.direction_y = target_dir_y
                else:
                    # 距離較遠時使用快速轉向
                    self.direction_x += (
                        target_dir_x - self.direction_x
                    ) * turn_intensity
                    self.direction_y += (
                        target_dir_y - self.direction_y
                    ) * turn_intensity

                # 重新標準化方向向量，保持速度一致
                current_length = math.sqrt(self.direction_x**2 + self.direction_y**2)
                if current_length > 0:
                    self.direction_x /= current_length
                    self.direction_y /= current_length

    def get_damage_against_target(self, target_type):
        """
        計算對特定目標的傷害值 - 簡化版本，不使用元素系統\n
        \n
        參數:\n
        target_type (str): 目標怪物類型\n
        \n
        回傳:\n
        tuple: (damage, status_effect_info)\n
        """
        # 直接返回基礎傷害，不考慮元素剋制
        final_damage = self.damage

        # 不使用狀態效果
        status_effect = None

        return final_damage, status_effect

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製子彈 - 根據武器類型使用不同視覺效果\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        繪製方式：\n
        - 機關槍：小圓形\n
        - 衝鋒槍：矩形\n
        - 散彈槍：三角形\n
        - 狙擊槍：大圓形\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if not self.is_active:
            return

        center_x = int(screen_x + self.width // 2)
        center_y = int(screen_y + self.height // 2)
        radius = self.width // 2

        if self.bullet_type == "machine_gun":
            # 機關槍：小圓形
            pygame.draw.circle(screen, self.color, (center_x, center_y), radius // 2)

        elif self.bullet_type == "assault_rifle":
            # 衝鋒槍：矩形
            bullet_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
            pygame.draw.rect(screen, self.color, bullet_rect)

        elif self.bullet_type == "shotgun":
            # 散彈槍：三角形
            points = [
                (center_x, center_y - radius),  # 頂點
                (center_x - radius, center_y + radius),  # 左下
                (center_x + radius, center_y + radius),  # 右下
            ]
            pygame.draw.polygon(screen, self.color, points)

        elif self.bullet_type == "sniper":
            # 狙擊槍：大圓形，紅色
            pygame.draw.circle(screen, self.color, (center_x, center_y), radius)
            # 內圈顯示威力
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius // 2)

        elif self.bullet_type == "lightning_tracking":
            # 雷電追蹤：簡潔的黃色閃電效果，無追蹤線
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius)
            # 繪製閃電效果
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius // 2)
            # 額外的電光效果
            for i in range(4):
                angle = (i * math.pi / 2) + (time.time() * 5)  # 旋轉的電光
                end_x = center_x + math.cos(angle) * radius * 1.5
                end_y = center_y + math.sin(angle) * radius * 1.5
                pygame.draw.line(
                    screen, YELLOW, (center_x, center_y), (int(end_x), int(end_y)), 1
                )


######################武器管理器類別######################


class WeaponManager:
    """
    武器管理器 - 統一管理所有子彈和攻擊行為\n
    \n
    負責：\n
    1. 子彈的生成和銷毀\n
    2. 子彈與目標的碰撞檢測\n
    3. 近戰攻擊的處理\n
    4. 武器系統的整體更新\n
    """

    def __init__(self):
        self.bullets = []  # 所有活躍的子彈列表
        self.lightning_bullets = []  # 雷電追蹤子彈列表

    def create_bullet(self, bullet_info):
        """
        根據玩家射擊資訊建立新子彈\n
        \n
        參數:\n
        bullet_info (list or dict): 包含子彈資訊的字典或列表\n
        \n
        回傳:\n
        list: 新建立的子彈物件列表\n
        """
        if bullet_info is None:
            return []

        new_bullets = []

        # 處理多發子彈的情況（散彈槍）
        if isinstance(bullet_info, list):
            for info in bullet_info:
                bullet = self._create_single_bullet(info)
                if bullet:
                    new_bullets.append(bullet)
        else:
            # 單發子彈
            bullet = self._create_single_bullet(bullet_info)
            if bullet:
                new_bullets.append(bullet)

        self.bullets.extend(new_bullets)
        return new_bullets

    def create_ultimate(self, ultimate_info, targets=None):
        """
        根據玩家必殺技資訊建立雷電追蹤子彈 - 智能目標分配\n
        \n
        策略:\n
        - 多怪物(>=2): 5顆子彈分散攻擊不同怪物\n
        - 單怪物(1): 5顆子彈集中攻擊同一怪物\n
        - 無怪物(0): 子彈朝預設方向發射\n
        \n
        參數:\n
        ultimate_info (list): 包含五顆必殺技子彈資訊的列表\n
        targets (list): 當前可攻擊的目標列表\n
        \n
        回傳:\n
        list: 新建立的雷電子彈物件列表\n
        """
        if ultimate_info is None:
            return []

        new_lightning_bullets = []

        # 處理五顆子彈的情況
        if isinstance(ultimate_info, list):
            # 扇型發射角度設定
            fan_angle = math.pi / 3  # 60度扇形角度
            start_angle = -fan_angle / 2  # 從-30度開始
            angle_step = fan_angle / 4  # 每顆子彈間隔15度

            for i, info in enumerate(ultimate_info):
                # 計算扇型發射的初始方向
                bullet_angle = start_angle + (i * angle_step)
                initial_direction_x = math.cos(bullet_angle)
                initial_direction_y = math.sin(bullet_angle)

                lightning_bullet = Bullet(
                    info["start_x"],
                    info["start_y"],
                    initial_direction_x,
                    initial_direction_y,
                    info["type"],
                )

                # 設定必殺技特定屬性
                lightning_bullet.damage = info["damage"]
                lightning_bullet.speed = info["speed"]
                lightning_bullet.bullet_id = info.get("bullet_id", 0)

                # 立即分配追蹤目標
                if targets:
                    if len(targets) == 1:
                        # 單怪物：所有子彈都追蹤同一目標
                        lightning_bullet.assigned_target = targets[0]
                    else:
                        # 多怪物：循環分配不同目標
                        target_index = i % len(targets)
                        lightning_bullet.assigned_target = targets[target_index]
                else:
                    lightning_bullet.assigned_target = None

                new_lightning_bullets.append(lightning_bullet)
        else:
            # 兼容舊的單發格式
            lightning_bullet = Bullet(
                ultimate_info["start_x"],
                ultimate_info["start_y"],
                1,  # 初始方向，之後會被追蹤邏輯覆蓋
                0,
                ultimate_info["type"],
            )

            # 設定必殺技特定屬性
            lightning_bullet.damage = ultimate_info["damage"]
            lightning_bullet.speed = ultimate_info["speed"]

            new_lightning_bullets.append(lightning_bullet)

        # 將新子彈加入列表
        self.lightning_bullets.extend(new_lightning_bullets)
        self.bullets.extend(new_lightning_bullets)  # 也加入一般子彈列表進行碰撞檢測

        return new_lightning_bullets

    def _create_single_bullet(self, info):
        """
        創建單發子彈\n
        \n
        參數:\n
        info (dict): 子彈資訊\n
        \n
        回傳:\n
        Bullet: 子彈物件\n
        """
        bullet = Bullet(
            info["start_x"],
            info["start_y"],
            info["direction_x"],
            info["direction_y"],
            info["type"],
        )

        # 設定武器特定屬性
        if "damage" in info:
            bullet.damage = info["damage"]
        if "speed" in info:
            bullet.speed = info["speed"]

        return bullet

    def handle_melee_attack(self, melee_info, targets):
        """
        處理近戰攻擊 - 檢查攻擊範圍內的目標\n
        \n
        參數:\n
        melee_info (dict): 近戰攻擊資訊\n
        targets (list): 可能被攻擊的目標列表\n
        \n
        回傳:\n
        list: 被擊中的目標列表\n
        """
        if melee_info is None:
            return []

        hit_targets = []
        attack_rect = melee_info["attack_rect"]

        for target in targets:
            if hasattr(target, "rect") and attack_rect.colliderect(target.rect):
                # 目標被近戰攻擊擊中
                damage = melee_info["damage"]
                knockback = melee_info["knockback"]
                direction = melee_info["direction"]

                # 對目標造成傷害
                if hasattr(target, "take_damage"):
                    target.take_damage(damage)

                # 對目標施加擊退效果
                if hasattr(target, "apply_knockback"):
                    target.apply_knockback(knockback, direction)

                hit_targets.append(target)

        return hit_targets

    def update_bullets(self, targets=None):
        """
        更新所有子彈的狀態 - 移除非活躍的子彈\n
        \n
        參數:\n
        targets (list): 可能的追蹤目標列表（用於雷電追蹤）\n
        """
        # 更新每顆子彈
        for bullet in self.bullets:
            bullet.update(targets)

        # 移除非活躍的子彈
        self.bullets = [bullet for bullet in self.bullets if bullet.is_active]
        self.lightning_bullets = [
            bullet for bullet in self.lightning_bullets if bullet.is_active
        ]

    def check_bullet_collisions(self, targets):
        """
        檢查子彈與目標的碰撞 - 處理命中效果\n
        \n
        參數:\n
        targets (list): 可能被子彈擊中的目標列表\n
        \n
        回傳:\n
        list: 發生碰撞的資訊列表\n
        """
        collision_results = []
        bullets_to_remove = []

        for bullet in self.bullets:
            if not bullet.is_active:
                continue

            for target in targets:
                if hasattr(target, "rect") and bullet.rect.colliderect(target.rect):
                    # 子彈擊中目標

                    # 計算傷害（考慮屬性剋制）
                    target_type = getattr(target, "monster_type", "unknown")
                    damage, status_effect = bullet.get_damage_against_target(
                        target_type
                    )

                    # 對目標造成傷害
                    if hasattr(target, "take_damage"):
                        target.take_damage(damage)

                    # 施加狀態效果
                    if status_effect and hasattr(target, "add_status_effect"):
                        target.add_status_effect(
                            status_effect["type"],
                            status_effect["duration"],
                            status_effect["intensity"],
                        )

                    # 記錄碰撞結果
                    collision_info = {
                        "bullet": bullet,
                        "target": target,
                        "damage": damage,
                        "status_effect": status_effect,
                    }
                    collision_results.append(collision_info)

                    # 標記子彈為待移除
                    bullets_to_remove.append(bullet)
                    break  # 子彈只能擊中一個目標

        # 移除擊中目標的子彈
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                bullet.is_active = False

        return collision_results

    def update(self, targets=None):
        """
        武器系統的主要更新方法\n
        \n
        參數:\n
        targets (list): 可能的攻擊目標列表\n
        \n
        回傳:\n
        list: 所有碰撞結果\n
        """
        # 更新所有子彈
        self.update_bullets(targets)

        # 檢查子彈碰撞
        collision_results = []
        if targets:
            collision_results = self.check_bullet_collisions(targets)

        return collision_results

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有武器相關元素\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 繪製所有活躍的子彈
        for bullet in self.bullets:
            bullet.draw(screen, camera_x, camera_y)

    def get_bullet_count(self):
        """
        獲取當前活躍子彈數量 - 用於性能監控\n
        \n
        回傳:\n
        int: 活躍子彈數量\n
        """
        return len([bullet for bullet in self.bullets if bullet.is_active])

    def clear_all_bullets(self):
        """
        清除所有子彈 - 用於關卡重置或遊戲結束\n
        """
        self.bullets.clear()
