######################載入套件######################
import pygame
import random
import math

# 嘗試相對導入，如果失敗則使用絕對導入
try:
    from ..config import *
except ImportError:
    # 直接執行時使用絕對導入
    from src.config import *

######################雲朵系統######################


class Cloud:
    """
    單個雲朵物件 - 天空背景中的雲朵\n
    \n
    每個雲朵有自己的位置、大小、移動速度和外觀\n
    雲朵會持續緩慢移動，營造天空動態效果\n
    """

    def __init__(self, x, y, size, speed, layer=0):
        """
        初始化雲朵物件\n
        \n
        參數:\n
        x (float): 雲朵初始 X 位置，範圍任意\n
        y (float): 雲朵初始 Y 位置，範圍任意\n
        size (float): 雲朵大小倍數，範圍 0.5-2.0\n
        speed (float): 雲朵移動速度，範圍 0.1-2.0\n
        layer (int): 雲朵層次，0=背景層，1=前景層\n
        """
        self.x = x
        self.y = y
        self.size = size  # 雲朵大小倍數
        self.speed = speed  # 水平移動速度
        self.layer = layer  # 層次，影響顏色深淺

        # 雲朵基本尺寸
        self.base_width = 80
        self.base_height = 40
        self.width = self.base_width * size
        self.height = self.base_height * size

        # 根據層次設定顏色深淺
        if layer == 0:
            # 背景層 - 較淡的顏色
            self.color = CLOUD_BACKGROUND_COLOR  # 半透明淺灰藍
        else:
            # 前景層 - 較深的顏色
            self.color = CLOUD_FOREGROUND_COLOR  # 半透明灰白

    def update(self, dt):
        """
        更新雲朵位置\n
        \n
        參數:\n
        dt (float): 時間差，用於平滑移動\n
        """
        # 雲朵緩慢向右飄移
        self.x += self.speed * dt * 60  # 轉換為每秒像素數

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製雲朵 - 使用橢圓形狀組合成雲朵外觀\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製表面\n
        camera_x (float): 攝影機 X 偏移\n
        camera_y (float): 攝影機 Y 偏移\n
        """
        # 計算螢幕座標（雲朵受攝影機影響較小）
        parallax_factor = 0.3 if self.layer == 0 else 0.6  # 背景層移動更慢
        screen_x = self.x - (camera_x * parallax_factor)
        screen_y = self.y - (camera_y * parallax_factor)

        # 如果雲朵不在螢幕範圍內就不繪製
        if screen_x + self.width < -50 or screen_x > SCREEN_WIDTH + 50:
            return
        if screen_y + self.height < -50 or screen_y > SCREEN_HEIGHT + 50:
            return

        # 創建半透明表面
        cloud_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # 繪製雲朵形狀 - 由多個橢圓組成
        self._draw_cloud_shape(cloud_surface)

        # 將雲朵繪製到螢幕上
        screen.blit(cloud_surface, (screen_x, screen_y))

    def _draw_cloud_shape(self, surface):
        """
        繪製雲朵形狀 - 使用多個橢圓組合\n
        \n
        參數:\n
        surface (pygame.Surface): 雲朵的繪製表面\n
        """
        # 主要的雲朵顏色（去掉透明度用於橢圓繪製）
        base_color = self.color[:3]

        # 繪製主體橢圓
        main_width = int(self.width * 0.8)
        main_height = int(self.height * 0.6)
        main_x = int(self.width * 0.1)
        main_y = int(self.height * 0.2)

        pygame.draw.ellipse(
            surface, base_color, (main_x, main_y, main_width, main_height)
        )

        # 繪製左側小圓
        left_radius = int(self.height * 0.3)
        left_x = int(self.width * 0.15)
        left_y = int(self.height * 0.3)

        pygame.draw.circle(surface, base_color, (left_x, left_y), left_radius)

        # 繪製右側小圓
        right_radius = int(self.height * 0.25)
        right_x = int(self.width * 0.75)
        right_y = int(self.height * 0.4)

        pygame.draw.circle(surface, base_color, (right_x, right_y), right_radius)

        # 繪製頂部小圓
        top_radius = int(self.height * 0.2)
        top_x = int(self.width * 0.4)
        top_y = int(self.height * 0.15)

        pygame.draw.circle(surface, base_color, (top_x, top_y), top_radius)


class CloudSystem:
    """
    雲朵系統管理器 - 管理天空中所有雲朵的生成、更新和顯示\n
    \n
    負責：\n
    1. 生成適量的雲朵分布在天空中\n
    2. 管理雲朵的移動和更新\n
    3. 處理雲朵的循環（移出螢幕後重新生成）\n
    4. 提供不同層次的雲朵營造景深效果\n
    """

    def __init__(self, level_width, level_height):
        """
        初始化雲朵系統\n
        \n
        參數:\n
        level_width (int): 關卡總寬度，用於雲朵分布範圍\n
        level_height (int): 關卡總高度，用於雲朵分布範圍\n
        """
        self.level_width = level_width
        self.level_height = level_height
        self.clouds = []  # 雲朵列表

        # 雲朵生成設定
        self.cloud_count = CLOUD_COUNT  # 總雲朵數量
        self.min_cloud_speed = CLOUD_MIN_SPEED  # 最小移動速度
        self.max_cloud_speed = CLOUD_MAX_SPEED  # 最大移動速度
        self.cloud_respawn_distance = CLOUD_RESPAWN_DISTANCE  # 雲朵重生距離

        # 初始化雲朵
        self._generate_initial_clouds()

    def _generate_initial_clouds(self):
        """
        生成初始雲朵分布在整個關卡天空中\n
        """
        for i in range(self.cloud_count):
            # 隨機分布在整個關卡範圍
            x = random.uniform(
                -self.cloud_respawn_distance,
                self.level_width + self.cloud_respawn_distance,
            )

            # 雲朵主要分布在上半部天空
            y = random.uniform(0, self.level_height * 0.4)

            # 隨機雲朵大小
            size = random.uniform(CLOUD_MIN_SIZE, CLOUD_MAX_SIZE)

            # 隨機移動速度
            speed = random.uniform(self.min_cloud_speed, self.max_cloud_speed)

            # 隨機層次
            layer = random.choice([0, 0, 1])  # 背景層機率較高

            # 創建雲朵
            cloud = Cloud(x, y, size, speed, layer)
            self.clouds.append(cloud)

    def update(self, dt, camera_x):
        """
        更新所有雲朵位置\n
        \n
        參數:\n
        dt (float): 時間差\n
        camera_x (float): 攝影機 X 位置，用於判斷雲朵是否需要重生\n
        """
        for cloud in self.clouds:
            # 更新雲朵位置
            cloud.update(dt)

            # 檢查雲朵是否移出右側螢幕太遠
            if cloud.x > camera_x + SCREEN_WIDTH + self.cloud_respawn_distance:
                # 重新定位到左側
                cloud.x = camera_x - self.cloud_respawn_distance
                cloud.y = random.uniform(0, self.level_height * 0.4)
                cloud.size = random.uniform(CLOUD_MIN_SIZE, CLOUD_MAX_SIZE)
                cloud.speed = random.uniform(self.min_cloud_speed, self.max_cloud_speed)
                cloud.layer = random.choice([0, 0, 1])

                # 更新雲朵尺寸
                cloud.width = cloud.base_width * cloud.size
                cloud.height = cloud.base_height * cloud.size

                # 更新雲朵顏色
                if cloud.layer == 0:
                    cloud.color = CLOUD_BACKGROUND_COLOR
                else:
                    cloud.color = CLOUD_FOREGROUND_COLOR

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有雲朵 - 先畫背景層再畫前景層\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製表面\n
        camera_x (float): 攝影機 X 偏移\n
        camera_y (float): 攝影機 Y 偏移\n
        """
        # 先繪製背景層雲朵
        for cloud in self.clouds:
            if cloud.layer == 0:
                cloud.draw(screen, camera_x, camera_y)

        # 再繪製前景層雲朵
        for cloud in self.clouds:
            if cloud.layer == 1:
                cloud.draw(screen, camera_x, camera_y)
