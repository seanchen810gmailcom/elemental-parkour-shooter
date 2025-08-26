######################載入套件######################
import pygame
import random
import math
from config import *
from game_objects import *

######################場景物件類別######################


class Hazard(GameObject):
    """
    環境陷阱基礎類別\n
    \n
    所有陷阱的共通功能：\n
    1. 對玩家造成傷害\n
    2. 具有特殊的視覺效果\n
    3. 可能具有動畫或移動\n
    \n
    屬性:\n
    damage (int): 陷阱造成的傷害值\n
    hazard_type (str): 陷阱類型（'lava', 'water', 'wind'）\n
    active (bool): 陷阱是否啟動\n
    """

    def __init__(self, x, y, width, height, damage, hazard_type):
        """
        初始化陷阱物件\n
        \n
        參數:\n
        x (int): 陷阱的 x 座標\n
        y (int): 陷阱的 y 座標\n
        width (int): 陷阱寬度\n
        height (int): 陷阱高度\n
        damage (int): 造成的傷害值，範圍 1-50\n
        hazard_type (str): 陷阱類型，可選 'lava', 'water', 'wind'\n
        """
        # 根據陷阱類型設定顏色
        if hazard_type == "lava":
            color = LAVA_COLOR
        elif hazard_type == "water":
            color = WATER_COLOR
        elif hazard_type == "wind":
            color = WIND_COLOR
        else:
            color = GRAY

        super().__init__(x, y, width, height, color)
        self.damage = damage
        self.hazard_type = hazard_type
        self.active = True
        self.animation_timer = 0  # 用於動畫效果

    def update(self, dt):
        """
        更新陷阱狀態和動畫\n
        \n
        參數:\n
        dt (float): 時間間隔，用於動畫計算\n
        """
        # 更新動畫計時器
        self.animation_timer += dt

    def check_collision(self, player):
        """
        檢查玩家是否碰到陷阱\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: 是否發生碰撞\n
        """
        if not self.active:
            return False

        # 檢查玩家矩形是否與陷阱重疊
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        hazard_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        return player_rect.colliderect(hazard_rect)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製陷阱（由子類別實作具體外觀）\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        pass  # 由子類別實作


class LavaPool(Hazard):
    """
    熔岩池陷阱 - 火山場景的主要陷阱\n
    \n
    特色:\n
    1. 持續造成火焰傷害\n
    2. 有冒泡動畫效果\n
    3. 發出橘紅色光芒\n
    """

    def __init__(self, x, y, width, height):
        """
        建立熔岩池陷阱\n
        \n
        參數:\n
        x, y (int): 位置座標\n
        width, height (int): 熔岩池大小\n
        """
        super().__init__(x, y, width, height, damage=15, hazard_type="lava")
        self.bubble_positions = []  # 泡泡位置列表
        self.generate_bubbles()

    def generate_bubbles(self):
        """
        產生隨機的泡泡位置用於動畫效果\n
        """
        # 清除舊泡泡
        self.bubble_positions = []

        # 在熔岩池範圍內隨機產生5-10個泡泡
        bubble_count = random.randint(5, 10)
        for _ in range(bubble_count):
            bubble_x = random.randint(int(self.x), int(self.x + self.width))
            bubble_y = random.randint(int(self.y), int(self.y + self.height))
            bubble_size = random.randint(3, 8)
            self.bubble_positions.append([bubble_x, bubble_y, bubble_size])

    def update(self, dt):
        """
        更新熔岩池的冒泡動畫\n
        """
        super().update(dt)

        # 每隔一段時間重新產生泡泡
        if self.animation_timer > 2.0:  # 2秒重新產生
            self.generate_bubbles()
            self.animation_timer = 0

        # 讓泡泡緩慢移動
        for bubble in self.bubble_positions:
            bubble[1] -= 10 * dt  # 泡泡往上移動
            # 如果泡泡移出熔岩池，重新定位到底部
            if bubble[1] < self.y:
                bubble[1] = self.y + self.height

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製熔岩池和冒泡效果\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 畫熔岩池主體（深紅色）
        lava_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(screen, LAVA_COLOR, lava_rect)

        # 畫熔岩池邊緣（更深的紅色）
        pygame.draw.rect(screen, (150, 0, 0), lava_rect, 3)

        # 畫冒泡效果
        for bubble in self.bubble_positions:
            bubble_screen_x = bubble[0] - camera_x
            bubble_screen_y = bubble[1] - camera_y
            # 只畫在螢幕範圍內的泡泡
            if (
                0 <= bubble_screen_x <= SCREEN_WIDTH
                and 0 <= bubble_screen_y <= SCREEN_HEIGHT
            ):
                # 泡泡用亮橘色
                pygame.draw.circle(
                    screen,
                    (255, 150, 0),
                    (int(bubble_screen_x), int(bubble_screen_y)),
                    bubble[2],
                )


class WaterCurrent(Hazard):
    """
    水流陷阱 - 海底場景的主要陷阱\n
    \n
    特色:\n
    1. 會推動玩家移動\n
    2. 造成窒息傷害\n
    3. 有流動動畫效果\n
    """

    def __init__(self, x, y, width, height, flow_direction):
        """
        建立水流陷阱\n
        \n
        參數:\n
        x, y (int): 位置座標\n
        width, height (int): 水流區域大小\n
        flow_direction (tuple): 水流方向 (x_dir, y_dir)，範圍 -1 到 1\n
        """
        super().__init__(x, y, width, height, damage=8, hazard_type="water")
        self.flow_direction = flow_direction
        self.flow_strength = 150  # 水流推力強度
        self.wave_lines = []  # 波浪線條用於動畫
        self.generate_wave_lines()

    def generate_wave_lines(self):
        """
        產生波浪線條用於表現水流效果\n
        """
        self.wave_lines = []

        # 產生水平波浪線
        for i in range(0, int(self.height), 20):
            line_y = self.y + i
            wave_points = []
            for x in range(int(self.x), int(self.x + self.width), 10):
                # 使用正弦波產生波浪效果
                wave_offset = (
                    math.sin((x - self.x) * 0.1 + self.animation_timer * 3) * 5
                )
                wave_points.append((x, line_y + wave_offset))
            self.wave_lines.append(wave_points)

    def update(self, dt):
        """
        更新水流動畫效果\n
        """
        super().update(dt)
        # 重新產生波浪線條來製造流動效果
        self.generate_wave_lines()

    def apply_force_to_player(self, player, dt):
        """
        對玩家施加水流推力\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        dt (float): 時間間隔\n
        """
        if self.check_collision(player):
            # 計算推力
            push_x = self.flow_direction[0] * self.flow_strength * dt
            push_y = self.flow_direction[1] * self.flow_strength * dt

            # 應用推力到玩家速度
            player.velocity_x += push_x
            player.velocity_y += push_y

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製水流區域和波浪效果\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 畫水流區域（半透明藍色）
        water_surface = pygame.Surface((self.width, self.height))
        water_surface.set_alpha(100)  # 設定透明度
        water_surface.fill(WATER_COLOR)
        screen.blit(water_surface, (screen_x, screen_y))

        # 畫波浪線條
        for wave_line in self.wave_lines:
            if len(wave_line) > 1:
                # 轉換到螢幕座標
                screen_points = [(x - camera_x, y - camera_y) for x, y in wave_line]
                # 過濾在螢幕範圍內的點
                visible_points = [
                    (x, y)
                    for x, y in screen_points
                    if 0 <= x <= SCREEN_WIDTH and 0 <= y <= SCREEN_HEIGHT
                ]
                if len(visible_points) > 1:
                    pygame.draw.lines(screen, (100, 200, 255), False, visible_points, 2)


class WindGust(Hazard):
    """
    風暴陷阱 - 颶風場景的主要陷阱\n
    \n
    特色:\n
    1. 會推動玩家和子彈\n
    2. 有間歇性的強風爆發\n
    3. 影響跳躍高度\n
    """

    def __init__(self, x, y, width, height, wind_direction):
        """
        建立風暴陷阱\n
        \n
        參數:\n
        x, y (int): 位置座標\n
        width, height (int): 風暴區域大小\n
        wind_direction (tuple): 風向 (x_dir, y_dir)\n
        """
        super().__init__(x, y, width, height, damage=5, hazard_type="wind")
        self.wind_direction = wind_direction
        self.wind_strength = 200  # 風力強度
        self.gust_timer = 0  # 陣風計時器
        self.is_gusting = False  # 是否正在颳陣風
        self.particles = []  # 風的粒子效果
        self.generate_particles()

    def generate_particles(self):
        """
        產生風的粒子效果\n
        """
        self.particles = []

        # 產生50個風粒子
        for _ in range(50):
            particle_x = random.uniform(self.x, self.x + self.width)
            particle_y = random.uniform(self.y, self.y + self.height)
            particle_speed = random.uniform(50, 150)
            self.particles.append([particle_x, particle_y, particle_speed])

    def update(self, dt):
        """
        更新風暴效果和陣風週期\n
        """
        super().update(dt)

        # 更新陣風週期（每3-5秒一次陣風）
        self.gust_timer += dt
        if not self.is_gusting and self.gust_timer > random.uniform(3, 5):
            self.is_gusting = True
            self.gust_timer = 0
        elif self.is_gusting and self.gust_timer > 1.5:  # 陣風持續1.5秒
            self.is_gusting = False
            self.gust_timer = 0

        # 更新風粒子
        for particle in self.particles:
            # 根據風向移動粒子
            current_strength = self.wind_strength * (2 if self.is_gusting else 1)
            particle[0] += self.wind_direction[0] * current_strength * dt
            particle[1] += self.wind_direction[1] * current_strength * dt

            # 如果粒子移出區域，重新放置
            if (
                particle[0] < self.x
                or particle[0] > self.x + self.width
                or particle[1] < self.y
                or particle[1] > self.y + self.height
            ):
                particle[0] = random.uniform(self.x, self.x + self.width)
                particle[1] = random.uniform(self.y, self.y + self.height)

    def apply_force_to_player(self, player, dt):
        """
        對玩家施加風力\n
        """
        if self.check_collision(player):
            # 計算風力（陣風時加倍）
            current_strength = self.wind_strength * (2 if self.is_gusting else 1)
            wind_x = self.wind_direction[0] * current_strength * dt
            wind_y = self.wind_direction[1] * current_strength * dt

            # 應用風力
            player.velocity_x += wind_x
            player.velocity_y += wind_y

    def apply_force_to_bullet(self, bullet, dt):
        """
        對子彈施加風力影響\n
        \n
        參數:\n
        bullet (Bullet): 子彈物件\n
        dt (float): 時間間隔\n
        """
        # 檢查子彈是否在風暴區域內
        bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)  # 子彈小矩形
        wind_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if bullet_rect.colliderect(wind_rect):
            # 風力對子彈的影響較小
            wind_effect = 0.3 if not self.is_gusting else 0.6
            bullet.velocity_x += (
                self.wind_direction[0] * self.wind_strength * wind_effect * dt
            )
            bullet.velocity_y += (
                self.wind_direction[1] * self.wind_strength * wind_effect * dt
            )

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製風暴區域和粒子效果\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 畫風暴區域（半透明灰色）
        wind_surface = pygame.Surface((self.width, self.height))
        alpha = 150 if self.is_gusting else 80
        wind_surface.set_alpha(alpha)
        wind_surface.fill(WIND_COLOR)
        screen.blit(wind_surface, (screen_x, screen_y))

        # 畫風粒子
        for particle in self.particles:
            particle_screen_x = particle[0] - camera_x
            particle_screen_y = particle[1] - camera_y
            # 只畫在螢幕範圍內的粒子
            if (
                0 <= particle_screen_x <= SCREEN_WIDTH
                and 0 <= particle_screen_y <= SCREEN_HEIGHT
            ):
                color = (220, 220, 220) if self.is_gusting else (180, 180, 180)
                pygame.draw.circle(
                    screen, color, (int(particle_screen_x), int(particle_screen_y)), 2
                )


######################關卡管理器######################


class LevelManager:
    """
    關卡管理器 - 控制不同場景的生成和管理\n
    \n
    負責:\n
    1. 生成不同主題的關卡（火山、海底、颶風）\n
    2. 管理平台和陷阱的配置\n
    3. 控制關卡進度和切換\n
    4. 提供關卡特定的環境效果\n
    """

    def __init__(self):
        """
        初始化關卡管理器\n
        """
        self.current_level = 1
        self.level_theme = "volcano"  # 可選: "volcano", "underwater", "hurricane"
        self.platforms = []
        self.hazards = []
        self.level_width = SCREEN_WIDTH * 3  # 關卡寬度是螢幕的3倍
        self.level_height = SCREEN_HEIGHT
        self.generate_level()

    def generate_level(self):
        """
        根據目前關卡主題生成對應的場景\n
        """
        # 清除舊的場景物件
        self.platforms = []
        self.hazards = []

        # 根據關卡數決定主題
        if self.current_level <= 3:
            self.level_theme = "volcano"
            self.generate_volcano_level()
        elif self.current_level <= 6:
            self.level_theme = "underwater"
            self.generate_underwater_level()
        else:
            self.level_theme = "hurricane"
            self.generate_hurricane_level()

    def generate_volcano_level(self):
        """
        生成火山主題關卡\n
        \n
        特色:\n
        - 熔岩池陷阱\n
        - 岩石平台\n
        - 高溫環境效果\n
        """
        # 生成基礎平台
        platform_y = SCREEN_HEIGHT - 100
        for i in range(0, self.level_width, 200):
            # 隨機平台高度變化
            height_variation = random.randint(-50, 50)
            platform_width = random.randint(120, 180)

            platform = Platform(i, platform_y + height_variation, platform_width, 20)
            self.platforms.append(platform)

        # 生成一些高台平台用於跑酷
        for i in range(1, 6):
            platform_x = i * (self.level_width // 6) + random.randint(-50, 50)
            platform_y = SCREEN_HEIGHT - random.randint(200, 350)
            platform_width = random.randint(80, 120)

            platform = Platform(platform_x, platform_y, platform_width, 20)
            self.platforms.append(platform)

        # 生成熔岩池陷阱
        for i in range(5):
            lava_x = random.randint(100, self.level_width - 200)
            lava_y = SCREEN_HEIGHT - 80
            lava_width = random.randint(80, 150)
            lava_height = 60

            lava_pool = LavaPool(lava_x, lava_y, lava_width, lava_height)
            self.hazards.append(lava_pool)

    def generate_underwater_level(self):
        """
        生成海底主題關卡\n
        \n
        特色:\n
        - 水流陷阱\n
        - 珊瑚礁平台\n
        - 水中物理效果\n
        """
        # 生成基礎平台（海底地形）
        platform_y = SCREEN_HEIGHT - 80
        for i in range(0, self.level_width, 150):
            platform_width = random.randint(100, 200)
            height_variation = random.randint(-30, 30)

            platform = Platform(i, platform_y + height_variation, platform_width, 30)
            self.platforms.append(platform)

        # 生成珊瑚礁平台
        for i in range(1, 8):
            platform_x = i * (self.level_width // 8) + random.randint(-40, 40)
            platform_y = SCREEN_HEIGHT - random.randint(150, 300)
            platform_width = random.randint(60, 100)

            platform = Platform(platform_x, platform_y, platform_width, 15)
            self.platforms.append(platform)

        # 生成水流陷阱
        for i in range(4):
            current_x = random.randint(200, self.level_width - 300)
            current_y = random.randint(100, SCREEN_HEIGHT - 200)
            current_width = random.randint(100, 200)
            current_height = random.randint(80, 150)

            # 隨機水流方向
            flow_directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]
            flow_direction = random.choice(flow_directions)

            water_current = WaterCurrent(
                current_x, current_y, current_width, current_height, flow_direction
            )
            self.hazards.append(water_current)

    def generate_hurricane_level(self):
        """
        生成颶風主題關卡\n
        \n
        特色:\n
        - 風暴陷阱\n
        - 浮動平台\n
        - 強風環境效果\n
        """
        # 生成基礎平台
        platform_y = SCREEN_HEIGHT - 60
        for i in range(0, self.level_width, 250):
            platform_width = random.randint(100, 160)

            platform = Platform(i, platform_y, platform_width, 20)
            self.platforms.append(platform)

        # 生成浮動平台（高度較高）
        for i in range(1, 10):
            platform_x = i * (self.level_width // 10) + random.randint(-60, 60)
            platform_y = SCREEN_HEIGHT - random.randint(200, 400)
            platform_width = random.randint(80, 120)

            platform = Platform(platform_x, platform_y, platform_width, 15)
            self.platforms.append(platform)

        # 生成風暴陷阱
        for i in range(6):
            wind_x = random.randint(100, self.level_width - 200)
            wind_y = random.randint(50, SCREEN_HEIGHT - 150)
            wind_width = random.randint(120, 200)
            wind_height = random.randint(100, 180)

            # 隨機風向
            wind_directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
            wind_direction = random.choice(wind_directions)

            wind_gust = WindGust(
                wind_x, wind_y, wind_width, wind_height, wind_direction
            )
            self.hazards.append(wind_gust)

    def next_level(self):
        """
        進入下一關\n
        """
        self.current_level += 1
        self.generate_level()

    def update(self, dt, player, bullets):
        """
        更新關卡中的所有動態物件\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player (Player): 玩家物件\n
        bullets (list): 子彈列表\n
        """
        # 更新所有陷阱
        for hazard in self.hazards:
            hazard.update(dt)

            # 陷阱對玩家的影響
            if isinstance(hazard, (WaterCurrent, WindGust)):
                hazard.apply_force_to_player(player, dt)

            # 風暴對子彈的影響
            if isinstance(hazard, WindGust):
                for bullet in bullets:
                    hazard.apply_force_to_bullet(bullet, dt)

    def check_hazard_collisions(self, player):
        """
        檢查玩家與陷阱的碰撞\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        int: 受到的總傷害\n
        """
        total_damage = 0

        for hazard in self.hazards:
            if hazard.check_collision(player):
                total_damage += hazard.damage

        return total_damage

    def get_platforms(self):
        """
        取得關卡中的所有平台\n
        \n
        回傳:\n
        list: 平台物件列表\n
        """
        return self.platforms

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製整個關卡場景\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 繪製背景顏色（根據主題）
        if self.level_theme == "volcano":
            background_color = (80, 40, 20)  # 深棕紅色
        elif self.level_theme == "underwater":
            background_color = (20, 50, 80)  # 深藍色
        else:  # hurricane
            background_color = (40, 40, 60)  # 深灰色

        screen.fill(background_color)

        # 繪製平台
        for platform in self.platforms:
            platform.draw(screen, camera_x, camera_y)

        # 繪製陷阱
        for hazard in self.hazards:
            hazard.draw(screen, camera_x, camera_y)

    def get_level_info(self):
        """
        取得關卡資訊\n
        \n
        回傳:\n
        dict: 關卡資訊字典\n
        """
        return {
            "level": self.current_level,
            "theme": self.level_theme,
            "width": self.level_width,
            "height": self.level_height,
            "platform_count": len(self.platforms),
            "hazard_count": len(self.hazards),
        }
