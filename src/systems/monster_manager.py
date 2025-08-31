######################載入套件######################
import pygame
import random
import time

# 支援直接執行和模組執行兩種方式
try:
    from ..config import *
    from ..entities.monsters import LavaMonster, WaterMonster, SniperBoss
except ImportError:
    from src.config import *
    from src.entities.monsters import LavaMonster, WaterMonster, SniperBoss

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
        self.spawn_interval = 2.5  # 生成間隔（秒）- 從4秒縮短到2.5秒，提升40%生成頻率
        self.max_monsters = 9  # 螢幕上最大怪物數量 - 從6增加到9
        self.wave_number = 1  # 當前波次
        self.monsters_killed = 0  # 擊殺數量
        self.boss_spawned = False  # Boss是否已生成
        self.boss = None  # Boss實例
        self.boss_stage = 1  # Boss階段：1=岩漿Boss, 2=狙擊Boss
        self.boss_transition_timer = 0  # Boss轉換延遲計時器
        self.boss_transition_delay = 3.0  # Boss轉換延遲時間（3秒）
        self.waiting_for_boss_transition = False  # 是否正在等待Boss轉換

        # 怪物類型比例（隨波次調整）- 移除粉紫色怪物TornadoMonster
        self.monster_types = [LavaMonster, WaterMonster]  # 只保留熔岩怪和水怪
        self.spawn_weights = [1, 1]  # 各類型怪物的生成權重

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

    def get_spawn_position(self, platforms, player):
        """
        獲取安全的怪物生成位置（在玩家視窗範圍內但不在玩家身上）\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        player (Player): 玩家物件，用於計算視窗範圍\n
        \n
        回傳:\n
        tuple: (x, y, platform) 座標和平台物件，如果找不到安全位置回傳 None\n
        """
        # 計算玩家當前視窗範圍
        player_center_x = player.x + player.width // 2
        player_center_y = player.y + player.height // 2

        # 視窗範圍（以玩家為中心）
        view_left = player_center_x - SCREEN_WIDTH // 2
        view_right = player_center_x + SCREEN_WIDTH // 2
        view_top = player_center_y - SCREEN_HEIGHT // 2
        view_bottom = player_center_y + SCREEN_HEIGHT // 2

        # 玩家安全距離（怪物不能在玩家太近的地方出生）
        safe_distance = 100

        # 在視窗範圍內尋找合適的平台
        suitable_platforms = []

        for platform in platforms:
            # 檢查平台是否在視窗範圍內
            platform_in_view = (
                platform.x + platform.width > view_left
                and platform.x < view_right
                and platform.y + platform.height > view_top
                and platform.y < view_bottom
            )

            if platform_in_view and platform.width >= 80:  # 確保平台夠大
                suitable_platforms.append(platform)

        # 如果沒有合適的平台，回傳 None
        if not suitable_platforms:
            return None

        # 嘗試在合適平台上找到安全的生成點
        max_attempts = 10
        for _ in range(max_attempts):
            # 隨機選擇一個平台
            platform = random.choice(suitable_platforms)

            # 在平台上隨機選擇位置
            margin = 30  # 距離平台邊緣的安全距離
            monster_width = 50  # 怪物寬度

            # 計算安全的生成範圍
            min_x = int(platform.x + margin)
            max_x = int(platform.x + platform.width - margin - monster_width)

            # 確保範圍有效
            if max_x <= min_x:
                # 如果平台太小，就在平台中央生成
                spawn_x = int(platform.x + platform.width // 2)
            else:
                spawn_x = random.randint(min_x, max_x)

            spawn_y = platform.y - 60  # 在平台上方生成

            # 檢查是否離玩家夠遠
            dx = spawn_x - player_center_x
            dy = spawn_y - player_center_y
            distance_to_player = (
                dx * dx + dy * dy
            ) ** 0.5  # 使用簡單的開根號避免依賴math

            if distance_to_player >= safe_distance:
                return (spawn_x, spawn_y, platform)

        # 如果找不到安全距離的位置，就選擇最遠的平台
        if suitable_platforms:
            farthest_platform = None
            max_distance = 0

            for platform in suitable_platforms:
                platform_center_x = platform.x + platform.width // 2
                platform_center_y = platform.y

                dx = platform_center_x - player_center_x
                dy = platform_center_y - player_center_y
                distance = (dx * dx + dy * dy) ** 0.5  # 使用簡單的開根號避免依賴math

                if distance > max_distance:
                    max_distance = distance
                    farthest_platform = platform

            if farthest_platform:
                spawn_x = int(farthest_platform.x + farthest_platform.width // 2)
                spawn_y = farthest_platform.y - 60
                return (spawn_x, spawn_y, farthest_platform)

        return None

    def spawn_monster(self, platforms, player):
        """
        生成新怪物\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        Monster or None: 新生成的怪物，失敗時回傳 None\n
        """
        if len(self.monsters) >= self.max_monsters:
            return None

        # 獲取生成位置（傳入player參數）
        spawn_result = self.get_spawn_position(platforms, player)
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
        # 每波增加15%的生命值和8%的攻擊力（原本10%和5%）
        health_multiplier = 1.0 + (self.wave_number - 1) * 0.15
        damage_multiplier = 1.0 + (self.wave_number - 1) * 0.08

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

        # 固定每2.5秒生成一隻怪物（提升生成頻率）
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
            # 清理Boss的火焰子彈
            if hasattr(self.boss, "fire_bullets"):
                self.boss.fire_bullets.clear()
            # Boss死亡不增加擊殺計數，因為它是特殊目標

        return killed_count

    def check_boss_spawn_condition(self):
        """
        檢查是否應該生成Boss\n
        \n
        回傳:\n
        bool: True 表示應該生成Boss\n
        """
        # Boss必須等玩家擊敗10個小怪後才能出現
        if self.monsters_killed < 10:
            return False

        # 第一階段：岩漿Boss
        if self.boss_stage == 1 and not self.boss_spawned:
            return True

        # 第二階段：狙擊Boss（需要等待轉換延遲）
        elif (
            self.boss_stage == 2
            and not self.boss_spawned
            and not self.waiting_for_boss_transition
        ):
            return True

        return False

    def spawn_boss(self, platforms, player):
        """
        生成Boss怪物 - 根據階段生成不同Boss\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        player (Player): 玩家物件\n
        \n
        回傳:\n
        Boss or None: 新生成的Boss，失敗時回傳 None\n
        """
        if self.boss_spawned or self.boss is not None:
            return None

        # 獲取Boss生成位置（在較大的平台上）
        spawn_result = self.get_spawn_position(platforms, player)
        if spawn_result is None:
            return None

        spawn_x, spawn_y, platform = spawn_result

        # 根據Boss階段生成不同類型的Boss
        if self.boss_stage == 1:
            # 第一階段：岩漿Boss
            self.boss = LavaMonster(spawn_x, spawn_y, allow_platform_collision=False)

            # 調整Boss體積為兩倍大
            self.boss.width = LAVA_MONSTER_WIDTH * BOSS_WIDTH_MULTIPLIER
            self.boss.height = LAVA_MONSTER_HEIGHT * BOSS_HEIGHT_MULTIPLIER

            # 重新調整Boss位置，確保它站在地面上而不是穿透
            self.boss.y = platform.y - self.boss.height

            # 重新載入Boss大小的圖片
            if hasattr(self.boss, "reload_image_if_boss"):
                self.boss.reload_image_if_boss()

            # 更新Boss的碰撞矩形大小（修復子彈碰撞問題）
            self.boss.update_rect()

            # Boss血量設定為1500（提升難度）
            self.boss.max_health = 1500
            self.boss.health = self.boss.max_health

            # Boss攻擊力大幅提升
            self.boss.damage = LAVA_MONSTER_DAMAGE * 2.0

            # Boss射擊頻率更高（從1.5秒改為1.0秒）
            self.boss.lava_ball_cooldown = 1.0

            # 為岩漿Boss添加回血機制
            self.boss.heal_cooldown = 5.0  # 每5秒回血一次
            self.boss.last_heal_time = 0
            self.boss.heal_amount = 2  # 每次回血2點

            # 添加火焰子彈功能 - 提升攻擊頻率
            self.boss.fire_bullet_cooldown = LAVA_BOSS_BULLET_INTERVAL  # 改為3秒間隔
            self.boss.last_fire_bullet_time = 0
            self.boss.fire_bullets = []

            # 設定為Boss（重要：啟用永久追蹤）
            self.boss.is_boss = True
            self.boss.monster_type = "boss_lava_monster"
            print(f"🔥 第一階段Boss - 岩漿怪王 出現！血量是一般怪物的3倍！")

        elif self.boss_stage == 2:
            # 第二階段：狙擊Boss
            self.boss = SniperBoss(spawn_x, spawn_y, allow_platform_collision=False)

            # 為狙擊Boss添加新的子彈系統
            self.boss.new_bullet_cooldown = SNIPER_BOSS_BULLET_INTERVAL  # 3秒間隔
            self.boss.last_new_bullet_time = 0
            self.boss.boss_bullets = []  # 新的Boss子彈系統

            print(f"🎯 最終Boss - 狙擊Boss已生成！具備追蹤子彈、震波攻擊和躲避能力！")

            # 狙擊Boss出現時同時生成3個額外小怪
            self.spawn_additional_monsters_for_sniper_boss(platforms, player)

        # 共同Boss設定
        self.boss.is_boss = True
        self.boss.home_platform = platform
        self.boss_spawned = True

        return self.boss

    def spawn_additional_monsters_for_sniper_boss(self, platforms, player):
        """
        為狙擊Boss清除多餘小怪並保留3個小怪\n
        \n
        參數:\n
        platforms (list): 平台列表\n
        player (Player): 玩家物件\n
        """
        # 先統計當前活著的小怪數量
        alive_monsters = [monster for monster in self.monsters if monster.is_alive]
        current_monster_count = len(alive_monsters)
        
        print(f"🎯 狙擊Boss出現前，場上有 {current_monster_count} 個小怪")
        
        # 如果小怪數量超過3個，只保留3個，其餘移除
        if current_monster_count > 3:
            # 隨機選擇3個小怪保留，其他的標記為死亡
            monsters_to_keep = random.sample(alive_monsters, 3)
            
            # 將不在保留清單中的小怪標記為死亡
            removed_count = 0
            for monster in alive_monsters:
                if monster not in monsters_to_keep:
                    monster.is_alive = False
                    removed_count += 1
            
            print(f"🧹 移除了 {removed_count} 個小怪，保留 3 個小怪")
        
        # 如果小怪數量不足3個，補充到3個
        elif current_monster_count < 3:
            needed_monsters = 3 - current_monster_count
            spawned_count = 0
            
            for _ in range(needed_monsters):
                # 獲取生成位置
                spawn_result = self.get_spawn_position(platforms, player)
                if spawn_result is None:
                    continue

                spawn_x, spawn_y, platform = spawn_result

                # 隨機選擇怪物類型
                monster_class = random.choice(self.monster_types)
                new_monster = monster_class(spawn_x, spawn_y)

                # 設定怪物所在平台
                new_monster.home_platform = platform

                # 根據波次調整怪物屬性
                self.adjust_monster_stats(new_monster)

                self.monsters.append(new_monster)
                spawned_count += 1
            
            print(f"➕ 補充了 {spawned_count} 個小怪")
        
        else:
            print(f"✅ 場上剛好有 3 個小怪，無需調整")
        
        # 最終確認
        final_alive_count = len([monster for monster in self.monsters if monster.is_alive])
        print(f"🎯 狙擊Boss出現後，場上確保有 {final_alive_count} 個小怪！")

    def update(self, player, platforms, dt, bullets=None, level_width=None):
        """
        更新所有怪物和管理器狀態\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        platforms (list): 平台列表\n
        dt (float): 距離上次更新的時間（秒）\n
        bullets (list): 玩家子彈列表（可選，用於Boss躲避）\n
        level_width (int): 關卡實際寬度\n
        \n
        回傳:\n
        dict: 更新結果資訊\n
        """
        # 更新所有活躍怪物，傳遞關卡寬度
        for monster in self.monsters:
            monster.update(player, platforms, level_width)

        # 更新Boss（如果存在）
        if self.boss:
            # 如果是狙擊Boss，需要傳入子彈資訊
            if hasattr(self.boss, "tracking_bullets"):  # 狙擊Boss的標識
                self.boss.update(player, platforms, bullets, level_width)
            else:
                self.boss.update(player, platforms, level_width)

            # 處理岩漿Boss的火焰子彈邏輯（只針對岩漿Boss）
            if hasattr(self.boss, "fire_bullets"):
                self.update_boss_fire_bullets(player)

        # 移除死亡怪物（包含Boss）
        killed_this_frame = self.remove_dead_monsters()

        # 檢查是否需要生成Boss
        boss_spawned = False
        if self.check_boss_spawn_condition():
            new_boss = self.spawn_boss(platforms, player)
            if new_boss:
                boss_spawned = True

        # 檢查Boss是否被擊敗
        boss_defeated = False
        boss_death_x = 0
        boss_death_y = 0
        sniper_boss_defeated = False  # 狙擊Boss是否被擊敗（觸發勝利）

        if self.boss and not self.boss.is_alive:
            boss_type = (
                "狙擊Boss" if hasattr(self.boss, "tracking_bullets") else "岩漿Boss"
            )
            boss_death_x = self.boss.x
            boss_death_y = self.boss.y

            if self.boss_stage == 1:
                # 岩漿Boss被擊敗，啟動轉換延遲機制
                print(f"🔥 第一階段Boss已被擊敗！將在3秒後出現最終Boss...")
                self.boss_stage = 2
                self.boss_spawned = False  # 重置以生成下一階段Boss
                self.waiting_for_boss_transition = True  # 開始等待轉換
                self.boss_transition_timer = 0  # 重置轉換計時器
                boss_defeated = False  # 不觸發勝利

            elif self.boss_stage == 2:
                # 狙擊Boss被擊敗，真正的勝利
                print(f"🎉 最終Boss - 狙擊Boss已被擊敗！真正的勝利！")
                boss_defeated = True
                sniper_boss_defeated = True

            self.boss = None

        # 處理Boss轉換延遲
        if self.waiting_for_boss_transition:
            self.boss_transition_timer += dt
            if self.boss_transition_timer >= self.boss_transition_delay:
                # 轉換延遲結束，可以生成狙擊Boss
                self.waiting_for_boss_transition = False
                print(f"⏰ Boss轉換延遲結束，狙擊Boss可以生成了！")

        # 更新生成計時器並嘗試生成新怪物（Boss存在時也繼續生成普通怪物）
        new_monster = None
        if self.update_spawn_timer(dt):
            new_monster = self.spawn_monster(platforms, player)

        return {
            "monsters_killed": killed_this_frame,
            "boss_spawned": boss_spawned,
            "boss_defeated": boss_defeated,
            "sniper_boss_defeated": sniper_boss_defeated,  # 新增：狙擊Boss擊敗標記
            "boss_death_x": boss_death_x,
            "boss_death_y": boss_death_y,
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
        self.spawn_weights = [1, 1]

    def create_boss_fire_bullet(self, target_x, target_y):
        """
        創建Boss火焰子彈\n
        \n
        參數:\n
        target_x (float): 目標 X 座標\n
        target_y (float): 目標 Y 座標\n
        \n
        回傳:\n
        dict or None: 火焰子彈資訊\n
        """
        if not self.boss or not hasattr(self.boss, "fire_bullet_cooldown"):
            return None

        current_time = time.time()
        if (
            current_time - self.boss.last_fire_bullet_time
            < self.boss.fire_bullet_cooldown
        ):
            return None

        # 計算發射方向
        start_x = self.boss.x + self.boss.width // 2
        start_y = self.boss.y + self.boss.height // 2

        dx = target_x - start_x
        dy = target_y - start_y
        distance = (dx**2 + dy**2) ** 0.5

        if distance > 0:
            direction_x = dx / distance
            direction_y = dy / distance

            fire_bullet = {
                "x": start_x,
                "y": start_y,
                "velocity_x": direction_x * BOSS_BULLET_SPEED,  # 使用新的Boss子彈速度
                "velocity_y": direction_y * BOSS_BULLET_SPEED,
                "damage": BOSS_BULLET_DAMAGE,  # 使用新的Boss子彈傷害
                "lifetime": BOSS_BULLET_LIFETIME,  # 10秒生存時間
                "created_time": current_time,
                "bullet_type": "lava_boss",  # 標記為岩漿Boss子彈
            }

            self.boss.fire_bullets.append(fire_bullet)
            self.boss.last_fire_bullet_time = current_time
            return fire_bullet

        return None

    def create_sniper_boss_tracking_bullet(self, target_x, target_y):
        """
        創建狙擊Boss追蹤子彈\n
        \n
        參數:\n
        target_x (float): 目標 X 座標\n
        target_y (float): 目標 Y 座標\n
        \n
        回傳:\n
        dict or None: 追蹤子彈資訊\n
        """
        if not self.boss or not hasattr(self.boss, "new_bullet_cooldown"):
            return None

        current_time = time.time()
        if (
            current_time - self.boss.last_new_bullet_time
            < self.boss.new_bullet_cooldown
        ):
            return None

        # 計算發射方向
        start_x = self.boss.x + self.boss.width // 2
        start_y = self.boss.y + self.boss.height // 2

        dx = target_x - start_x
        dy = target_y - start_y
        distance = (dx**2 + dy**2) ** 0.5

        if distance > 0:
            direction_x = dx / distance
            direction_y = dy / distance

            tracking_bullet = {
                "x": start_x,
                "y": start_y,
                "velocity_x": direction_x * BOSS_BULLET_SPEED,  # 使用Boss子彈速度
                "velocity_y": direction_y * BOSS_BULLET_SPEED,
                "target_x": target_x,  # 追蹤目標
                "target_y": target_y,
                "damage": BOSS_BULLET_DAMAGE,  # 使用Boss子彈傷害
                "lifetime": BOSS_BULLET_LIFETIME,  # 10秒生存時間
                "created_time": current_time,
                "bullet_type": "sniper_boss_tracking",  # 標記為狙擊Boss追蹤子彈
                "tracking_strength": SNIPER_BOSS_TRACKING_SPEED,  # 追蹤強度
            }

            self.boss.boss_bullets.append(tracking_bullet)
            self.boss.last_new_bullet_time = current_time
            print(f"🎯 狙擊Boss發射追蹤子彈！")
            return tracking_bullet

        return None

    def update_boss_fire_bullets(self, player):
        """
        更新Boss火焰子彈和狙擊Boss追蹤子彈狀態並檢查碰撞\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        if not self.boss:
            return

        # 處理岩漿Boss的火焰子彈（舊系統）
        if hasattr(self.boss, "fire_bullets"):
            self.update_lava_boss_fire_bullets(player)

        # 處理狙擊Boss的追蹤子彈（新系統）
        if hasattr(self.boss, "boss_bullets"):
            self.update_sniper_boss_bullets(player)

    def update_lava_boss_fire_bullets(self, player):
        """
        更新岩漿Boss火焰子彈狀態\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        current_time = time.time()
        active_bullets = []

        for bullet in self.boss.fire_bullets:
            # 檢查生存時間
            if current_time - bullet["created_time"] > bullet["lifetime"]:
                continue

            # 更新位置
            bullet["x"] += bullet["velocity_x"]
            bullet["y"] += bullet["velocity_y"]

            # 檢查與玩家的碰撞
            bullet_rect = pygame.Rect(bullet["x"] - 8, bullet["y"] - 8, 16, 16)
            if bullet_rect.colliderect(player.rect):
                # 火焰子彈擊中玩家
                player.take_damage(bullet["damage"])
                print(f"🔥 Boss火焰子彈擊中玩家！造成 {bullet['damage']} 點傷害")
                continue  # 擊中後子彈消失

            # 檢查是否超出螢幕
            if 0 <= bullet["x"] <= SCREEN_WIDTH and 0 <= bullet["y"] <= SCREEN_HEIGHT:
                active_bullets.append(bullet)

        self.boss.fire_bullets = active_bullets

        # 嘗試發射新的火焰子彈
        if self.boss.is_alive and player.is_alive:
            # 計算與玩家的距離
            dx = player.x - self.boss.x
            dy = player.y - self.boss.y
            distance = (dx**2 + dy**2) ** 0.5

            # 如果玩家在合適的距離內，發射火焰子彈
            if 80 <= distance <= 250:  # 火焰子彈的有效攻擊範圍
                self.create_boss_fire_bullet(player.x, player.y)

    def update_sniper_boss_bullets(self, player):
        """
        更新狙擊Boss追蹤子彈狀態\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        current_time = time.time()
        active_bullets = []

        for bullet in self.boss.boss_bullets:
            # 檢查生存時間
            if current_time - bullet["created_time"] > bullet["lifetime"]:
                continue

            # 更新追蹤目標位置
            bullet["target_x"] = player.x + player.width // 2
            bullet["target_y"] = player.y + player.height // 2

            # 計算朝向目標的方向
            dx = bullet["target_x"] - bullet["x"]
            dy = bullet["target_y"] - bullet["y"]
            distance = (dx**2 + dy**2) ** 0.5

            if distance > 0:
                # 計算新的追蹤方向
                direction_x = dx / distance
                direction_y = dy / distance

                # 混合當前速度和追蹤方向，實現平滑追蹤
                tracking_strength = bullet["tracking_strength"]
                bullet["velocity_x"] = (1 - tracking_strength) * bullet[
                    "velocity_x"
                ] + tracking_strength * direction_x * BOSS_BULLET_SPEED
                bullet["velocity_y"] = (1 - tracking_strength) * bullet[
                    "velocity_y"
                ] + tracking_strength * direction_y * BOSS_BULLET_SPEED

            # 更新位置
            bullet["x"] += bullet["velocity_x"]
            bullet["y"] += bullet["velocity_y"]

            # 檢查與玩家的碰撞
            bullet_rect = pygame.Rect(bullet["x"] - 8, bullet["y"] - 8, 16, 16)
            if bullet_rect.colliderect(player.rect):
                # 追蹤子彈擊中玩家
                player.take_damage(bullet["damage"])
                print(f"🎯 狙擊Boss追蹤子彈擊中玩家！造成 {bullet['damage']} 點傷害")
                continue  # 擊中後子彈消失

            # 檢查是否超出螢幕邊界太遠（避免無限追蹤）
            if (
                -200 <= bullet["x"] <= SCREEN_WIDTH + 200
                and -200 <= bullet["y"] <= SCREEN_HEIGHT + 200
            ):
                active_bullets.append(bullet)

        self.boss.boss_bullets = active_bullets

        # 嘗試發射新的追蹤子彈
        if self.boss.is_alive and player.is_alive:
            # 計算與玩家的距離
            dx = player.x - self.boss.x
            dy = player.y - self.boss.y
            distance = (dx**2 + dy**2) ** 0.5

            # 如果玩家在攻擊範圍內，發射追蹤子彈
            if distance <= 300:  # 狙擊Boss的攻擊範圍
                self.create_sniper_boss_tracking_bullet(
                    player.x + player.width // 2, player.y + player.height // 2
                )

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

            # 特別標示Boss（根據Boss類型顯示不同標籤）
            boss_screen_x = self.boss.x - camera_x
            boss_screen_y = self.boss.y - camera_y

            font = get_chinese_font(FONT_SIZE_MEDIUM)

            if hasattr(self.boss, "tracking_bullets"):  # 狙擊Boss
                boss_text = font.render("🎯 SNIPER BOSS", True, PURPLE)

                # 繪製狙擊Boss的追蹤子彈
                if hasattr(self.boss, "boss_bullets"):
                    for bullet in self.boss.boss_bullets:
                        bullet_screen_x = bullet["x"] - camera_x
                        bullet_screen_y = bullet["y"] - camera_y
                        # 只繪製在螢幕範圍內的追蹤子彈
                        if (
                            -20 <= bullet_screen_x <= SCREEN_WIDTH + 20
                            and -20 <= bullet_screen_y <= SCREEN_HEIGHT + 20
                        ):
                            # 繪製追蹤子彈：紫色外圈和亮紫色內圈
                            pygame.draw.circle(
                                screen,
                                SNIPER_BOSS_BULLET_COLOR,
                                (int(bullet_screen_x), int(bullet_screen_y)),
                                8,
                            )
                            pygame.draw.circle(
                                screen,
                                (255, 100, 255),  # 亮紫色內圈
                                (int(bullet_screen_x), int(bullet_screen_y)),
                                4,
                            )
            else:  # 岩漿Boss
                boss_text = font.render("🔥 LAVA BOSS", True, RED)

                # 繪製岩漿Boss的火焰子彈
                if hasattr(self.boss, "fire_bullets"):
                    for bullet in self.boss.fire_bullets:
                        bullet_screen_x = bullet["x"] - camera_x
                        bullet_screen_y = bullet["y"] - camera_y
                        # 只繪製在螢幕範圍內的火焰子彈
                        if (
                            -20 <= bullet_screen_x <= SCREEN_WIDTH + 20
                            and -20 <= bullet_screen_y <= SCREEN_HEIGHT + 20
                        ):
                            # 繪製火焰子彈：橘紅色外圈和黃色內圈
                            pygame.draw.circle(
                                screen,
                                FIRE_BULLET_COLOR,
                                (int(bullet_screen_x), int(bullet_screen_y)),
                                8,
                            )
                            pygame.draw.circle(
                                screen,
                                YELLOW,
                                (int(bullet_screen_x), int(bullet_screen_y)),
                                4,
                            )

            # 繪製Boss標籤
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

        # 重置Boss相關狀態
        self.boss_spawned = False
        self.boss = None
        self.boss_stage = 1  # 重置Boss階段為第一階段
        self.boss_transition_timer = 0  # 重置Boss轉換計時器
        self.waiting_for_boss_transition = False  # 重置Boss轉換等待狀態

        # 保持當前波次但可選擇重置
        # self.wave_number = 1  # 如果要重置波次的話

        print(f"🔄 怪物系統已為新關卡重置")

    def clear_all_monsters(self):
        """
        清除所有怪物\n
        """
        self.monsters.clear()
        print("🧹 已清除所有怪物")
