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
        4. 雷電追蹤邏輯（分階段執行）\n
        """
        if not self.is_active:
            return

        # 雷電追蹤的階段性邏輯
        if self.bullet_type == "lightning_tracking":
            self.update_lightning_phases(targets)
        # 一般子彈的追蹤邏輯（保持原有功能）
        elif self.bullet_type == "lightning_tracking" and targets:
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

    def update_lightning_phases(self, targets):
        """
        更新雷電子彈的階段性行為\n
        \n
        階段1：往上飛行到指定高度\n
        階段2：追蹤分配的目標往下衝\n
        \n
        參數:\n
        targets (list): 可能的追蹤目標列表\n
        """
        if not hasattr(self, "phase"):
            # 如果沒有階段屬性，初始化為追蹤模式（兼容舊子彈）
            self.phase = "tracking"

        if self.phase == "ascending":
            # 階段1：往上飛行
            # 計算已上升的距離
            self.ascent_distance += self.speed

            # 檢查是否達到最大上升高度
            if self.ascent_distance >= self.max_ascent:
                # 切換到追蹤階段
                self.phase = "tracking"
                # 增加下降時的速度，讓攻擊更有衝擊感
                self.speed = self.original_speed * 1.5

        elif self.phase == "tracking":
            # 階段2：追蹤目標
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
                    turn_intensity = 0.9  # 提高轉向強度，讓追蹤更精準

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
                    current_length = math.sqrt(
                        self.direction_x**2 + self.direction_y**2
                    )
                    if current_length > 0:
                        self.direction_x /= current_length
                        self.direction_y /= current_length

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


######################爆炸效果類別######################


class ExplosionEffect:
    """
    爆炸視覺效果 - 展示手榴彈爆炸的視覺回饋\n
    \n
    特效包含：\n
    1. 多層同心圓爆炸波\n
    2. 顏色漸變從黃到紅\n
    3. 半秒鐘的動畫效果\n
    \n
    參數:\n
    x (float): 爆炸中心 X 座標\n
    y (float): 爆炸中心 Y 座標\n
    max_radius (float): 最大爆炸半徑\n
    """

    def __init__(self, x, y, max_radius):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.start_time = time.time()
        self.duration = EXPLOSION_DURATION
        self.is_active = True

    def update(self):
        """更新爆炸效果狀態"""
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.is_active = False

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製爆炸效果\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        if not self.is_active:
            return

        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration

        # 計算螢幕座標
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 爆炸波效果 - 從中心向外擴散
        for i, color in enumerate(EXPLOSION_COLORS):
            # 每層波的半徑隨時間增長
            wave_progress = min(1.0, progress + i * 0.1)
            current_radius = int(self.max_radius * wave_progress)

            # 透明度隨時間遞減
            alpha = max(0, 255 * (1 - progress))

            if current_radius > 0 and alpha > 0:
                # 創建帶透明度的表面
                surface = pygame.Surface(
                    (current_radius * 2, current_radius * 2), pygame.SRCALPHA
                )
                color_with_alpha = (*color, int(alpha))

                # 繪製爆炸圓圈
                pygame.draw.circle(
                    surface,
                    color_with_alpha,
                    (current_radius, current_radius),
                    current_radius,
                    max(1, current_radius // 10),  # 線條粗細
                )

                # 將表面貼到螢幕上
                screen.blit(
                    surface, (screen_x - current_radius, screen_y - current_radius)
                )


######################手榴彈類別######################


class Grenade(GameObject):
    """
    手榴彈類別 - 具備黏附能力的爆炸武器\n
    \n
    特殊功能：\n
    1. 拋物線飛行，可黏附在任何物體上\n
    2. 使用狙擊槍準心進行精確瞄準\n
    3. 右鍵引爆，範圍傷害200點\n
    4. 玩家最多只能有5顆\n
    \n
    參數:\n
    x (float): 手榴彈初始 X 座標\n
    y (float): 手榴彈初始 Y 座標\n
    direction_x (float): X 方向的投擲向量\n
    direction_y (float): Y 方向的投擲向量\n
    """

    def __init__(self, x, y, direction_x, direction_y):
        super().__init__(x, y, GRENADE_SIZE, GRENADE_SIZE, GRENADE_COLOR)

        # 移動屬性
        self.velocity_x = direction_x * GRENADE_SPEED
        self.velocity_y = direction_y * GRENADE_SPEED

        # 手榴彈狀態
        self.is_active = True
        self.is_attached = False  # 是否已黏附到物體
        self.attached_to = None  # 黏附的目標物件
        self.attached_offset_x = 0  # 相對於黏附物件的偏移
        self.attached_offset_y = 0

        # 爆炸屬性
        self.damage = GRENADE_DAMAGE
        self.explosion_radius = GRENADE_EXPLOSION_RADIUS

        # 記錄初始位置（用於調試）
        self.start_x = x
        self.start_y = y

    def update(self, platforms=None, targets=None, level_width=None, level_height=None):
        """
        更新手榴彈位置和狀態\n
        \n
        參數:\n
        platforms (list): 平台列表，用於碰撞檢測\n
        targets (list): 目標列表（怪物等），用於黏附檢測\n
        level_width (int): 關卡世界寬度\n
        level_height (int): 關卡世界高度\n
        \n
        處理：\n
        1. 如果已黏附，跟隨黏附物件移動\n
        2. 如果未黏附，按照物理規律飛行\n
        3. 檢測與各種物體的碰撞黏附\n
        """
        if not self.is_active:
            return

        if self.is_attached:
            # 如果已黏附，跟隨黏附的物件移動
            if self.attached_to:
                self.x = self.attached_to.x + self.attached_offset_x
                self.y = self.attached_to.y + self.attached_offset_y
        else:
            # 如果未黏附，繼續飛行
            # 套用重力
            self.velocity_y += GRENADE_GRAVITY

            # 更新位置
            self.x += self.velocity_x
            self.y += self.velocity_y

            # 檢查是否碰撞並黏附
            self.check_attachment(platforms, targets, level_width, level_height)

        # 更新碰撞矩形
        self.update_rect()

    def check_attachment(
        self, platforms=None, targets=None, level_width=None, level_height=None
    ):
        """
        檢查手榴彈是否應該黏附到物體上\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        targets (list): 目標列表（怪物等）\n
        level_width (int): 關卡世界寬度\n
        level_height (int): 關卡世界高度\n
        \n
        黏附優先順序：\n
        1. 怪物和Boss\n
        2. 平台和牆壁\n
        3. 其他遊戲物件\n
        """
        if self.is_attached:
            return

        # 優先黏附到怪物身上
        if targets:
            for target in targets:
                if hasattr(target, "rect") and self.rect.colliderect(target.rect):
                    self.attach_to_object(target)
                    return

        # 其次黏附到平台上
        if platforms:
            for platform in platforms:
                if hasattr(platform, "rect") and self.rect.colliderect(platform.rect):
                    self.attach_to_object(platform)
                    return

        # 檢查是否碰到世界邊界（使用關卡尺寸而非螢幕尺寸）
        if level_width and level_height:
            if self.x <= 0 or self.x >= level_width - self.width:
                self.attach_to_wall(level_width)
            elif self.y >= level_height - self.height:
                self.attach_to_ground(level_height)

    def attach_to_object(self, target_object):
        """
        將手榴彈黏附到指定物件上\n
        \n
        參數:\n
        target_object: 要黏附的目標物件\n
        """
        self.is_attached = True
        self.attached_to = target_object

        # 計算相對於目標物件的偏移量
        self.attached_offset_x = self.x - target_object.x
        self.attached_offset_y = self.y - target_object.y

        # 停止移動
        self.velocity_x = 0
        self.velocity_y = 0

    def attach_to_wall(self, level_width=None):
        """
        將手榴彈黏附到牆壁上\n
        \n
        參數:\n
        level_width (int): 關卡世界寬度\n
        """
        self.is_attached = True
        self.attached_to = None  # 牆壁沒有物件
        self.velocity_x = 0
        self.velocity_y = 0

        # 確保不超出世界邊界
        if level_width:
            if self.x <= 0:
                self.x = 0
            elif self.x >= level_width - self.width:
                self.x = level_width - self.width

    def attach_to_ground(self, level_height=None):
        """
        將手榴彈黏附到地面上\n
        \n
        參數:\n
        level_height (int): 關卡世界高度\n
        """
        self.is_attached = True
        self.attached_to = None  # 地面沒有物件
        if level_height:
            self.y = level_height - self.height
        self.velocity_x = 0
        self.velocity_y = 0

    def explode(self, all_targets):
        """
        引爆手榴彈，對範圍內所有目標造成傷害\n
        \n
        參數:\n
        all_targets (list): 所有可能受到傷害的目標列表（包括玩家）\n
        \n
        回傳:\n
        list: 受到傷害的目標資訊列表\n
        """
        if not self.is_active:
            return []

        explosion_results = []

        # 計算爆炸中心點
        explosion_x = self.x + self.width // 2
        explosion_y = self.y + self.height // 2

        # 檢查範圍內的所有目標
        for target in all_targets:
            if hasattr(target, "x") and hasattr(target, "y"):
                # 計算目標中心點
                target_x = target.x + getattr(target, "width", 0) // 2
                target_y = target.y + getattr(target, "height", 0) // 2

                # 計算距離
                distance = math.sqrt(
                    (target_x - explosion_x) ** 2 + (target_y - explosion_y) ** 2
                )

                # 如果在爆炸範圍內
                if distance <= self.explosion_radius:
                    explosion_results.append(
                        {
                            "target": target,
                            "damage": self.damage,
                            "explosion_x": explosion_x,
                            "explosion_y": explosion_y,
                            "distance": distance,
                        }
                    )

        # 引爆後手榴彈失效
        self.is_active = False

        return explosion_results

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製手榴彈\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        if not self.is_active:
            return

        # 計算螢幕座標
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 只有在螢幕範圍內才繪製
        if (
            screen_x < -self.width
            or screen_x > SCREEN_WIDTH
            or screen_y < -self.height
            or screen_y > SCREEN_HEIGHT
        ):
            return

        center_x = int(screen_x + self.width // 2)
        center_y = int(screen_y + self.height // 2)
        radius = self.width // 2

        # 繪製手榴彈本體（深綠色圓形）
        pygame.draw.circle(screen, self.color, (center_x, center_y), radius)

        # 如果已黏附，繪製黏附狀態指示器
        if self.is_attached:
            # 繪製橘色邊框表示已黏附
            pygame.draw.circle(screen, ORANGE, (center_x, center_y), radius + 2, 2)
            # 繪製白色中心點
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius // 3)
        else:
            # 飛行中，繪製軌跡效果
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius // 2)


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
    5. 手榴彈系統的管理\n
    """

    def __init__(self):
        self.bullets = []  # 所有活躍的子彈列表
        self.lightning_bullets = []  # 雷電追蹤子彈列表
        self.grenades = []  # 所有活躍的手榴彈列表
        self.grenade_count = GRENADE_MAX_COUNT  # 玩家剩餘手榴彈數量
        self.explosion_effects = []  # 爆炸視覺效果列表
        
        # hack 模式 - 作弊功能開關
        self.hack_mode = False

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
        根據玩家必殺技資訊建立雷電追蹤子彈 - 先往上扇形發射，再追蹤目標\n
        \n
        策略:\n
        - 階段1：5顆子彈以扇形往上飛行（角度向上傾斜45-135度）\n
        - 階段2：到達高點後智能分配不同怪物進行追蹤攻擊\n
        - 多怪物(>=2): 分散攻擊不同怪物\n
        - 單怪物(1): 集中攻擊同一怪物\n
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
            # 扇型往上發射角度設定（從左上45度到右上135度）
            fan_angle = math.pi / 2  # 90度扇形角度，往上發射
            start_angle = math.pi / 4  # 從45度開始（左上）
            angle_step = fan_angle / 4  # 每顆子彈間隔22.5度

            for i, info in enumerate(ultimate_info):
                # 計算扇型往上發射的初始方向
                bullet_angle = start_angle + (i * angle_step)
                initial_direction_x = math.cos(bullet_angle)
                initial_direction_y = -math.sin(bullet_angle)  # 負號表示往上

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

                # 新增階段控制屬性
                lightning_bullet.phase = "ascending"  # 初始階段：往上飛行
                lightning_bullet.ascent_distance = 0  # 已上升距離
                lightning_bullet.max_ascent = 200  # 最大上升距離
                lightning_bullet.original_speed = info["speed"]  # 保存原始速度

                # 智能目標分配策略 - 優先攻擊Boss
                if targets:
                    # 分離Boss和普通怪物
                    boss_targets = [
                        target
                        for target in targets
                        if hasattr(target, "is_boss") and target.is_boss
                    ]
                    regular_targets = [
                        target
                        for target in targets
                        if not (hasattr(target, "is_boss") and target.is_boss)
                    ]

                    if boss_targets:
                        # 有Boss時：所有子彈都攻擊Boss，忽略小怪
                        # 如果有多個Boss（理論上不會發生），優先攻擊第一個
                        lightning_bullet.assigned_target = boss_targets[0]
                        if i == 0:  # 只在第一顆子彈時顯示訊息
                            print(
                                f"⚡ 必殺技鎖定Boss目標：{boss_targets[0].monster_type}"
                            )
                    elif regular_targets:
                        # 沒有Boss時：攻擊普通怪物
                        if len(regular_targets) == 1:
                            # 單怪物：所有子彈都追蹤同一目標
                            lightning_bullet.assigned_target = regular_targets[0]
                        else:
                            # 多怪物：優先確保每個怪物至少被一顆子彈攻擊
                            target_index = i % len(regular_targets)
                            lightning_bullet.assigned_target = regular_targets[
                                target_index
                            ]
                            # 記錄這個目標已被分配
                            if not hasattr(
                                regular_targets[target_index], "assigned_bullet_count"
                            ):
                                regular_targets[target_index].assigned_bullet_count = 0
                            regular_targets[target_index].assigned_bullet_count += 1

                        if i == 0:  # 只在第一顆子彈時顯示訊息
                            print(
                                f"⚡ 必殺技攻擊普通怪物：{len(regular_targets)}個目標"
                            )
                    else:
                        lightning_bullet.assigned_target = None
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

    def create_grenade(self, grenade_info):
        """
        創建新手榴彈 - 檢查數量限制\n
        \n
        參數:\n
        grenade_info (dict): 手榴彈資訊，包含起始位置和投擲方向\n
        \n
        回傳:\n
        bool: 是否成功創建手榴彈\n
        """
        # hack 模式下忽略手榴彈數量限制
        if grenade_info is None or (not self.hack_mode and self.grenade_count <= 0):
            return False

        # 創建新手榴彈
        grenade = Grenade(
            grenade_info["start_x"],
            grenade_info["start_y"],
            grenade_info["direction_x"],
            grenade_info["direction_y"],
        )

        self.grenades.append(grenade)
        
        # hack 模式下不消耗手榴彈
        if not self.hack_mode:
            self.grenade_count -= 1  # 減少可用手榴彈數量

        return True

    def explode_all_grenades(self, all_targets):
        """
        引爆所有活躍的手榴彈 - 右鍵觸發\n
        \n
        參數:\n
        all_targets (list): 所有可能受到傷害的目標列表（包括玩家和怪物）\n
        \n
        回傳:\n
        list: 所有爆炸造成的傷害結果\n
        """
        all_explosion_results = []

        for grenade in self.grenades[:]:  # 使用切片避免在迭代中修改列表
            if grenade.is_active:
                explosion_results = grenade.explode(all_targets)
                all_explosion_results.extend(explosion_results)

                # 創建爆炸視覺效果
                explosion_effect = ExplosionEffect(
                    grenade.x + grenade.width // 2,  # 爆炸中心 X
                    grenade.y + grenade.height // 2,  # 爆炸中心 Y
                    GRENADE_EXPLOSION_RADIUS,  # 最大爆炸半徑
                )
                self.explosion_effects.append(explosion_effect)

        # 移除已爆炸的手榴彈
        self.grenades = [grenade for grenade in self.grenades if grenade.is_active]

        return all_explosion_results

    def update_grenades(
        self, platforms=None, targets=None, level_width=None, level_height=None
    ):
        """
        更新所有手榴彈的狀態\n
        \n
        參數:\n
        platforms (list): 平台列表，用於碰撞檢測\n
        targets (list): 目標列表（怪物等），用於黏附檢測\n
        level_width (int): 關卡世界寬度\n
        level_height (int): 關卡世界高度\n
        """
        for grenade in self.grenades:
            grenade.update(platforms, targets, level_width, level_height)

        # 移除非活躍的手榴彈
        self.grenades = [grenade for grenade in self.grenades if grenade.is_active]

    def get_grenade_count(self):
        """
        獲取玩家剩餘手榴彈數量\n
        \n
        回傳:\n
        int: 剩餘手榴彈數量\n
        """
        return self.grenade_count

    def get_active_grenades_count(self):
        """
        獲取當前場上活躍手榴彈數量\n
        \n
        回傳:\n
        int: 場上手榴彈數量\n
        """
        return len([grenade for grenade in self.grenades if grenade.is_active])

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

    def update(self, targets=None, platforms=None, level_width=None, level_height=None):
        """
        武器系統的主要更新方法\n
        \n
        參數:\n
        targets (list): 可能的攻擊目標列表\n
        platforms (list): 平台列表，用於手榴彈碰撞檢測\n
        level_width (int): 關卡世界寬度\n
        level_height (int): 關卡世界高度\n
        \n
        回傳:\n
        list: 所有碰撞結果\n
        """
        # 更新所有子彈
        self.update_bullets(targets)

        # 更新所有手榴彈
        self.update_grenades(platforms, targets, level_width, level_height)

        # 更新爆炸效果
        for effect in self.explosion_effects[:]:
            effect.update()
            if not effect.is_active:
                self.explosion_effects.remove(effect)

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

        # 繪製所有活躍的手榴彈
        for grenade in self.grenades:
            grenade.draw(screen, camera_x, camera_y)

        # 繪製所有爆炸效果
        for effect in self.explosion_effects:
            effect.draw(screen, camera_x, camera_y)

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
        清除所有子彈和手榴彈 - 用於關卡重置或遊戲結束\n
        """
        self.bullets.clear()
        self.grenades.clear()
        self.explosion_effects.clear()

    def reset_grenades(self):
        """
        重置手榴彈系統 - 補充滿手榴彈數量\n
        """
        self.grenade_count = GRENADE_MAX_COUNT
        self.grenades.clear()
        self.explosion_effects.clear()
