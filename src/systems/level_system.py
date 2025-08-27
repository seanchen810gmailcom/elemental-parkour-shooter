######################載入套件######################
import pygame
import random
import math

# 支援直接執行和模組執行兩種方式
try:
    from ..config import *
    from ..core.game_objects import *
except ImportError:
    from src.config import *
    from src.core.game_objects import *

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
    關卡管理器 - 控制跑酷平台的生成和管理\n
    \n
    負責:\n
    1. 生成30層高度的跑酷平台系統\n
    2. 管理平台配置和目標星星\n
    3. 提供安全的跑酷體驗\n
    4. 無危險陷阱，專注跑酷樂趣\n
    """

    def __init__(self):
        """
        初始化關卡管理器\n
        """
        self.current_level = 1
        self.level_theme = "parkour"  # 跑酷主題
        self.platforms = []
        self.hazards = []  # 保留但不使用危險陷阱
        self.level_width = SCREEN_WIDTH * 3  # 關卡寬度適中
        self.level_height = SCREEN_HEIGHT * 15  # 高度大幅增加，容納30層
        self.total_levels = 30  # 總共30層
        self.star_collected = False  # 星星是否被收集
        self.star_x = 0  # 星星位置
        self.star_y = 0
        self.generate_level()

    def generate_level(self):
        """
        生成30層跑酷平台系統\n
        """
        # 清除舊的場景物件
        self.platforms = []
        self.hazards = []  # 不使用危險陷阱

        # 生成30層跑酷平台
        self.generate_parkour_platforms()

        # 在最高層放置目標星星
        self.place_target_star()

    def generate_parkour_platforms(self):
        """
        生成30層跑酷平台系統\n
        \n
        特色:\n
        - 每層都有安全的落腳點\n
        - 平台大小和間距適合跑酷\n
        - 從底部到頂部逐漸提升挑戰\n
        - 沒有會讓玩家死亡的陷阱\n
        - 實心地板確保玩家不會掉下去死亡\n
        """
        # 生成實心地面（加厚地板，覆蓋整個關卡底部）
        ground_thickness = 80  # 地板厚度
        ground_platform = Platform(
            0, SCREEN_HEIGHT - ground_thickness, self.level_width, ground_thickness
        )
        self.platforms.append(ground_platform)

        # 每層平台的基本設定
        platforms_per_level = 3  # 每層3個平台
        level_height_gap = 100  # 每層之間的高度差（減少到100像素，更容易攀爬）
        platform_min_width = 120  # 增加最小寬度讓平台更好跳上去
        platform_max_width = 200  # 增加最大寬度

        for level in range(1, self.total_levels + 1):
            # 計算這層的基準高度
            base_y = SCREEN_HEIGHT - ground_thickness - (level * level_height_gap)

            # 每層的平台分佈在整個關卡寬度上
            section_width = self.level_width // platforms_per_level

            for section in range(platforms_per_level):
                # 在每個區段內隨機放置平台
                section_start = section * section_width
                section_end = section_start + section_width

                # 平台位置隨機，但確保可達性（減少間距）
                platform_x = random.randint(
                    section_start + 20, section_end - platform_max_width - 20
                )

                # 平台高度變化很小，讓跳躍更容易
                height_variation = random.randint(-15, 15)
                platform_y = base_y + height_variation

                # 平台寬度隨機
                platform_width = random.randint(platform_min_width, platform_max_width)

                # 確保平台不會太接近邊界
                if platform_x + platform_width > self.level_width:
                    platform_x = self.level_width - platform_width

                # 創建平台
                platform = Platform(platform_x, platform_y, platform_width, 25)
                self.platforms.append(platform)

            # 為了確保可達性，在每層額外增加一些小跳板
            if level % 3 == 0:  # 每三層增加額外的輔助平台
                extra_x = self.level_width // 2
                extra_y = base_y - 30
                extra_platform = Platform(extra_x - 40, extra_y, 80, 20)
                self.platforms.append(extra_platform)

        # 在左右兩側創建實心牆壁，防止玩家掉出關卡
        left_wall = Platform(-50, 0, 50, self.level_height)
        right_wall = Platform(self.level_width, 0, 50, self.level_height)
        self.platforms.append(left_wall)
        self.platforms.append(right_wall)

    def place_target_star(self):
        """
        在最高層放置閃閃發亮的目標星星\n
        """
        # 星星放在最高層的中央平台上（使用新的高度差100）
        ground_thickness = 80
        star_y = SCREEN_HEIGHT - ground_thickness - (self.total_levels * 100) - 60
        self.star_x = self.level_width // 2
        self.star_y = star_y
        self.star_collected = False

        # 在星星下方創建一個特殊的大平台
        star_platform = Platform(self.star_x - 150, star_y + 50, 300, 40)
        self.platforms.append(star_platform)

    def check_star_collision(self, player):
        """
        檢查玩家是否碰到目標星星\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        bool: 是否收集到星星\n
        """
        if self.star_collected:
            return False

        # 星星的碰撞範圍
        star_size = 30
        star_rect = pygame.Rect(
            self.star_x - star_size // 2,
            self.star_y - star_size // 2,
            star_size,
            star_size,
        )
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

        if player_rect.colliderect(star_rect):
            self.star_collected = True
            return True

        return False

    def update(self, dt, player, bullets):
        """
        更新關卡中的所有動態物件\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player (Player): 玩家物件\n
        bullets (list): 子彈列表\n
        """
        # 檢查玩家是否收集到星星
        if self.check_star_collision(player):
            print("🌟 恭喜！您找到了目標星星！")
            return {"star_collected": True}

        return {"star_collected": False}

    def check_hazard_collisions(self, player):
        """
        檢查玩家與環境的碰撞（現在沒有危險陷阱）\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        int: 受到的總傷害（現在總是0）\n
        """
        # 移除所有危險陷阱，返回0傷害
        return 0

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
        # 繪製背景顏色（爽朗的天空藍）
        background_color = (135, 206, 235)  # 天空藍
        screen.fill(background_color)

        # 繪製平台
        for platform in self.platforms:
            platform.draw(screen, camera_x, camera_y)

        # 繪製目標星星（如果還沒被收集）
        if not self.star_collected:
            self.draw_target_star(screen, camera_x, camera_y)

    def draw_target_star(self, screen, camera_x=0, camera_y=0):
        """
        繪製閃閃發亮的目標星星\n
        \n
        參數:\n
        screen (pygame.Surface): 遊戲畫面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 計算螢幕位置
        screen_x = self.star_x - camera_x
        screen_y = self.star_y - camera_y

        # 只在螢幕範圍內繪製
        if (
            -50 <= screen_x <= SCREEN_WIDTH + 50
            and -50 <= screen_y <= SCREEN_HEIGHT + 50
        ):

            # 創建閃爍效果
            import time

            flash_intensity = abs(math.sin(time.time() * 4)) * 0.5 + 0.5

            # 星星大小
            star_size = 25

            # 繪製發光外圈
            glow_color = (255, 255, int(100 + flash_intensity * 155))
            for i in range(5, 0, -1):
                alpha = int((6 - i) * flash_intensity * 50)
                glow_surface = pygame.Surface((star_size + i * 4, star_size + i * 4))
                glow_surface.set_alpha(alpha)
                glow_surface.fill(glow_color)
                screen.blit(
                    glow_surface,
                    (
                        screen_x - star_size // 2 - i * 2,
                        screen_y - star_size // 2 - i * 2,
                    ),
                )

            # 繪製星星主體（五角星）
            star_color = (255, 255, int(150 + flash_intensity * 105))
            star_points = []

            # 計算五角星的頂點
            for i in range(10):
                angle = math.pi * i / 5
                if i % 2 == 0:
                    # 外圍頂點
                    radius = star_size
                else:
                    # 內圍頂點
                    radius = star_size * 0.4

                x = screen_x + radius * math.cos(angle - math.pi / 2)
                y = screen_y + radius * math.sin(angle - math.pi / 2)
                star_points.append((x, y))

            if len(star_points) >= 3:
                pygame.draw.polygon(screen, star_color, star_points)

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
            "total_levels": self.total_levels,
            "platform_count": len(self.platforms),
            "star_collected": self.star_collected,
        }
