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
PLAYER_WIDTH = 60  # 增加寬度 (40 -> 60)
PLAYER_HEIGHT = 90  # 增加高度 (60 -> 90)
PLAYER_COLOR = BLUE
PLAYER_SPEED = 8
PLAYER_JUMP_STRENGTH = -20  # 增強跳躍力
PLAYER_MAX_HEALTH = 800  # 將玩家血量增加為兩倍（從200增加到400）

# 玩家圖片設定
PLAYER_RIGHT_IMAGE_PATH = "素材/maxresdefault.png"  # 玩家向右看的圖片
PLAYER_LEFT_IMAGE_PATH = "素材/maxresdefault拷貝.png"  # 玩家向左看的圖片
PLAYER_IMAGE_SIZE = (PLAYER_WIDTH, PLAYER_HEIGHT)  # 玩家圖片大小

# 跑酷相關設定
GRAVITY = 1.2
MAX_FALL_SPEED = 20
WALL_JUMP_STRENGTH = -17  # 增強爬牆跳
WALL_JUMP_PUSH = 12
DOUBLE_JUMP_STRENGTH = (
    -15
)  # 已棄用：現在三段跳都使用 PLAYER_JUMP_STRENGTH 確保每次跳躍高度一致

# 玩家死亡設定
PLAYER_LIVES = 2  # 玩家總生命次數 - 從3降到2，增加挑戰性
DEATH_RESPAWN_DELAY = 1.0  # 死亡後重生延遲時間（秒）
GAME_OVER_DELAY = 2.0  # 進入遊戲結束畫面的延遲時間（秒）

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

# 甩槍攻擊設定 - 四種武器的甩槍攻擊配置
MELEE_DAMAGE = 120  # 基礎甩槍攻擊力（已棄用，現在使用武器特定設定）
MELEE_KNOCKBACK = 150  # 基礎擊退效果（已棄用，現在使用武器特定設定）

# 各武器甩槍攻擊特性 - 攻擊力比射擊更強，但冷卻時間較長
WEAPON_SWING_CONFIGS = {
    "machine_gun": {
        "damage": 25,  # 機關槍甩擊：攻擊力是射擊的3倍（8 x 3 = 24，調整為25）
        "knockback": 100,  # 中等擊退力
        "range": 70,  # 攻擊範圍較小
        "cooldown": 0.8,  # 冷卻時間較短
    },
    "assault_rifle": {
        "damage": 120,  # 衝鋒槍甩擊：攻擊力是射擊的3倍（40 x 3 = 120）
        "knockback": 180,  # 強力擊退
        "range": 85,  # 攻擊範圍中等
        "cooldown": 1.2,  # 冷卻時間中等
    },
    "shotgun": {
        "damage": 90,  # 散彈槍甩擊：攻擊力是射擊的3.5倍（25 x 3.6 = 90）
        "knockback": 220,  # 最強擊退力（散彈槍本身就是近戰武器）
        "range": 95,  # 攻擊範圍最大
        "cooldown": 1.5,  # 冷卻時間較長
    },
    "sniper": {
        "damage": 200,  # 狙擊槍甩擊：攻擊力是射擊的2.2倍（90 x 2.2 = 198，調整為200）
        "knockback": 250,  # 超強擊退力（狙擊槍重量大）
        "range": 100,  # 攻擊範圍最大（槍最長）
        "cooldown": 2.0,  # 冷卻時間最長
    },
}

######################怪物設定######################

# 岩漿怪
LAVA_MONSTER_WIDTH = 50
LAVA_MONSTER_HEIGHT = 50
LAVA_MONSTER_COLOR = RED
LAVA_MONSTER_SPEED = 2  # 降低移動速度避免被跑酷板卡住（從4降至2）
LAVA_MONSTER_HEALTH = 120  # 提升血量 80→120 (+50%)
LAVA_MONSTER_DAMAGE = 45  # 提升傷害 30→45 (+50%)

# Boss尺寸設定（兩倍大）
BOSS_WIDTH_MULTIPLIER = 2
BOSS_HEIGHT_MULTIPLIER = 2

# 水怪
WATER_MONSTER_WIDTH = 90  # 放大一倍：45 → 90
WATER_MONSTER_HEIGHT = 90  # 放大一倍：45 → 90
WATER_MONSTER_COLOR = BLUE
WATER_MONSTER_SPEED = 3  # 降低移動速度避免被跑酷板卡住（從6降至3）
WATER_MONSTER_HEALTH = 90  # 提升血量 60→90 (+50%)
WATER_MONSTER_DAMAGE = 35  # 提升傷害 25→35 (+40%)

# 龍捲風怪
TORNADO_MONSTER_WIDTH = 40
TORNADO_MONSTER_HEIGHT = 70
TORNADO_MONSTER_COLOR = (200, 200, 255)  # 淺藍色，不再使用灰色
TORNADO_MONSTER_SPEED = 4  # 降低移動速度避免被跑酷板卡住（從10降至4）
TORNADO_MONSTER_HEALTH = 65  # 提升血量 40→65 (+62.5%)
TORNADO_MONSTER_DAMAGE = 50  # 提升傷害 35→50 (+43%)

# 狙擊Boss
SNIPER_BOSS_WIDTH = 130  # 縮小：原本195 → 130 (約67%大小)
SNIPER_BOSS_HEIGHT = 160  # 縮小：原本240 → 160 (約67%大小)
SNIPER_BOSS_COLOR = (150, 0, 150)  # 深紫色
SNIPER_BOSS_SPEED = 3  # 降低移動速度避免被跑酷板卡住（從8降至3）
SNIPER_BOSS_HEALTH = 1500  # 與岩漿Boss相同的血量
SNIPER_BOSS_DAMAGE = 60  # 高攻擊力

######################Boss設定######################

# 熔岩龍捲怪 Boss
LAVA_TORNADO_BOSS_WIDTH = 120
LAVA_TORNADO_BOSS_HEIGHT = 150
LAVA_TORNADO_BOSS_COLOR = ORANGE
LAVA_TORNADO_BOSS_SPEED = 2  # 降低Boss移動速度避免被跑酷板卡住（從5降至2）
LAVA_TORNADO_BOSS_HEALTH = 1500  # 提升Boss血量 1000→1500 (+50%)
LAVA_TORNADO_BOSS_DAMAGE = 75  # 提升Boss傷害 50→75 (+50%)

# 海嘯巨獸 Boss
TSUNAMI_BOSS_WIDTH = 150
TSUNAMI_BOSS_HEIGHT = 120
TSUNAMI_BOSS_COLOR = DARK_GRAY
TSUNAMI_BOSS_SPEED = 2  # 降低Boss移動速度避免被跑酷板卡住（從4降至2）
TSUNAMI_BOSS_HEALTH = 1500  # 提升Boss血量 1000→1500 (+50%)
TSUNAMI_BOSS_DAMAGE = 90  # 提升Boss傷害 60→90 (+50%)

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
TRAP_DAMAGE = 35  # 提升陷阱傷害 20→35 (+75%)

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

# 遊戲結束介面設定
GAME_OVER_TITLE_COLOR = RED
GAME_OVER_TEXT_COLOR = WHITE
GAME_OVER_RETRY_COLOR = YELLOW
GAME_OVER_BG_COLOR = BLACK

# 死亡畫面文字內容
DEATH_TITLE_TEXT = "💀 遊戲結束"
DEATH_RETRY_TEXT = "按 R 重新開始"
DEATH_QUIT_TEXT = "按 ESC 離開遊戲"
DEATH_LIVES_TEXT = "剩餘生命"
DEATH_FINAL_SCORE_TEXT = "最終分數"

######################背景與環境設定######################

# 雲朵系統設定
CLOUD_COUNT = 20  # 總雲朵數量
CLOUD_MIN_SIZE = 0.6  # 最小雲朵大小倍數
CLOUD_MAX_SIZE = 1.8  # 最大雲朵大小倍數
CLOUD_MIN_SPEED = 0.5  # 最小移動速度
CLOUD_MAX_SPEED = 2.0  # 最大移動速度
CLOUD_RESPAWN_DISTANCE = 200  # 雲朵重生距離

# 雲朵圖片設定
CLOUD_IMAGE_PATH = "素材/Cloud.png"  # 雲朵圖片路徑
CLOUD_IMAGE_BASE_SIZE = (100, 60)  # 雲朵圖片基礎大小（寬度, 高度）

# 雲朵系統顏色設定（當圖片載入失敗時的備用顏色）
CLOUD_BACKGROUND_COLOR = (255, 255, 255, 180)  # 背景層雲朵顏色（純白半透明）
CLOUD_FOREGROUND_COLOR = (255, 255, 255, 220)  # 前景層雲朵顏色（純白較不透明）

# 天空背景顏色
SKY_COLOR = (135, 206, 235)  # 天藍色

######################小地圖設定######################

# 小地圖尺寸和位置
MINIMAP_WIDTH = 200  # 小地圖寬度
MINIMAP_HEIGHT = 150  # 小地圖高度
MINIMAP_MARGIN = 15  # 距離螢幕邊緣的間距

# 小地圖顏色設定
MINIMAP_BG_COLOR = (0, 0, 0, 120)  # 半透明黑色背景
MINIMAP_BORDER_COLOR = (255, 255, 255, 200)  # 白色邊框
MINIMAP_PLAYER_COLOR = (0, 255, 0)  # 綠色玩家點
MINIMAP_BOSS_COLOR = (255, 0, 255)  # 紫色Boss點
MINIMAP_STAR_COLOR = (255, 255, 0)  # 黃色星星
MINIMAP_PLATFORM_COLOR = (100, 100, 100)  # 灰色平台

# 小地圖怪物顏色映射
MINIMAP_LAVA_MONSTER_COLOR = (255, 100, 0)  # 橘紅色岩漿怪
MINIMAP_WATER_MONSTER_COLOR = (0, 150, 255)  # 藍色水怪
MINIMAP_TORNADO_MONSTER_COLOR = (200, 200, 255)  # 淺藍色龍捲風怪
MINIMAP_DEFAULT_MONSTER_COLOR = (255, 0, 0)  # 預設紅色

######################狙擊槍準心設定######################

######################Boss子彈設定######################

# Boss子彈速度設定
BOSS_BULLET_SPEED = BULLET_SPEED / 3  # 比狙擊槍子彈慢三倍 (15/3 = 5)
BOSS_BULLET_LIFETIME = 10.0  # Boss子彈生存時間（10秒）
BOSS_BULLET_DAMAGE = 60  # Boss子彈傷害值

# 岩漿Boss子彈設定
LAVA_BOSS_BULLET_INTERVAL = 3.0  # 岩漿Boss每3秒發射一次子彈
LAVA_BOSS_BULLET_COLOR = FIRE_BULLET_COLOR  # 火焰子彈顏色

# 狙擊Boss子彈設定
SNIPER_BOSS_BULLET_INTERVAL = 3.0  # 狙擊Boss每3秒發射一次子彈
SNIPER_BOSS_BULLET_COLOR = PURPLE  # 紫色追蹤子彈
SNIPER_BOSS_TRACKING_SPEED = 0.8  # 追蹤子彈的追蹤速度倍數

######################狙擊槍準心設定######################

# 狙擊槍準心圖片設定
CROSSHAIR_IMAGE_PATH = (
    "素材/—Pngtree—crosshair simple split sight graphics_6809012.png"  # 準心圖片路徑
)
CROSSHAIR_SIZE = 50  # 準心圖片大小（像素）- 適合狙擊槍使用的尺寸
CROSSHAIR_COLOR = (255, 0, 0)  # 備用準心顏色（當圖片載入失敗時使用）

######################機關槍武器設定######################

# 機關槍圖片設定
MACHINE_GUN_IMAGE_PATH = "素材/fad95fd7547c5b8858130e235f96b0b4.png"  # 機關槍圖片路徑
MACHINE_GUN_REVERSE_IMAGE_PATH = "素材/啊哈.png"  # 機關槍反向圖片路徑（往後射擊時使用）
MACHINE_GUN_IMAGE_SIZE = (100, 50)  # 機關槍圖片大小（寬度, 高度）- 放大圖片
MACHINE_GUN_ROTATION_OFFSET = 0  # 圖片旋轉偏移角度，用於對齊槍口

# 正向機關槍槍口偏移（原始圖片）
MACHINE_GUN_MUZZLE_OFFSET_X = 42  # 槍口相對於槍圖片中心的X偏移（往右上角下面一點）
MACHINE_GUN_MUZZLE_OFFSET_Y = -8  # 槍口相對於槍圖片中心的Y偏移（往右上角下面一點）

# 反向機關槍槍口偏移（啊哈.png 圖片）
MACHINE_GUN_REVERSE_MUZZLE_OFFSET_X = -42  # 反向圖片的槍口X偏移（相對於圖片中心）
MACHINE_GUN_REVERSE_MUZZLE_OFFSET_Y = -8  # 反向圖片的槍口Y偏移（相對於圖片中心）

MACHINE_GUN_COLOR = BLACK  # 機關槍備用顏色（當圖片載入失敗時使用）

######################狙擊槍武器設定######################

# 狙擊槍圖片設定
SNIPER_RIFLE_IMAGE_PATH = "素材/20052023635pic_outside_ff97cd246501-removebg-preview.png"  # 狙擊槍正向圖片路徑（往右射擊）
SNIPER_RIFLE_REVERSE_IMAGE_PATH = "素材/哈哈哈.png"  # 狙擊槍反向圖片路徑（往左射擊）
SNIPER_RIFLE_IMAGE_SIZE = (120, 60)  # 狙擊槍圖片大小（寬度, 高度）- 比機關槍稍大
SNIPER_RIFLE_ROTATION_OFFSET = 0  # 圖片旋轉偏移角度，用於對齊槍口

# 正向狙擊槍槍口偏移（往右射擊圖片）
SNIPER_RIFLE_MUZZLE_OFFSET_X = 50  # 槍口相對於槍圖片中心的X偏移（往槍管尖端）
SNIPER_RIFLE_MUZZLE_OFFSET_Y = -5  # 槍口相對於槍圖片中心的Y偏移（槍管中心）

# 反向狙擊槍槍口偏移（往左射擊圖片）
SNIPER_RIFLE_REVERSE_MUZZLE_OFFSET_X = -50  # 反向圖片的槍口X偏移（相對於圖片中心）
SNIPER_RIFLE_REVERSE_MUZZLE_OFFSET_Y = -5  # 反向圖片的槍口Y偏移（相對於圖片中心）

SNIPER_RIFLE_COLOR = RED  # 狙擊槍備用顏色（當圖片載入失敗時使用）

######################散彈槍武器設定######################

# 散彈槍圖片設定
SHOTGUN_IMAGE_PATH = (
    "素材/20052023447pic_outside_d1f490258290.png"  # 散彈槍正向圖片路徑（往右射擊）
)
SHOTGUN_REVERSE_IMAGE_PATH = None  # 反向圖片通過程式鏡像生成
SHOTGUN_IMAGE_SIZE = (110, 55)  # 散彈槍圖片大小（寬度, 高度）- 介於機關槍和狙擊槍之間
SHOTGUN_ROTATION_OFFSET = 0  # 圖片旋轉偏移角度，用於對齊槍口

# 正向散彈槍槍口偏移（往右射擊圖片）
SHOTGUN_MUZZLE_OFFSET_X = 45  # 槍口相對於槍圖片中心的X偏移（往槍管尖端）
SHOTGUN_MUZZLE_OFFSET_Y = -6  # 槍口相對於槍圖片中心的Y偏移（槍管中心）

# 反向散彈槍槍口偏移（鏡像後的槍口位置）
SHOTGUN_REVERSE_MUZZLE_OFFSET_X = -45  # 反向圖片的槍口X偏移（相對於圖片中心）
SHOTGUN_REVERSE_MUZZLE_OFFSET_Y = -6  # 反向圖片的槍口Y偏移（相對於圖片中心）

SHOTGUN_COLOR = RED  # 散彈槍備用顏色（當圖片載入失敗時使用）

# 散彈槍散射設定
SHOTGUN_PELLET_COUNT = 5  # 每次射擊的彈丸數量
SHOTGUN_SPREAD_ANGLE = 1.0  # 散射角度（弧度）
SHOTGUN_DAMAGE_PER_PELLET = 25  # 每顆彈丸的傷害
SHOTGUN_RANGE_MODIFIER = 0.8  # 射程修正（相對於其他武器）

######################衝鋒槍武器設定######################

# 衝鋒槍圖片設定
ASSAULT_RIFLE_IMAGE_PATH = (
    "素材/B&T_APC_9_K_side_profile.png"  # 衝鋒槍正向圖片路徑（往右射擊）
)
ASSAULT_RIFLE_REVERSE_IMAGE_PATH = (
    "素材/B&T_APC_9_K_side_profile拷貝.png"  # 衝鋒槍反向圖片路徑（往左射擊）
)
ASSAULT_RIFLE_IMAGE_SIZE = (
    105,
    55,
)  # 衝鋒槍圖片大小（寬度, 高度）- 介於機關槍和散彈槍之間
ASSAULT_RIFLE_ROTATION_OFFSET = 0  # 圖片旋轉偏移角度，用於對齊槍口

# 正向衝鋒槍槍口偏移（往右射擊圖片）
ASSAULT_RIFLE_MUZZLE_OFFSET_X = 47  # 槍口相對於槍圖片中心的X偏移（往槍管尖端）
ASSAULT_RIFLE_MUZZLE_OFFSET_Y = -5  # 槍口相對於槍圖片中心的Y偏移（槍管中心）

# 反向衝鋒槍槍口偏移（往左射擊圖片）
ASSAULT_RIFLE_REVERSE_MUZZLE_OFFSET_X = -47  # 反向圖片的槍口X偏移（相對於圖片中心）
ASSAULT_RIFLE_REVERSE_MUZZLE_OFFSET_Y = -5  # 反向圖片的槍口Y偏移（相對於圖片中心）

ASSAULT_RIFLE_COLOR = PURPLE  # 衝鋒槍備用顏色（當圖片載入失敗時使用）

######################怪物圖片設定######################

# 怪物圖片檔案路徑
LAVA_MONSTER_IMAGE_PATH = "素材/去背的1.png"  # 小火怪圖片
WATER_MONSTER_IMAGE_PATH = "素材/去背的2.png"  # 小水怪圖片
LAVA_BOSS_IMAGE_PATH = "素材/去背的3.png"  # 岩漿Boss圖片
SNIPER_BOSS_LEFT_IMAGE_PATH = "素材/去背的4.png"  # 狙擊Boss往左看圖片
SNIPER_BOSS_RIGHT_IMAGE_PATH = "素材/去背的4拷貝.png"  # 狙擊Boss往右看圖片

# 怪物圖片大小設定
LAVA_MONSTER_IMAGE_SIZE = (LAVA_MONSTER_WIDTH, LAVA_MONSTER_HEIGHT)  # 小火怪圖片大小
WATER_MONSTER_IMAGE_SIZE = (WATER_MONSTER_WIDTH, WATER_MONSTER_HEIGHT)  # 小水怪圖片大小
LAVA_BOSS_IMAGE_SIZE = (
    LAVA_TORNADO_BOSS_WIDTH,
    LAVA_TORNADO_BOSS_HEIGHT,
)  # 岩漿Boss圖片大小（放大到Boss尺寸）
SNIPER_BOSS_IMAGE_SIZE = (
    SNIPER_BOSS_WIDTH,
    SNIPER_BOSS_HEIGHT,
)  # 狙擊Boss圖片大小（調整後的尺寸）

######################音效設定######################

# 音效檔案路徑
SHOOTING_SOUND_PATH = "素材/attack-laser-128280 (mp3cut.net).mp3"
ULTIMATE_SOUND_PATH = (
    "素材/heavy-thunder-sound-effect-no-copyright-338980.mp3"  # 必殺技雷電音效
)
SNIPER_INCOMING_MUSIC_PATH = "素材/sniper_incoming.mp3"  # 狙擊怪來襲背景音樂
BOSS_MUSIC_PATH = "素材/大怪來襲.wav"  # Boss背景音樂
GAME_OVER_SOUND_PATH = "素材/Game Over.wav"  # 玩家死亡音效
VICTORY_SOUND_PATH = (
    "素材/Stage Win (Super Mario) - QuickSounds.com.mp3"  # 勝利星星音效
)
HEALTH_PICKUP_SOUND_PATH = "素材/吃到寶物.wav"  # 愛心道具音效

# 音效音量設定（0.0 - 1.0）
SHOOTING_SOUND_VOLUME = 0.2  # 射擊音效音量，降低讓必殺技更突出
ULTIMATE_SOUND_VOLUME = 4.0  # 必殺技音效音量，設定為4倍（pygame會限制在1.0但表達意圖）
SNIPER_INCOMING_MUSIC_VOLUME = 2.1  # 狙擊怪來襲音樂音量（3倍大聲）
BOSS_MUSIC_VOLUME = 0.8  # Boss背景音樂音量
GAME_OVER_SOUND_VOLUME = 0.8  # 死亡音效音量，較大聲但不過於震撼
VICTORY_SOUND_VOLUME = 0.9  # 勝利星星音效音量
HEALTH_PICKUP_SOUND_VOLUME = 0.6  # 愛心道具音效音量
MASTER_VOLUME = 0.9  # 主音量

# 音效播放設定
SOUND_CHANNELS = 8  # 同時播放的音效頻道數量，支援機關槍連續射擊

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
