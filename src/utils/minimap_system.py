######################載入套件######################
import pygame
import math
import random

# 嘗試相對導入，如果失敗則使用絕對導入
try:
    from ..config import *
except ImportError:
    # 直接執行時使用絕對導入
    from src.config import *

######################小地圖系統######################


class MinimapSystem:
    """
    小地圖系統 - 顯示玩家和怪物的位置概覽\n
    \n
    功能：\n
    1. 在右上角顯示關卡的縮小版本\n
    2. 標示玩家當前位置\n
    3. 顯示所有怪物位置，使用不同顏色區分屬性\n
    4. 顯示Boss位置（如果存在）\n
    5. 顯示勝利星星位置（如果存在）\n
    6. 支援拖拽改變位置\n
    7. 彩色地形顯示\n
    8. 背景雲朵裝飾\n
    \n
    設計理念：\n
    - 半透明背景，不遮擋遊戲畫面\n
    - 簡潔的圖示，一目了然\n
    - 動態更新，即時反映遊戲狀態\n
    - 可拖拽的互動式小地圖\n
    """

    def __init__(self, level_width, level_height):
        """
        初始化小地圖系統\n
        \n
        參數:\n
        level_width (int): 關卡總寬度\n
        level_height (int): 關卡總高度\n
        """
        self.level_width = level_width
        self.level_height = level_height

        # 小地圖尺寸和位置設定
        self.minimap_width = MINIMAP_WIDTH  # 小地圖寬度
        self.minimap_height = MINIMAP_HEIGHT  # 小地圖高度
        self.margin = MINIMAP_MARGIN  # 距離螢幕邊緣的間距

        # 小地圖在螢幕上的位置（右上角）
        self.minimap_x = SCREEN_WIDTH - self.minimap_width - self.margin
        self.minimap_y = self.margin

        # 拖拽相關變數
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.original_x = self.minimap_x
        self.original_y = self.minimap_y

        # 縮放比例計算
        self.scale_x = self.minimap_width / level_width
        self.scale_y = self.minimap_height / level_height

        # 顏色設定
        self.bg_color = MINIMAP_BG_COLOR  # 半透明黑色背景
        self.border_color = MINIMAP_BORDER_COLOR  # 白色邊框
        self.player_color = MINIMAP_PLAYER_COLOR  # 綠色玩家點
        self.boss_color = MINIMAP_BOSS_COLOR  # 紫色Boss點
        self.star_color = MINIMAP_STAR_COLOR  # 黃色星星

        # 地形顏色設定（與主遊戲同步）
        self.ground_color = (101, 67, 33)  # 深棕色地面（與main.py一致）
        self.sky_color = SKY_COLOR  # 天空藍（使用config.py的定義）
        self.grass_color = (34, 139, 34)  # 草綠色（與main.py一致）

        # 怪物顏色映射（根據屬性）
        self.monster_colors = {
            "lava": MINIMAP_LAVA_MONSTER_COLOR,  # 橘紅色 - 岩漿怪
            "water": MINIMAP_WATER_MONSTER_COLOR,  # 藍色 - 水怪
            "tornado": MINIMAP_TORNADO_MONSTER_COLOR,  # 淺藍色 - 龍捲風怪
            "default": MINIMAP_DEFAULT_MONSTER_COLOR,  # 預設紅色
        }

        # 創建小地圖表面
        self.minimap_surface = pygame.Surface(
            (self.minimap_width, self.minimap_height), pygame.SRCALPHA
        )

        # 初始化小地圖系統，不需要雲朵裝飾
        # self._init_minimap_clouds()  # 移除雲朵系統

    def handle_mouse_event(self, event):
        """
        處理滑鼠事件以支援拖拽功能\n
        \n
        參數:\n
        event: pygame事件物件\n
        \n
        回傳:\n
        bool: 是否處理了事件\n
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵
                # 檢查是否點擊在小地圖範圍內
                if (
                    self.minimap_x <= mouse_x <= self.minimap_x + self.minimap_width
                    and self.minimap_y
                    <= mouse_y
                    <= self.minimap_y + self.minimap_height
                ):
                    self.is_dragging = True
                    self.drag_offset_x = mouse_x - self.minimap_x
                    self.drag_offset_y = mouse_y - self.minimap_y
                    return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左鍵
                self.is_dragging = False
                return self.is_dragging  # 如果之前正在拖拽，回傳True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # 更新小地圖位置
                new_x = mouse_x - self.drag_offset_x
                new_y = mouse_y - self.drag_offset_y

                # 限制在螢幕範圍內
                self.minimap_x = max(0, min(SCREEN_WIDTH - self.minimap_width, new_x))
                self.minimap_y = max(0, min(SCREEN_HEIGHT - self.minimap_height, new_y))
                return True

        return False

    def _world_to_minimap(self, world_x, world_y):
        """
        將世界座標轉換為小地圖座標\n
        使用簡單的直接比例映射，確保位置準確\n
        \n
        參數:\n
        world_x (float): 世界座標 X\n
        world_y (float): 世界座標 Y\n
        \n
        回傳:\n
        tuple: (minimap_x, minimap_y) 小地圖內的座標\n
        """
        # 直接比例映射，不做複雜的區域劃分
        minimap_x = world_x * self.scale_x
        minimap_y = world_y * self.scale_y

        # 確保座標在小地圖範圍內
        minimap_x = max(0, min(self.minimap_width - 1, minimap_x))
        minimap_y = max(0, min(self.minimap_height - 1, minimap_y))

        return int(minimap_x), int(minimap_y)

    def _draw_background(self):
        """
        繪製小地圖背景和邊框\n
        簡潔版本：只顯示關卡的基本區域，不包含裝飾性元素\n
        """
        # 清空表面
        self.minimap_surface.fill((0, 0, 0, 0))

        # 繪製簡潔的背景 - 只有基本的天空和地面區域劃分
        # 上半部為天空區域（淺藍色）
        sky_rect = pygame.Rect(0, 0, self.minimap_width, self.minimap_height // 2)
        pygame.draw.rect(self.minimap_surface, (200, 230, 255), sky_rect)  # 淺天藍色

        # 下半部為地面區域（淺棕色）
        ground_rect = pygame.Rect(
            0, self.minimap_height // 2, self.minimap_width, self.minimap_height // 2
        )
        pygame.draw.rect(self.minimap_surface, (180, 150, 120), ground_rect)  # 淺棕色

        # 繪製邊框
        pygame.draw.rect(
            self.minimap_surface,
            self.border_color[:3],
            (0, 0, self.minimap_width, self.minimap_height),
            2,
        )

    def _draw_platforms(self, platforms):
        """
        繪製關卡平台的簡化版本\n
        使用彩色和更豐富的視覺效果\n
        \n
        參數:\n
        platforms (list): 平台物件列表\n
        """
        for platform in platforms:
            # 轉換平台座標
            platform_x, platform_y = self._world_to_minimap(platform.x, platform.y)
            platform_w = max(2, int(platform.width * self.scale_x))  # 最小寬度2像素
            platform_h = max(2, int(platform.height * self.scale_y))  # 最小高度2像素

            # 繪製平台矩形
            if platform_x < self.minimap_width and platform_y < self.minimap_height:
                platform_rect = pygame.Rect(
                    platform_x, platform_y, platform_w, platform_h
                )

                # 根據平台位置選擇顏色
                # 低處平台使用深棕色，高處平台使用灰色
                if platform.y > self.level_height * 0.7:
                    platform_color = (139, 69, 19)  # 深棕色（地面平台）
                elif platform.y > self.level_height * 0.4:
                    platform_color = (160, 82, 45)  # 中棕色（中層平台）
                else:
                    platform_color = (169, 169, 169)  # 灰色（高空平台）

                # 繪製平台主體
                pygame.draw.rect(self.minimap_surface, platform_color, platform_rect)

                # 添加頂部高光效果
                if platform_h >= 3:
                    highlight_color = tuple(min(255, c + 30) for c in platform_color)
                    highlight_rect = pygame.Rect(platform_x, platform_y, platform_w, 1)
                    pygame.draw.rect(
                        self.minimap_surface, highlight_color, highlight_rect
                    )

    def _draw_player(self, player):
        """
        繪製玩家位置\n
        \n
        參數:\n
        player: 玩家物件\n
        """
        if not player.is_alive:
            return

        # 轉換玩家座標
        player_x, player_y = self._world_to_minimap(
            player.x + player.width // 2,  # 使用玩家中心點
            player.y + player.height // 2,
        )

        # 繪製玩家點（帶光環效果）
        player_radius = 4

        # 外圈光環
        pygame.draw.circle(
            self.minimap_surface,
            (255, 255, 255),
            (player_x, player_y),
            player_radius + 1,
        )

        # 主要玩家點
        pygame.draw.circle(
            self.minimap_surface, self.player_color, (player_x, player_y), player_radius
        )

    def _draw_monsters(self, monsters):
        """
        繪製怪物位置，使用不同形狀和顏色區分怪物類型\n
        \n
        參數:\n
        monsters (list): 怪物物件列表\n
        """
        for monster in monsters:
            if not hasattr(monster, "x") or not hasattr(monster, "y"):
                continue

            # 轉換怪物座標
            monster_x, monster_y = self._world_to_minimap(
                monster.x + monster.width // 2,  # 使用怪物中心點
                monster.y + monster.height // 2,
            )

            # 根據怪物類型選擇顏色和形狀
            monster_type = getattr(monster, "monster_type", "default")
            monster_color = self.monster_colors.get(
                monster_type, self.monster_colors["default"]
            )

            # 根據不同怪物類型繪製不同形狀
            if monster_type == "lava":
                # 岩漿怪：圓形 + 外圈
                pygame.draw.circle(
                    self.minimap_surface,
                    (255, 255, 255),  # 白色外圈
                    (monster_x, monster_y),
                    5,
                )
                pygame.draw.circle(
                    self.minimap_surface,
                    monster_color,
                    (monster_x, monster_y),
                    3,
                )
            elif monster_type == "water":
                # 水怪：方形
                rect_size = 6
                pygame.draw.rect(
                    self.minimap_surface,
                    monster_color,
                    (
                        monster_x - rect_size // 2,
                        monster_y - rect_size // 2,
                        rect_size,
                        rect_size,
                    ),
                )
                # 白色邊框
                pygame.draw.rect(
                    self.minimap_surface,
                    (255, 255, 255),
                    (
                        monster_x - rect_size // 2,
                        monster_y - rect_size // 2,
                        rect_size,
                        rect_size,
                    ),
                    1,
                )
            elif monster_type == "tornado":
                # 龍捲風怪：三角形
                triangle_points = [
                    (monster_x, monster_y - 4),  # 頂點
                    (monster_x - 4, monster_y + 3),  # 左下
                    (monster_x + 4, monster_y + 3),  # 右下
                ]
                pygame.draw.polygon(
                    self.minimap_surface,
                    monster_color,
                    triangle_points,
                )
                # 白色邊框
                pygame.draw.polygon(
                    self.minimap_surface,
                    (255, 255, 255),
                    triangle_points,
                    1,
                )
            else:
                # 預設怪物：簡單圓形
                pygame.draw.circle(
                    self.minimap_surface,
                    monster_color,
                    (monster_x, monster_y),
                    3,
                )

    def _draw_boss(self, boss):
        """
        繪製Boss位置\n
        \n
        參數:\n
        boss: Boss物件\n
        """
        if boss is None:
            return

        # 轉換Boss座標
        boss_x, boss_y = self._world_to_minimap(
            boss.x + boss.width // 2, boss.y + boss.height // 2  # 使用Boss中心點
        )

        # 繪製Boss點（較大且有特殊效果）
        boss_radius = 6

        # 外圈警告色
        pygame.draw.circle(
            self.minimap_surface, (255, 255, 255), (boss_x, boss_y), boss_radius + 2
        )

        # Boss主體
        pygame.draw.circle(
            self.minimap_surface, self.boss_color, (boss_x, boss_y), boss_radius
        )

        # 內部標記
        pygame.draw.circle(self.minimap_surface, (255, 255, 255), (boss_x, boss_y), 2)

    def _draw_star(self, level_manager):
        """
        繪製勝利星星位置\n
        \n
        參數:\n
        level_manager: 關卡管理器物件\n
        """
        if level_manager.star_collected or not hasattr(level_manager, "star_x"):
            return

        # 轉換星星座標
        star_x, star_y = self._world_to_minimap(
            level_manager.star_x, level_manager.star_y
        )

        # 繪製星星（使用十字形狀）
        star_size = 5

        # 外圈光環
        pygame.draw.circle(
            self.minimap_surface, (255, 255, 255), (star_x, star_y), star_size + 1
        )

        # 星星主體
        pygame.draw.circle(
            self.minimap_surface, self.star_color, (star_x, star_y), star_size
        )

        # 十字標記
        cross_size = 3
        pygame.draw.line(
            self.minimap_surface,
            (255, 255, 255),
            (star_x - cross_size, star_y),
            (star_x + cross_size, star_y),
            2,
        )
        pygame.draw.line(
            self.minimap_surface,
            (255, 255, 255),
            (star_x, star_y - cross_size),
            (star_x, star_y + cross_size),
            2,
        )

    def _draw_legend(self):
        """
        繪製小地圖圖例說明，顯示不同形狀代表的怪物類型\n
        """
        # 圖例起始位置
        legend_x = 5
        legend_y = self.minimap_height - 80

        # 字體（使用較小字體）
        legend_font = get_chinese_font(10)

        # 繪製圖例背景
        legend_bg = pygame.Rect(legend_x - 2, legend_y - 2, 80, 75)
        pygame.draw.rect(self.minimap_surface, (0, 0, 0, 180), legend_bg)
        pygame.draw.rect(self.minimap_surface, (255, 255, 255), legend_bg, 1)

        # 圖例項目
        legend_items = [
            ("player", "玩家", 0),
            ("lava", "岩漿怪", 12),
            ("water", "水怪", 24),
            ("tornado", "風怪", 36),
            ("boss", "Boss", 48),
        ]

        for item_type, text, y_offset in legend_items:
            item_y = legend_y + y_offset

            if item_type == "player":
                # 玩家：綠色圓形
                pygame.draw.circle(
                    self.minimap_surface,
                    self.player_color,
                    (legend_x + 6, item_y + 6),
                    3,
                )
            elif item_type == "lava":
                # 岩漿怪：橘紅色圓形
                pygame.draw.circle(
                    self.minimap_surface,
                    self.monster_colors["lava"],
                    (legend_x + 6, item_y + 6),
                    3,
                )
            elif item_type == "water":
                # 水怪：藍色方形
                pygame.draw.rect(
                    self.minimap_surface,
                    self.monster_colors["water"],
                    (legend_x + 3, item_y + 3, 6, 6),
                )
            elif item_type == "tornado":
                # 風怪：淺藍色三角形
                triangle_points = [
                    (legend_x + 6, item_y + 3),  # 頂點
                    (legend_x + 3, item_y + 9),  # 左下
                    (legend_x + 9, item_y + 9),  # 右下
                ]
                pygame.draw.polygon(
                    self.minimap_surface,
                    self.monster_colors["tornado"],
                    triangle_points,
                )
            elif item_type == "boss":
                # Boss：紫色大圓形
                pygame.draw.circle(
                    self.minimap_surface, self.boss_color, (legend_x + 6, item_y + 6), 4
                )

            # 繪製文字
            text_surface = legend_font.render(text, True, (255, 255, 255))
            self.minimap_surface.blit(text_surface, (legend_x + 15, item_y + 2))

    def update(self, dt=1 / 60):
        """
        更新小地圖（簡化版本，不需要動畫）\n
        \n
        參數:\n
        dt (float): 時間差\n
        """
        # 小地圖不需要動態更新，保持簡潔
        pass

    def draw(self, screen, player, monster_manager, level_manager, dt=1 / 60):
        """
        繪製完整的小地圖\n
        \n
        參數:\n
        screen (pygame.Surface): 主遊戲螢幕\n
        player: 玩家物件\n
        monster_manager: 怪物管理器\n
        level_manager: 關卡管理器\n
        dt (float): 時間差，用於動畫\n
        """
        # 更新動畫（簡化版本）
        self.update(dt)

        # 繪製背景
        self._draw_background()

        # 繪製關卡平台
        platforms = level_manager.get_platforms()
        self._draw_platforms(platforms)

        # 繪製遊戲物件
        self._draw_monsters(monster_manager.monsters)

        if monster_manager.boss:
            self._draw_boss(monster_manager.boss)

        self._draw_star(level_manager)
        self._draw_player(player)

        # 繪製圖例
        self._draw_legend()

        # 將小地圖繪製到主螢幕上
        screen.blit(self.minimap_surface, (self.minimap_x, self.minimap_y))

        # 繪製小地圖標題和拖拽提示
        self._draw_title_and_hints(screen)

    def _draw_title_and_hints(self, screen):
        """
        繪製小地圖標題和拖拽提示\n
        \n
        參數:\n
        screen (pygame.Surface): 主遊戲螢幕\n
        """
        # 繪製小地圖標題
        title_font = get_chinese_font(16)
        title_text = title_font.render("小地圖", True, WHITE)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.minimap_x + self.minimap_width // 2
        title_rect.bottom = self.minimap_y - 5
        screen.blit(title_text, title_rect)

        # 繪製拖拽提示（當滑鼠懸停時）
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if (
            self.minimap_x <= mouse_x <= self.minimap_x + self.minimap_width
            and self.minimap_y <= mouse_y <= self.minimap_y + self.minimap_height
        ):

            hint_font = get_chinese_font(12)
            hint_text = hint_font.render("拖拽移動", True, (255, 255, 255, 200))
            hint_rect = hint_text.get_rect()
            hint_rect.centerx = self.minimap_x + self.minimap_width // 2
            hint_rect.top = self.minimap_y + self.minimap_height + 5
            screen.blit(hint_text, hint_rect)
