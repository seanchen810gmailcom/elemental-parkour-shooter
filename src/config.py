######################遊戲基本設定######################

# 螢幕設定
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 顏色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# 關卡場景顏色
LAVA_COLOR = (255, 80, 0)  # 橘紅色熔岩
WATER_COLOR = (0, 150, 255)  # 藍色水流
WIND_COLOR = (200, 200, 200)  # 灰白色風暴
PLATFORM_COLOR = (100, 50, 0)  # 棕色平台

# UI 相關設定
SCORE_COLOR = WHITE
SCORE_FONT_SIZE = 24
PLATFORM_HEIGHT = 20

######################玩家設定######################

# 玩家基本屬性
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_COLOR = BLUE
PLAYER_SPEED = 8
PLAYER_JUMP_STRENGTH = -20  # 增強跳躍力
PLAYER_MAX_HEALTH = 300  # 大幅提高玩家血量從200到300

# 跑酷相關設定
GRAVITY = 1.2
MAX_FALL_SPEED = 20
WALL_JUMP_STRENGTH = -17  # 增強爬牆跳
WALL_JUMP_PUSH = 12
DOUBLE_JUMP_STRENGTH = -15  # 增強二段跳

######################武器與子彈設定######################

# 槍械基本設定
GUN_RANGE = 300
MELEE_RANGE = 80
BULLET_SPEED = 15
BULLET_SIZE = 8
FIRE_RATE = 0.3  # 發射間隔（秒）

# 子彈屬性顏色
WATER_BULLET_COLOR = CYAN
ICE_BULLET_COLOR = WHITE
THUNDER_BULLET_COLOR = YELLOW
FIRE_BULLET_COLOR = RED

# 子彈屬性傷害
WATER_DAMAGE = 25
ICE_DAMAGE = 20
THUNDER_DAMAGE = 30
FIRE_DAMAGE = 35

# 近戰攻擊設定
MELEE_DAMAGE = 40
MELEE_KNOCKBACK = 100

######################怪物設定######################

# 岩漿怪
LAVA_MONSTER_WIDTH = 50
LAVA_MONSTER_HEIGHT = 50
LAVA_MONSTER_COLOR = RED
LAVA_MONSTER_SPEED = 3
LAVA_MONSTER_HEALTH = 80
LAVA_MONSTER_DAMAGE = 30

# 水怪
WATER_MONSTER_WIDTH = 45
WATER_MONSTER_HEIGHT = 45
WATER_MONSTER_COLOR = BLUE
WATER_MONSTER_SPEED = 5
WATER_MONSTER_HEALTH = 60
WATER_MONSTER_DAMAGE = 25

# 龍捲風怪
TORNADO_MONSTER_WIDTH = 40
TORNADO_MONSTER_HEIGHT = 70
TORNADO_MONSTER_COLOR = (200, 200, 255)  # 淺藍色，不再使用灰色
TORNADO_MONSTER_SPEED = 8
TORNADO_MONSTER_HEALTH = 40
TORNADO_MONSTER_DAMAGE = 35

######################Boss設定######################

# 熔岩龍捲怪 Boss
LAVA_TORNADO_BOSS_WIDTH = 120
LAVA_TORNADO_BOSS_HEIGHT = 150
LAVA_TORNADO_BOSS_COLOR = ORANGE
LAVA_TORNADO_BOSS_SPEED = 4
LAVA_TORNADO_BOSS_HEALTH = 10000  # 提升為2000%（500 × 20）
LAVA_TORNADO_BOSS_DAMAGE = 50

# 海嘯巨獸 Boss
TSUNAMI_BOSS_WIDTH = 150
TSUNAMI_BOSS_HEIGHT = 120
TSUNAMI_BOSS_COLOR = DARK_GRAY
TSUNAMI_BOSS_SPEED = 3
TSUNAMI_BOSS_HEALTH = 12000  # 提升為2000%（600 × 20）
TSUNAMI_BOSS_DAMAGE = 60

######################屬性剋制設定######################

# 剋制倍率
WEAKNESS_MULTIPLIER = 2.0  # 弱點攻擊傷害倍率
RESISTANCE_MULTIPLIER = 0.5  # 抗性攻擊傷害倍率
NORMAL_MULTIPLIER = 1.0  # 一般攻擊傷害倍率

# 狀態效果持續時間（秒）
SLOW_EFFECT_DURATION = 3.0
PARALYSIS_EFFECT_DURATION = 2.0

# 狀態效果強度
SLOW_EFFECT_RATE = 0.5  # 減速至原本的50%
PARALYSIS_EFFECT_RATE = 0.0  # 麻痺時完全無法移動

######################關卡環境設定######################

# 平台設定
PLATFORM_HEIGHT = 30
PLATFORM_COLOR = GRAY

# 陷阱設定
LAVA_TRAP_COLOR = RED
WATER_TRAP_COLOR = BLUE
WIND_TRAP_COLOR = WHITE
TRAP_DAMAGE = 20

# 火山場景
VOLCANO_BG_COLOR = (139, 69, 19)  # 褐色背景
LAVA_COLOR = (255, 69, 0)  # 亮橘紅色

# 海底場景
OCEAN_BG_COLOR = (0, 105, 148)  # 深藍色背景
BUBBLE_COLOR = (173, 216, 230)  # 淺藍色

# 颶風場景
STORM_BG_COLOR = (105, 105, 105)  # 暗灰色背景
WIND_COLOR = (220, 220, 220)  # 亮灰色

######################介面設定######################

# 血量條設定
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_COLOR = GREEN
HEALTH_BAR_BG_COLOR = RED

# 子彈切換介面
BULLET_UI_SIZE = 40
BULLET_UI_SPACING = 50
BULLET_UI_Y = 50

# 分數顯示
SCORE_FONT_SIZE = 36
SCORE_COLOR = WHITE

######################字體設定######################

import pygame
import os

# 繁體中文字體路徑設定
# macOS 系統內建字體路徑
CHINESE_FONTS = [
    "/System/Library/Fonts/STHeiti Light.ttc",  # 黑體-繁（最佳選擇）
    "/System/Library/Fonts/STHeiti Medium.ttc",  # 黑體-中（備選）
    "/System/Library/Fonts/Helvetica.ttc",  # macOS 預設字體（支援部分中文）
    "/Library/Fonts/Microsoft JhengHei.ttf",  # 微軟正黑體
    "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 冬青黑體
    "NotoSansCJK-Regular.ttc",  # Google 思源黑體
    "SimHei.ttf",  # 簡體黑體（也支援繁體）
]

# 字體大小設定
FONT_SIZE_LARGE = 72  # 遊戲結束、勝利標題
FONT_SIZE_MEDIUM = 36  # 分數顯示
FONT_SIZE_NORMAL = 24  # 一般文字
FONT_SIZE_SMALL = 20  # 說明文字
FONT_SIZE_TINY = 16  # 最小文字

# 字體緩存字典，避免重複載入
_font_cache = {}


def get_chinese_font(size):
    """
    獲取支援繁體中文的字體\n
    \n
    此函數會依序嘗試載入繁體中文字體，如果都失敗則使用預設字體\n
    使用緩存機制避免重複載入同樣大小的字體\n
    \n
    參數:\n
    size (int): 字體大小，範圍 > 0\n
    \n
    回傳:\n
    pygame.font.Font: 字體物件，保證不會是 None\n
    \n
    降級策略:\n
    1. 檢查緩存中是否已有相同大小的字體\n
    2. 嘗試載入系統中的繁體中文字體\n
    3. 如果都失敗，使用 pygame 預設字體\n
    4. 確保遊戲能正常運行，即使字體不完美\n
    """
    # 檢查緩存中是否已有這個大小的字體
    if size in _font_cache:
        return _font_cache[size]

    # 確保 pygame 字體模組已初始化
    if not pygame.get_init() or not pygame.font.get_init():
        pygame.font.init()

    font = None

    # 嘗試載入繁體中文字體
    for font_path in CHINESE_FONTS:
        try:
            # 檢查字體檔案是否存在
            if os.path.exists(font_path):
                # 嘗試載入字體
                font = pygame.font.Font(font_path, size)
                print(f"成功載入字體: {font_path} (大小: {size})")
                break
        except (pygame.error, OSError, FileNotFoundError) as e:
            # 字體載入失敗，繼續嘗試下一個
            continue

    # 所有字體都載入失敗，使用預設字體
    if font is None:
        print(f"所有中文字體載入失敗，使用預設字體，大小: {size}")
        font = pygame.font.Font(None, size)

    # 將字體加入緩存
    _font_cache[size] = font
    return font
