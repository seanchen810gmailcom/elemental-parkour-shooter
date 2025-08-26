######################載入套件######################
import pygame
import random
import time
from config import *
from monsters import LavaMonster, WaterMonster, TornadoMonster

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
        self.spawn_interval = 5.0  # 生成間隔（秒）
        self.max_monsters = 6  # 螢幕上最大怪物數量
        self.wave_number = 1  # 當前波次
        self.monsters_killed = 0  # 擊殺數量

        # 怪物類型比例（隨波次調整）
        self.monster_types = [LavaMonster, WaterMonster, TornadoMonster]
        self.spawn_weights = [1, 1, 1]  # 各類型怪物的生成權重

    def get_spawn_position(self, platforms):
        """
        獲取安全的怪物生成位置\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        \n
        回傳:\n
        tuple: (x, y) 座標，如果找不到安全位置回傳 None\n
        """
        # 嘗試多次找到合適的生成位置
        for _ in range(20):
            # 隨機選擇螢幕邊緣的位置
            if random.choice([True, False]):
                # 從左右兩側生成
                x = random.choice([0, SCREEN_WIDTH - 50])
                y = random.randint(100, SCREEN_HEIGHT - 200)
            else:
                # 從上方生成
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = 0

            # 檢查這個位置是否與平台重疊
            test_rect = pygame.Rect(x, y, 50, 50)
            collision = False

            for platform in platforms:
                if test_rect.colliderect(platform.rect):
                    collision = True
                    break

            if not collision:
                return (x, y)

        # 如果找不到合適位置，使用預設位置
        return (SCREEN_WIDTH - 50, 100)

    def spawn_monster(self, platforms):
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
        spawn_pos = self.get_spawn_position(platforms)
        if spawn_pos is None:
            return None

        # 根據權重隨機選擇怪物類型
        monster_class = random.choices(self.monster_types, weights=self.spawn_weights)[
            0
        ]

        # 生成怪物
        new_monster = monster_class(spawn_pos[0], spawn_pos[1])

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

        # 根據波次調整生成間隔
        current_interval = max(2.0, self.spawn_interval - (self.wave_number - 1) * 0.2)

        if self.spawn_timer >= current_interval:
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
        return killed_count

    def check_wave_completion(self):
        """
        檢查是否應該進入下一波\n
        \n
        回傳:\n
        bool: True 表示應該進入下一波\n
        """
        # 每擊殺10個怪物進入下一波
        target_kills = self.wave_number * 10

        if self.monsters_killed >= target_kills:
            self.advance_to_next_wave()
            return True

        return False

    def advance_to_next_wave(self):
        """
        進入下一波 - 調整難度和怪物生成規則\n
        """
        self.wave_number += 1

        # 每3波增加最大怪物數量
        if self.wave_number % 3 == 0:
            self.max_monsters = min(10, self.max_monsters + 1)

        # 調整怪物類型權重
        if self.wave_number >= 3:
            # 第3波開始，龍捲風怪出現更頻繁
            self.spawn_weights = [1, 1, 2]

        if self.wave_number >= 5:
            # 第5波開始，所有怪物權重相等，但數量更多
            self.spawn_weights = [2, 2, 2]

        # 重設生成計時器，立即生成一波怪物
        self.spawn_timer = self.spawn_interval

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

        # 移除死亡怪物
        killed_this_frame = self.remove_dead_monsters()

        # 檢查波次完成
        wave_advanced = self.check_wave_completion()

        # 更新生成計時器並嘗試生成新怪物
        new_monster = None
        if self.update_spawn_timer(dt):
            new_monster = self.spawn_monster(platforms)

        return {
            "monsters_killed": killed_this_frame,
            "wave_advanced": wave_advanced,
            "new_monster": new_monster is not None,
            "current_wave": self.wave_number,
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
