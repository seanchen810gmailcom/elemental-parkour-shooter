######################載入套件######################
import pygame
import random
import time

# 支援直接執行和模組執行兩種方式
try:
    from ..config import *
    from ..entities.monsters import LavaMonster, WaterMonster, TornadoMonster
except ImportError:
    from src.config import *
    from src.entities.monsters import LavaMonster, WaterMonster, TornadoMonster

######################怪物管理器類別######################


class MonsterManager:
    """
    怪物管理器 - 統一管理所有怪物的生成、更新和互動\n
    \n
    負責：\n
    1. 怪物的生成和銷毀\n
    2. 怪物 AI 的統一更新\n
    3. 怪物與玩家、子彈的碰撞檢測\n
    4. 關卡難度調整和怪物波次管理\n
    """

    def __init__(self):
        self.monsters = []  # 所有活躍怪物列表
        self.spawn_timer = 0
        self.spawn_interval = 4.0  # 生成間隔（秒）- 固定為4秒
        self.max_monsters = 6  # 螢幕上最大怪物數量
        self.wave_number = 1  # 當前波次
        self.monsters_killed = 0  # 擊殺數量
        self.boss_spawned = False  # Boss是否已生成
        self.boss = None  # Boss實例

        # 怪物類型比例（隨波次調整）
        self.monster_types = [LavaMonster, WaterMonster, TornadoMonster]
        self.spawn_weights = [1, 1, 1]  # 各類型怪物的生成權重

    def get_ground_platform(self, platforms):
        """
        獲取地面平台（最下層平台）\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        Platform or None: 地面平台物件，如果找不到回傳 None\n
        """
        # 找到最下層的平台（y座標最大的平台）
        ground_platform = None
        max_y = -1

        for platform in platforms:
            if platform.y > max_y and platform.width >= 100:  # 確保是夠大的平台
                max_y = platform.y
                ground_platform = platform

        return ground_platform

    def get_spawn_position(self, platforms):
        """
        獲取安全的怪物生成位置（只在最下層地面平台）\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        tuple: (x, y, platform) 座標和平台物件，如果找不到安全位置回傳 None\n
        """
        # 只在地面平台生成怪物
        ground_platform = self.get_ground_platform(platforms)

        if ground_platform is None:
            return None

        # 在地面平台上隨機選擇位置，確保怪物不會掉下去
        margin = 50  # 距離平台邊緣的安全距離
        monster_width = 50  # 怪物寬度

        # 計算安全的生成範圍
        min_x = int(ground_platform.x + margin)
        max_x = int(ground_platform.x + ground_platform.width - margin - monster_width)

        # 確保範圍有效
        if max_x <= min_x:
            # 如果平台太小，就在平台中央生成
            spawn_x = int(ground_platform.x + ground_platform.width // 2)
        else:
            spawn_x = random.randint(min_x, max_x)
        spawn_y = ground_platform.y - 60  # 在平台上方生成

        return (spawn_x, spawn_y, ground_platform)

    def spawn_monster(self, platforms, player):
        """
        生成新怪物\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        Monster or None: 新生成的怪物，失敗時回傳 None\n
        """
        if len(self.monsters) >= self.max_monsters:
            return None

        # 獲取生成位置
        spawn_result = self.get_spawn_position(platforms)
        if spawn_result is None:
            return None

        spawn_x, spawn_y, platform = spawn_result

        # 根據權重隨機選擇怪物類型
        monster_class = random.choices(self.monster_types, weights=self.spawn_weights)[
            0
        ]

        # 生成怪物
        new_monster = monster_class(spawn_x, spawn_y)

        # 記錄怪物所在的平台，防止掉落
        new_monster.home_platform = platform

        # 根據波次調整怪物屬性
        self.adjust_monster_stats(new_monster)

        self.monsters.append(new_monster)
        return new_monster

    def adjust_monster_stats(self, monster):
        """
        根據當前波次調整怪物屬性\n
        \n
        參數:\n
        monster (Monster): 要調整的怪物\n
        """
        # 每波增加10%的生命值和5%的攻擊力
        health_multiplier = 1.0 + (self.wave_number - 1) * 0.1
        damage_multiplier = 1.0 + (self.wave_number - 1) * 0.05

        monster.max_health = int(monster.max_health * health_multiplier)
        monster.health = monster.max_health
        monster.damage = int(monster.damage * damage_multiplier)

    def update_spawn_timer(self, dt):
        """
        更新怪物生成計時器\n
        \n
        參數:\n
        dt (float): 距離上次更新的時間（秒）\n
        """
        self.spawn_timer += dt

        # 固定每4秒生成一隻怪物
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            return True  # 該生成新怪物了

        return False

    def remove_dead_monsters(self):
        """
        移除死亡的怪物並計算擊殺數\n
        \n
        回傳:\n
        int: 本次移除的怪物數量\n
        """
        killed_count = 0
        alive_monsters = []

        for monster in self.monsters:
            if monster.is_alive:
                alive_monsters.append(monster)
            else:
                killed_count += 1
                self.monsters_killed += 1

        self.monsters = alive_monsters

        # 檢查Boss是否死亡
        if self.boss and not self.boss.is_alive:
            killed_count += 1
            # Boss死亡不增加擊殺計數，因為它是特殊目標

        return killed_count

    def check_boss_spawn_condition(self):
        """
        檢查是否應該生成Boss\n
        \n
        回傳:\n
        bool: True 表示應該生成Boss\n
        """
        # 每擊殺10個怪物生成一次Boss
        if self.monsters_killed >= 10 and not self.boss_spawned:
            return True
        return False

    def spawn_boss(self, platforms):
        """
        生成Boss怪物\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        Boss or None: 新生成的Boss，失敗時回傳 None\n
        """
        if self.boss_spawned or self.boss is not None:
            return None

        # 獲取Boss生成位置（在較大的平台上）
        spawn_result = self.get_spawn_position(platforms)
        if spawn_result is None:
            return None

        spawn_x, spawn_y, platform = spawn_result

        # 創建Boss（使用LavaMonster作為基礎，但增強屬性）
        self.boss = LavaMonster(spawn_x, spawn_y)

        # Boss血量是一般怪物的7倍
        self.boss.max_health = LAVA_MONSTER_HEALTH * 7
        self.boss.health = self.boss.max_health

        # Boss攻擊力稍微提升
        self.boss.damage = LAVA_MONSTER_DAMAGE * 1.5

        # Boss每3秒射擊一次
        self.boss.lava_ball_cooldown = 3.0

        # 設定Boss標記
        self.boss.is_boss = True
        self.boss.monster_type = "boss_lava_monster"

        # Boss所在平台
        self.boss.home_platform = platform

        self.boss_spawned = True
        print("🔥 Boss 岩漿怪王 出現！血量是一般怪物的7倍！")
        return self.boss

    def update(self, player, platforms, dt):
        """
        更新所有怪物和管理器狀態\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        dt (float): 距離上次更新的時間（秒）\n
        \n
        回傳:\n
        dict: 更新結果資訊\n
        """
        # 更新所有活躍怪物
        for monster in self.monsters:
            monster.update(player, platforms)

        # 更新Boss（如果存在）
        if self.boss:
            self.boss.update(player, platforms)

        # 移除死亡怪物（包含Boss）
        killed_this_frame = self.remove_dead_monsters()

        # 檢查是否需要生成Boss
        boss_spawned = False
        if self.check_boss_spawn_condition():
            new_boss = self.spawn_boss(platforms)
            if new_boss:
                boss_spawned = True

        # 檢查Boss是否被擊敗
        boss_defeated = False
        if self.boss and not self.boss.is_alive:
            print("🎉 Boss已被擊敗！遊戲即將結束！")
            boss_defeated = True
            self.boss = None

        # 更新生成計時器並嘗試生成新怪物（如果沒有Boss）
        new_monster = None
        if not self.boss_spawned and self.update_spawn_timer(dt):
            new_monster = self.spawn_monster(platforms, player)

        return {
            "monsters_killed": killed_this_frame,
            "boss_spawned": boss_spawned,
            "boss_defeated": boss_defeated,
            "new_monster": new_monster is not None,
            "total_killed": self.monsters_killed,
        }

    def get_monsters_in_range(self, x, y, range_distance):
        """
        獲取指定範圍內的怪物\n
        \n
        參數:\n
        x (float): 中心點 X 座標\n
        y (float): 中心點 Y 座標\n
        range_distance (float): 搜尋半徑\n
        \n
        回傳:\n
        list: 範圍內的怪物列表\n
        """
        monsters_in_range = []

        for monster in self.monsters:
            if not monster.is_alive:
                continue

            # 計算距離
            dx = monster.x - x
            dy = monster.y - y
            distance = (dx**2 + dy**2) ** 0.5

            if distance <= range_distance:
                monsters_in_range.append(monster)

        return monsters_in_range

    def get_closest_monster(self, x, y):
        """
        獲取最近的怪物\n
        \n
        參數:\n
        x (float): 參考點 X 座標\n
        y (float): 參考點 Y 座標\n
        \n
        回傳:\n
        Monster or None: 最近的怪物\n
        """
        closest_monster = None
        closest_distance = float("inf")

        for monster in self.monsters:
            if not monster.is_alive:
                continue

            dx = monster.x - x
            dy = monster.y - y
            distance = (dx**2 + dy**2) ** 0.5

            if distance < closest_distance:
                closest_distance = distance
                closest_monster = monster

        return closest_monster

    def clear_all_monsters(self):
        """
        清除所有怪物 - 用於關卡重置\n
        """
        self.monsters.clear()
        self.spawn_timer = 0
        self.wave_number = 1
        self.monsters_killed = 0
        self.max_monsters = 6
        self.spawn_weights = [1, 1, 1]

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有怪物\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        for monster in self.monsters:
            monster.draw(screen, camera_x, camera_y)

        # 繪製Boss（如果存在）
        if self.boss:
            self.boss.draw(screen, camera_x, camera_y)

            # 特別標示Boss
            boss_screen_x = self.boss.x - camera_x
            boss_screen_y = self.boss.y - camera_y

            # 在Boss上方顯示"BOSS"文字
            font = get_chinese_font(FONT_SIZE_MEDIUM)
            boss_text = font.render("BOSS", True, RED)
            text_rect = boss_text.get_rect()
            text_rect.centerx = boss_screen_x + self.boss.width // 2
            text_rect.bottom = boss_screen_y - 10
            screen.blit(boss_text, text_rect)

    def get_monster_count(self):
        """
        獲取當前活躍怪物數量\n
        \n
        回傳:\n
        int: 活躍怪物數量\n
        """
        return len([monster for monster in self.monsters if monster.is_alive])

    def get_monster_stats(self):
        """
        獲取怪物統計資訊\n
        \n
        回傳:\n
        dict: 統計資訊\n
        """
        alive_count = self.get_monster_count()
        type_counts = {"lava": 0, "water": 0, "tornado": 0}

        for monster in self.monsters:
            if monster.is_alive:
                if monster.monster_type == "lava_monster":
                    type_counts["lava"] += 1
                elif monster.monster_type == "water_monster":
                    type_counts["water"] += 1
                elif monster.monster_type == "tornado_monster":
                    type_counts["tornado"] += 1

        return {
            "total_alive": alive_count,
            "total_killed": self.monsters_killed,
            "current_wave": self.wave_number,
            "type_counts": type_counts,
            "max_monsters": self.max_monsters,
        }

    def reset_for_new_level(self):
        """
        為新關卡重置怪物管理器\n
        \n
        清除所有現有怪物，重置計時器和統計\n
        """
        # 清除所有怪物
        self.monsters.clear()

        # 重置計時器和計數器
        self.spawn_timer = 0
        self.monsters_killed = 0

        # 保持當前波次但可選擇重置
        # self.wave_number = 1  # 如果要重置波次的話

        print(f"🔄 怪物系統已為新關卡重置")

    def clear_all_monsters(self):
        """
        清除所有怪物\n
        """
        self.monsters.clear()
        print("🧹 已清除所有怪物")
