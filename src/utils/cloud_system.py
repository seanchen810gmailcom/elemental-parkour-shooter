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
    使用 Cloud.png 圖片素材來顯示雲朵外觀\n
    """

    def __init__(self, x, y, size, speed):
        """
        初始化雲朵物件\n
        \n
        參數:\n
        x (float): 雲朵初始 X 位置，範圍任意\n
        y (float): 雲朵初始 Y 位置，範圍任意\n
        size (float): 雲朵大小倍數，範圍 0.5-2.0\n
        speed (float): 雲朵移動速度，範圍 0.1-2.0\n
        """
        self.x = x
        self.y = y
        self.size = size  # 雲朵大小倍數
        self.speed = speed  # 水平移動速度

        # 雲朵基本尺寸（基於配置）
        self.base_width = CLOUD_IMAGE_BASE_SIZE[0]
        self.base_height = CLOUD_IMAGE_BASE_SIZE[1]
        self.width = self.base_width * size
        self.height = self.base_height * size

        # 載入雲朵圖片
        self.image = self._load_cloud_image()

        # 統一設定為完全不透明
        self.alpha = 255

    def _load_cloud_image(self):
        """
        載入雲朵圖片素材\n
        \n
        回傳:\n
        pygame.Surface: 雲朵圖片表面，如果載入失敗則返回程式繪製的雲朵\n
        """
        try:
            # 嘗試載入雲朵圖片
            cloud_image = pygame.image.load(CLOUD_IMAGE_PATH).convert_alpha()
            cloud_image = pygame.transform.scale(
                cloud_image, (int(self.width), int(self.height))
            )
            return cloud_image
        except (pygame.error, FileNotFoundError) as e:
            print(f"🌤️ 載入雲朵圖片失敗: {e}")
            # 創建一個白色雲朵，完全不透明
            cloud_surface = pygame.Surface(
                (int(self.width), int(self.height)), pygame.SRCALPHA
            )

            # 使用純白色，完全不透明
            cloud_color = (255, 255, 255, 255)  # 純白色，完全不透明

            # 繪製雲朵形狀
            center_x = int(self.width / 2)
            center_y = int(self.height / 2)

            # 繪製主要橢圓
            pygame.draw.ellipse(
                cloud_surface,
                cloud_color,
                (0, int(self.height * 0.3), int(self.width), int(self.height * 0.4)),
            )

            # 繪製左側圓形
            pygame.draw.circle(
                cloud_surface,
                cloud_color,
                (int(self.width * 0.25), center_y),
                int(self.height * 0.3),
            )

            # 繪製右側圓形
            pygame.draw.circle(
                cloud_surface,
                cloud_color,
                (int(self.width * 0.75), center_y),
                int(self.height * 0.25),
            )

            # 繪製頂部圓形
            pygame.draw.circle(
                cloud_surface,
                cloud_color,
                (center_x, int(self.height * 0.2)),
                int(self.height * 0.2),
            )

            print(
                f"🌤️ 使用統一白色雲朵圖案，大小: {int(self.width)}x{int(self.height)}, 顏色: {cloud_color}"
            )
            return cloud_surface

    def _create_fallback_cloud(self):
        """
        創建備用雲朵圖案（當圖片載入失敗時使用）\n
        \n
        回傳:\n
        pygame.Surface: 程式繪製的雲朵表面\n
        """
        # 創建雲朵表面
        cloud_surface = pygame.Surface(
            (int(self.width), int(self.height)), pygame.SRCALPHA
        )

        # 根據層次選擇顏色
        if self.layer == 0:
            base_color = CLOUD_BACKGROUND_COLOR[:3]  # 背景層顏色
        else:
            base_color = CLOUD_FOREGROUND_COLOR[:3]  # 前景層顏色

        # 繪製雲朵形狀 - 由多個橢圓組成
        self._draw_cloud_shape_on_surface(cloud_surface, base_color)

        return cloud_surface

    def _draw_cloud_shape_on_surface(self, surface, color):
        """
        在表面上繪製雲朵形狀 - 使用多個橢圓組合\n
        \n
        參數:\n
        surface (pygame.Surface): 雲朵的繪製表面\n
        color (tuple): 雲朵顏色 (R, G, B)\n
        """
        width, height = surface.get_size()

        # 繪製主體橢圓
        main_width = int(width * 0.8)
        main_height = int(height * 0.6)
        main_x = int(width * 0.1)
        main_y = int(height * 0.2)
        pygame.draw.ellipse(surface, color, (main_x, main_y, main_width, main_height))

        # 繪製左側小圓
        left_radius = int(height * 0.3)
        left_x = int(width * 0.15)
        left_y = int(height * 0.3)
        pygame.draw.circle(surface, color, (left_x, left_y), left_radius)

        # 繪製右側小圓
        right_radius = int(height * 0.25)
        right_x = int(width * 0.75)
        right_y = int(height * 0.4)
        pygame.draw.circle(surface, color, (right_x, right_y), right_radius)

        # 繪製頂部小圓
        top_radius = int(height * 0.2)
        top_x = int(width * 0.4)
        top_y = int(height * 0.15)
        pygame.draw.circle(surface, color, (top_x, top_y), top_radius)

    def update(self, dt):
        """
        更新雲朵位置\n
        \n
        參數:\n
        dt (float): 時間差，用於平滑移動\n
        """
        # 雲朵緩慢向右飄移
        self.x += self.speed * dt * 60  # 轉換為每秒像素數

    def update_size(self, new_size):
        """
        更新雲朵大小並重新載入圖片\n
        \n
        參數:\n
        new_size (float): 新的雲朵大小倍數\n
        """
        self.size = new_size
        self.width = self.base_width * new_size
        self.height = self.base_height * new_size
        # 重新載入並縮放圖片
        self.image = self._load_cloud_image()

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製雲朵 - 使用相對座標跟隨玩家\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製表面\n
        camera_x (float): 攝影機 X 偏移\n
        camera_y (float): 攝影機 Y 偏移\n
        """
        # 計算雲朵在螢幕上的相對位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 檢查是否在螢幕範圍內（允許稍微超出螢幕邊界）
        if (
            screen_x + self.width < -100
            or screen_x > SCREEN_WIDTH + 100
            or screen_y + self.height < -100
            or screen_y > SCREEN_HEIGHT + 100
        ):
            return

        # 將雲朵繪製到螢幕上
        screen.blit(self.image, (screen_x, screen_y))


class CloudSystem:
    """
    雲朵系統管理器 - 管理天空中的背景雲朵\n
    \n
    負責：\n
    1. 生成多朵雲朵分布在天空背景中\n
    2. 雲朵固定在背景位置，不跟隨玩家移動\n
    3. 使用純白色無透明度顯示\n
    4. 營造靜態天空背景效果\n
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

        # 初始化背景雲朵
        self._generate_background_clouds()

    def _generate_background_clouds(self):
        """
        生成背景雲朵分布在天空中\n
        \n
        雲朵Y位置設定為Y100~Y400，固定在天空背景中\n
        """
        # 設定雲朵分布的Y範圍：Y100到Y400（天空區域）
        cloud_top = 100  # 雲朵分布上限
        cloud_bottom = 400  # 雲朵分布下限

        for i in range(self.cloud_count):
            # 在整個關卡寬度範圍內隨機分布
            x = random.uniform(0, self.level_width)

            # 雲朵分布在Y100~Y400範圍內（天空區域）
            y = random.uniform(cloud_top, cloud_bottom)

            # 隨機雲朵大小
            size = random.uniform(CLOUD_MIN_SIZE, CLOUD_MAX_SIZE)

            # 速度設為0，雲朵不移動
            speed = 0

            # 創建背景雲朵
            cloud = Cloud(x, y, size, speed)
            self.clouds.append(cloud)

    def update(self, dt, player_x, player_y):
        """
        更新雲朵系統 - 背景雲朵不需要更新\n
        \n
        參數:\n
        dt (float): 時間差\n
        player_x (float): 玩家X座標（保留相容性）\n
        player_y (float): 玩家Y座標（保留相容性）\n
        """
        # 背景雲朵固定不動，不需要更新
        pass

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製背景雲朵 - 固定在背景位置\n
        \n
        參數:\n
        screen (pygame.Surface): 繪製表面\n
        camera_x (float): 攝影機 X 偏移\n
        camera_y (float): 攝影機 Y 偏移\n
        """
        # 繪製所有背景雲朵
        for cloud in self.clouds:
            cloud.draw(screen, camera_x, camera_y)
