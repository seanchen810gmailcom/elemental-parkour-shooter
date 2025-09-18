######################載入套件######################
import pygame
import sys
import time
import os

# 添加父目錄到路徑，支援直接執行
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 嘗試相對導入，如果失敗則使用絕對導入
try:
    from .config import *
    from .core.game_objects import *
    from .entities.player import Player
    from .entities.weapon import WeaponManager
    from .systems.monster_manager import MonsterManager
    from .systems.damage_display import DamageDisplayManager
    from .systems.level_system import LevelManager
    from .utils.cloud_system import CloudSystem
except ImportError:
    # 直接執行時使用絕對導入
    from src.config import *
    from src.core.game_objects import *
    from src.entities.player import Player
    from src.entities.weapon import WeaponManager
    from src.systems.monster_manager import MonsterManager
    from src.systems.damage_display import DamageDisplayManager
    from src.systems.level_system import LevelManager
    from src.utils.cloud_system import CloudSystem

######################遊戲主類別######################


class ElementalParkourShooter:
    """
    跑酷射擊大冒險 - 主遊戲類別\n
    \n
    統合管理整個遊戲的運行，包含：\n
    1. 遊戲初始化和設定\n
    2. 主遊戲迴圈控制\n
    3. 事件處理和畫面更新\n
    4. 遊戲狀態管理\n
    \n
    遊戲狀態:\n
    - 'menu': 主選單\n
    - 'playing': 進行遊戲\n
    - 'death_screen': 死亡重新開始畫面\n
    - 'paused': 暫停\n
    - 'game_over': 遊戲結束\n
    - 'victory': 勝利\n
    """

    def __init__(self):
        """
        初始化遊戲系統和基本設定\n
        \n
        設定 pygame、建立遊戲視窗、初始化遊戲狀態\n
        """
        # 初始化 pygame 系統
        pygame.init()

        # 初始化音效系統
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(SOUND_CHANNELS)  # 設定音效頻道數量

        # 載入射擊音效
        self.shooting_sound = None
        try:
            self.shooting_sound = pygame.mixer.Sound(SHOOTING_SOUND_PATH)
            self.shooting_sound.set_volume(SHOOTING_SOUND_VOLUME)
            print(f"成功載入射擊音效: {SHOOTING_SOUND_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            print(f"載入射擊音效失敗: {e}")
            print("遊戲將在沒有音效的情況下運行")

        # 載入必殺技音效
        self.ultimate_sound = None
        try:
            self.ultimate_sound = pygame.mixer.Sound(ULTIMATE_SOUND_PATH)
            self.ultimate_sound.set_volume(ULTIMATE_SOUND_VOLUME)
            print(f"成功載入必殺技音效: {ULTIMATE_SOUND_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            print(f"載入必殺技音效失敗: {e}")
            print("必殺技將在沒有音效的情況下運行")

        # 載入狙擊怪來襲音樂
        self.sniper_incoming_music = None
        try:
            self.sniper_incoming_music = pygame.mixer.Sound(SNIPER_INCOMING_MUSIC_PATH)
            self.sniper_incoming_music.set_volume(SNIPER_INCOMING_MUSIC_VOLUME)
            print(f"成功載入狙擊怪來襲音樂: {SNIPER_INCOMING_MUSIC_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            print(f"載入狙擊怪來襲音樂失敗: {e}")
            print("狙擊怪將在沒有特殊音樂的情況下出現")

        # 載入死亡音效
        self.game_over_sound = None
        try:
            self.game_over_sound = pygame.mixer.Sound(GAME_OVER_SOUND_PATH)
            self.game_over_sound.set_volume(GAME_OVER_SOUND_VOLUME)
            print(f"成功載入死亡音效: {GAME_OVER_SOUND_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            print(f"載入死亡音效失敗: {e}")
            print("遊戲將在沒有死亡音效的情況下運行")

        # 載入勝利星星音效
        self.victory_sound = None
        try:
            self.victory_sound = pygame.mixer.Sound(VICTORY_SOUND_PATH)
            self.victory_sound.set_volume(VICTORY_SOUND_VOLUME)
            print(f"成功載入勝利星星音效: {VICTORY_SOUND_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            print(f"載入勝利星星音效失敗: {e}")
            print("勝利星星將在沒有音效的情況下顯示")

        # 載入愛心道具音效
        self.health_pickup_sound = None
        try:
            self.health_pickup_sound = pygame.mixer.Sound(HEALTH_PICKUP_SOUND_PATH)
            self.health_pickup_sound.set_volume(HEALTH_PICKUP_SOUND_VOLUME)
            print(f"成功載入愛心道具音效: {HEALTH_PICKUP_SOUND_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            print(f"載入愛心道具音效失敗: {e}")
            print("愛心道具將在沒有音效的情況下顯示")

        # 載入Boss背景音樂
        self.boss_music = None
        try:
            self.boss_music = pygame.mixer.Sound(BOSS_MUSIC_PATH)
            self.boss_music.set_volume(BOSS_MUSIC_VOLUME)
            print(f"成功載入Boss背景音樂: {BOSS_MUSIC_PATH}")
        except (pygame.error, FileNotFoundError) as e:
            print(f"載入Boss背景音樂失敗: {e}")
            print("Boss將在沒有背景音樂的情況下出現")

        # 音樂播放狀態管理
        self.is_sniper_music_playing = False
        self.sniper_music_channel = None
        self.sniper_music_channels = []  # 多重播放頻道列表

        # Boss音樂管理
        self.boss_music_channel = None
        self.is_boss_music_playing = False
        self.boss_music_fade_duration = 1.0  # 漸弱持續時間（秒）

        # 建立遊戲視窗
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("跑酷射擊大冒險 - Elemental Parkour Shooter")

        # 設定遊戲時鐘，控制幀率
        self.clock = pygame.time.Clock()

        # 遊戲狀態管理
        self.game_state = "playing"  # 目前先直接開始遊戲，之後可加入選單
        self.running = True
        self.game_over_time = 0  # 進入遊戲結束狀態的時間

        # 遊戲進度管理（簡化為只有一個跑酷關卡）
        self.star_collected = False

        # 分數系統
        self.score = 0
        self.font = get_chinese_font(FONT_SIZE_MEDIUM)

        # 初始化遊戲物件
        self.player = Player(100, SCREEN_HEIGHT - 200)  # 在安全位置生成玩家
        self.weapon_manager = WeaponManager()  # 武器系統管理器
        self.monster_manager = MonsterManager()  # 怪物系統管理器
        self.damage_display = DamageDisplayManager()  # 傷害顯示管理器
        self.level_manager = LevelManager()  # 關卡場景管理器

        # 初始化背景和UI系統
        self.cloud_system = CloudSystem(
            self.level_manager.level_width, self.level_manager.level_height
        )  # 雲朵背景系統

        # 攝影機系統
        self.camera_x = 0
        self.camera_y = 0

        # 時間管理
        self.last_update_time = time.time()
        self.dt = 1 / 60  # 默認時間間隔

    def update_camera(self):
        """
        更新攝影機位置，讓攝影機跟隨玩家\n
        """
        # 攝影機跟隨玩家，但有邊界限制
        target_camera_x = self.player.x - SCREEN_WIDTH // 2
        target_camera_y = self.player.y - SCREEN_HEIGHT // 2

        # 限制攝影機不超出關卡邊界
        self.camera_x = max(
            0, min(target_camera_x, self.level_manager.level_width - SCREEN_WIDTH)
        )
        self.camera_y = max(
            0, min(target_camera_y, self.level_manager.level_height - SCREEN_HEIGHT)
        )

    def handle_melee_bullet_deflection(self):
        """
        甩槍攔截敵方子彈 - 在甩槍攻擊時擋掉範圍內的敵方子彈\n
        \n
        檢查甩槍攻擊範圍內是否有敵方子彈，如果有就把它們移除\n
        甩槍範圍使用目前裝備武器的攻擊距離來決定\n
        \n
        影響:\n
        - 移除攔截到的熔岩球和水彈\n
        - 產生視覺回饋（可能的爆炸效果）\n
        """
        # 取得目前武器的攻擊範圍，決定甩槍能擋多遠的子彈
        # 根據不同武器類型設定不同的擋彈範圍
        deflection_ranges = {
            "machine_gun": 80,
            "assault_rifle": 90,
            "shotgun": 100,
            "sniper": 120,
        }
        deflection_range = deflection_ranges.get(self.player.current_weapon, 80)

        # 計算甩槍的圓形防護區域（以玩家為中心）
        player_center_x = self.player.x + self.player.width // 2
        player_center_y = self.player.y + self.player.height // 2

        # 檢查所有怪物的子彈，看看有沒有飛進甩槍範圍
        for monster in self.monster_manager.monsters:
            # 擋掉熔岩球 - 從後面開始檢查，這樣移除時不會搞亂索引
            if hasattr(monster, "lava_balls"):  # 確保怪物有熔岩球系統
                for i in range(len(monster.lava_balls) - 1, -1, -1):
                    lava_ball = monster.lava_balls[i]

                    # 算出熔岩球跟玩家的距離
                    distance = (
                        (lava_ball["x"] - player_center_x) ** 2
                        + (lava_ball["y"] - player_center_y) ** 2
                    ) ** 0.5

                    # 如果熔岩球進入甩槍範圍就擋掉
                    if distance <= deflection_range:
                        monster.lava_balls.pop(i)  # 把熔岩球從遊戲中移除

            # 擋掉水彈 - 同樣從後面開始檢查
            if hasattr(monster, "water_bullets"):  # 確保怪物有水彈系統
                for i in range(len(monster.water_bullets) - 1, -1, -1):
                    water_bullet = monster.water_bullets[i]

                    # 算出水彈跟玩家的距離
                    distance = (
                        (water_bullet[0] - player_center_x) ** 2
                        + (water_bullet[1] - player_center_y) ** 2
                    ) ** 0.5

                    # 如果水彈進入甩槍範圍就擋掉
                    if distance <= deflection_range:
                        monster.water_bullets.pop(i)  # 把水彈從遊戲中移除

    def handle_weapon_spin_collision(self):
        """
        處理武器轉動時與怪物的碰撞 - 當槍還在轉時怪物被碰到會被擊退並扣血\n
        \n
        功能：\n
        1. 檢查旋轉中的武器是否碰到怪物\n
        2. 對碰到的怪物造成90點傷害\n
        3. 產生強力的擊退效果\n
        4. 防止同一次攻擊重複傷害同一怪物\n
        \n
        碰撞範圍：\n
        - 以玩家為中心計算武器旋轉位置\n
        - 根據武器飛行距離確定攻擊範圍\n
        - 使用圓形碰撞檢測確保精確判定\n
        """
        if not hasattr(self.player, "weapon_hit_monsters"):
            # 初始化已攻擊怪物記錄，防止重複傷害
            self.player.weapon_hit_monsters = set()

        # 如果這是新的攻擊，清空之前的記錄
        if self.player.melee_animation_time == 0:
            self.player.weapon_hit_monsters.clear()

        # 計算武器當前位置（基於玩家位置和武器飛行距離）
        player_center_x = self.player.x + self.player.width // 2
        player_center_y = self.player.y + self.player.height // 2

        # 根據武器旋轉角度計算武器位置
        weapon_angle_radians = math.radians(self.player.weapon_spin_angle)
        weapon_x = (
            player_center_x
            + math.cos(weapon_angle_radians) * self.player.weapon_fly_distance
        )
        weapon_y = (
            player_center_y
            + math.sin(weapon_angle_radians) * self.player.weapon_fly_distance
        )

        # 武器攻擊範圍（武器大小）
        weapon_attack_radius = 40  # 武器攻擊範圍半徑

        # 檢查所有怪物是否被武器碰到
        for monster in self.monster_manager.monsters:
            # 避免對同一怪物重複攻擊
            if id(monster) in self.player.weapon_hit_monsters:
                continue

            # 計算怪物中心位置
            monster_center_x = monster.x + monster.width // 2
            monster_center_y = monster.y + monster.height // 2

            # 計算武器與怪物的距離
            distance = math.sqrt(
                (weapon_x - monster_center_x) ** 2 + (weapon_y - monster_center_y) ** 2
            )

            # 檢查是否在攻擊範圍內
            if distance <= weapon_attack_radius:
                # 記錄已攻擊的怪物，避免重複傷害
                self.player.weapon_hit_monsters.add(id(monster))

                # 對怪物造成傷害
                if hasattr(monster, "take_damage"):
                    monster.take_damage(90)  # 造成90點傷害
                    print(f"🌪️ 旋轉武器擊中怪物！造成90點傷害")

                # 計算擊退方向（從武器位置推向怪物）
                if distance > 0:
                    knockback_direction_x = (monster_center_x - weapon_x) / distance
                    knockback_direction_y = (monster_center_y - weapon_y) / distance
                else:
                    # 如果距離為0，使用預設方向
                    knockback_direction_x = self.player.facing_direction
                    knockback_direction_y = 0

                # 施加擊退效果
                knockback_force = 200  # 強力擊退
                if hasattr(monster, "apply_knockback"):
                    monster.apply_knockback(knockback_force, knockback_direction_x)
                elif hasattr(monster, "velocity_x"):
                    # 如果怪物沒有 apply_knockback 方法，直接修改速度
                    monster.velocity_x += knockback_direction_x * knockback_force
                    if hasattr(monster, "velocity_y"):
                        monster.velocity_y += (
                            knockback_direction_y * knockback_force * 0.5
                        )  # 輕微向上擊飛

                # 增加分數
                self.score += 25  # 旋轉攻擊額外分數

    def handle_events(self):
        """
        處理所有遊戲事件 - 滑鼠點擊、鍵盤按鍵、視窗關閉等\n
        \n
        檢查玩家的輸入並做出對應反應，\n
        包含遊戲控制和系統事件。\n
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 玩家點擊視窗關閉按鈕
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # 按 ESC 鍵離開遊戲
                    self.running = False
                elif event.key == pygame.K_r:
                    # 按 R 鍵重新開始遊戲 - 修正重新開始邏輯
                    if self.game_state in ["game_over", "victory", "death_screen"]:
                        self.reset_game()
                        print("🔄 玩家按下 R 鍵，遊戲重新開始")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 處理滑鼠點擊事件 - 只在遊戲進行時處理
                if self.game_state == "playing" and self.player.is_alive:
                    if event.button == 3:  # 右鍵點擊
                        # 執行甩槍攻擊
                        attack_result = self.player.melee_attack()
                        if attack_result and attack_result.get("success"):
                            print(
                                f"🥊 {attack_result.get('weapon_name', '武器')}甩槍攻擊！"
                            )

                            # 檢查攻擊是否命中怪物
                            attack_x = self.player.x
                            attack_y = self.player.y
                            attack_range = attack_result.get("range", 80)
                            attack_damage = attack_result.get("damage", 120)
                            attack_knockback = attack_result.get("knockback", 150)

                            # 計算攻擊範圍內的怪物
                            hit_monsters = []
                            for monster in self.monster_manager.monsters:
                                distance = (
                                    (monster.x - attack_x) ** 2
                                    + (monster.y - attack_y) ** 2
                                ) ** 0.5
                                if distance <= attack_range:
                                    hit_monsters.append(monster)

                            # 對範圍內的怪物造成傷害
                            for monster in hit_monsters:
                                monster.take_damage(
                                    attack_damage, "melee"
                                )  # 標記為甩槍攻擊

                                # 計算擊退方向
                                dx = monster.x - attack_x
                                dy = monster.y - attack_y
                                distance = (dx**2 + dy**2) ** 0.5
                                if distance > 0:
                                    dx /= distance
                                    dy /= distance
                                    monster.velocity_x = dx * attack_knockback
                                    monster.velocity_y = dy * attack_knockback

                                # 顯示傷害數字
                                self.damage_display.add_damage_number(
                                    monster.x, monster.y - 20, attack_damage
                                )

                                print(
                                    f"💥 {attack_result.get('weapon_name', '武器')}甩槍攻擊命中怪物，造成 {attack_damage} 點傷害！"
                                )

                                # 檢查怪物是否死亡
                                if monster.health <= 0:
                                    self.score += monster.score_value
                                    print(
                                        f"💀 怪物被甩槍攻擊擊敗！得分 +{monster.score_value}"
                                    )
                        else:
                            print("🔄 甩槍攻擊冷卻中...")

        # 處理連續按鍵和滑鼠輸入 - 確保只在遊戲進行時處理
        if self.game_state == "playing" and self.player.is_alive:
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            self.player.handle_input(keys, mouse_buttons, self.camera_x, self.camera_y)

    def update(self):
        """
        更新遊戲邏輯 - 每一幀都會執行的遊戲更新\n
        \n
        依照遊戲狀態執行對應的更新邏輯：\n
        - 玩家移動和跑酷動作\n
        - 怪物 AI 和攻擊\n
        - 子彈飛行和碰撞\n
        - 狀態效果更新\n
        """
        if self.game_state == "playing":
            # 計算時間差
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.last_update_time = current_time
            self.dt = dt  # 儲存為實例變數以供其他方法使用

            # 更新玩家狀態
            if self.player.is_alive:
                # 使用關卡管理器的平台資料
                platforms = self.level_manager.get_platforms()
                player_update_result = self.player.update(platforms)

                # 檢查玩家更新結果（可能包含死亡資訊）
                if player_update_result and player_update_result.get(
                    "game_over", False
                ):
                    # 玩家死亡直接遊戲結束
                    self.play_game_over_sound()  # 播放死亡音效
                    self.stop_sniper_incoming_music()  # 強制停止大怪來襲音樂
                    self.game_state = "game_over"
                    self.game_over_time = time.time()
                    print("💀 遊戲結束！")

                # 檢查玩家與陷阱的碰撞（現在沒有危險陷阱）
                hazard_damage = self.level_manager.check_hazard_collisions(self.player)
                # hazard_damage 現在總是 0

                # 處理玩家的射擊 - 檢查是否有待發射的子彈
                bullet_info = self.player.get_pending_bullet()
                if bullet_info:
                    self.weapon_manager.create_bullet(bullet_info)
                    # 播放射擊音效，根據子彈傷害調整音量
                    if isinstance(bullet_info, list):
                        # 散彈槍會返回多顆子彈的列表，取第一顆的傷害值
                        damage = bullet_info[0]["damage"]
                    else:
                        # 其他武器返回單一子彈資訊
                        damage = bullet_info["damage"]
                    self.play_shooting_sound(damage)

                # 處理玩家的必殺技 - 檢查是否有待發射的必殺技
                ultimate_info = self.player.get_pending_ultimate()
                if ultimate_info:
                    # 獲取當前所有可攻擊的目標
                    all_targets = []
                    all_targets.extend(self.monster_manager.monsters)
                    if self.monster_manager.boss:
                        all_targets.append(self.monster_manager.boss)

                    # 創建必殺技，傳入目標資訊讓子彈智能分配攻擊
                    self.weapon_manager.create_ultimate(ultimate_info, all_targets)

                    # 播放必殺技專用雷電音效（大聲震撼）
                    self.play_ultimate_sound()

                    # 根據目標類型顯示不同的攻擊模式訊息
                    boss_targets = [
                        target
                        for target in all_targets
                        if hasattr(target, "is_boss") and target.is_boss
                    ]
                    regular_targets = [
                        target
                        for target in all_targets
                        if not (hasattr(target, "is_boss") and target.is_boss)
                    ]

                    if boss_targets:
                        # 有Boss時優先攻擊Boss
                        if len(boss_targets) == 1:
                            boss_type = getattr(boss_targets[0], "monster_type", "Boss")
                            print(f"⚡ 雷電追蹤攻擊發動！鎖定Boss目標：{boss_type}")
                        else:
                            print(
                                f"⚡ 雷電追蹤攻擊發動！鎖定多個Boss目標：{len(boss_targets)}個"
                            )
                    elif regular_targets:
                        # 沒有Boss時攻擊普通怪物
                        if len(regular_targets) == 1:
                            print("⚡ 雷電追蹤攻擊發動！(集中火力模式)")
                        else:
                            print(
                                f"⚡ 雷電追蹤攻擊發動！(分散攻擊模式 - {len(regular_targets)}個目標)"
                            )
                    else:
                        print("⚡ 雷電追蹤攻擊發動！(無目標模式)")

                # 處理玩家的近戰攻擊
                melee_info = (
                    self.player.melee_attack()
                    if self.player.keys_pressed.get("melee", False)
                    else None
                )
                if melee_info:
                    # 檢查近戰攻擊是否擊中怪物
                    hit_monsters = self.weapon_manager.handle_melee_attack(
                        melee_info, self.monster_manager.monsters
                    )

                    # 每擊中一個怪物得20分
                    self.score += len(hit_monsters) * 20

                    # 根據武器類型顯示甩槍攻擊資訊
                    if hit_monsters:
                        weapon_names = {
                            "machine_gun": "機關槍",
                            "assault_rifle": "衝鋒槍",
                            "shotgun": "散彈槍",
                            "sniper": "狙擊槍",
                        }
                        weapon_name = weapon_names.get(
                            melee_info.get("weapon_type", "unknown"), "未知武器"
                        )
                        damage = melee_info.get("damage", 0)
                        print(
                            f"🔨 {weapon_name}甩擊命中 {len(hit_monsters)} 個目標！傷害: {damage}"
                        )
                    else:
                        print("🔨 甩槍攻擊發動但未命中目標")

            elif self.player.is_dead:
                # 玩家已經死亡，不再進行遊戲更新
                pass

            # 更新關卡系統
            bullets = self.weapon_manager.bullets
            level_update_result = self.level_manager.update(
                dt, self.player, bullets, False
            )

            # 檢查關卡中的傷害結果（如尖刺傷害）
            damage_result = level_update_result.get("damage_result")
            if damage_result:
                if damage_result.get("game_over", False):
                    # 玩家死亡直接遊戲結束
                    self.play_game_over_sound()  # 播放死亡音效
                    self.stop_sniper_incoming_music()  # 強制停止大怪來襲音樂
                    self.game_state = "game_over"
                    self.game_over_time = time.time()
                    print("💀 遊戲結束！")

            # 檢查是否收集到星星
            if level_update_result.get("star_collected", False):
                # 玩家成功收集到星星！播放勝利音效
                self.play_victory_sound()
                self.game_state = "victory"
                self.score += 10000  # 收集星星的大獎勵

            # 檢查是否拾取到愛心道具
            if level_update_result.get("health_pickup_collected", False):
                # 玩家成功拾取愛心道具！播放拾取音效
                self.play_health_pickup_sound()

            # 更新攝影機
            self.update_camera()

            # 更新雲朵系統 - 傳遞玩家座標讓雲朵跟隨
            self.cloud_system.update(dt, self.player.x, self.player.y)

            # 小地圖系統已移除

            # 更新怪物系統
            platforms = self.level_manager.get_platforms()
            bullets = self.weapon_manager.bullets  # 獲取玩家子彈用於Boss躲避
            level_width = self.level_manager.level_width  # 獲取關卡實際寬度
            monster_update_result = self.monster_manager.update(
                self.player, platforms, dt, bullets, level_width
            )

            # 甩槍攔截怪物子彈 - 檢查甩槍攻擊是否能擋下敵方子彈
            if self.player.is_melee_attacking:
                self.handle_melee_bullet_deflection()

            # 武器轉動時的怪物碰撞檢測 - 檢查轉動中的武器是否碰到怪物
            if self.player.is_melee_attacking and self.player.weapon_flying:
                self.handle_weapon_spin_collision()

            # 根據怪物擊殺數增加分數
            if monster_update_result["monsters_killed"] > 0:
                self.score += monster_update_result["monsters_killed"] * 50

            # 處理怪物對玩家造成的傷害
            monster_damage_result = monster_update_result.get("player_damage_result")
            if monster_damage_result:
                if monster_damage_result.get("game_over", False):
                    # 玩家死亡直接遊戲結束
                    self.play_game_over_sound()
                    self.stop_sniper_incoming_music()
                    self.game_state = "game_over"
                    self.game_over_time = time.time()
                    print("💀 遊戲結束！")

            # 檢查Boss生成
            if monster_update_result["boss_spawned"]:
                print("🔥 強大的Boss出現了！")
                # 開始播放Boss背景音樂
                self.start_boss_music()

            # 更新Boss音樂狀態（檢查是否需要重新播放）
            self.update_boss_music_status()

            # 管理狙擊怪來襲音樂
            self.manage_sniper_incoming_music()

            # 檢查Boss是否被擊敗
            if monster_update_result["boss_defeated"]:
                # 停止Boss背景音樂（漸弱效果）
                self.stop_boss_music_with_fade()

                # 強制停止狙擊怪來襲音樂（大怪來襲.wav）
                self.stop_sniper_incoming_music()

                # 只有狙擊Boss被擊敗時才生成勝利星星
                if monster_update_result.get("sniper_boss_defeated", False):
                    boss_x = monster_update_result.get(
                        "boss_death_x", self.level_manager.level_width // 2
                    )
                    boss_y = monster_update_result.get(
                        "boss_death_y", SCREEN_HEIGHT - 200
                    )
                    self.level_manager.star_x = boss_x
                    self.level_manager.star_y = boss_y - 50
                    self.level_manager.star_collected = False
                    self.level_manager.star_visible = True  # 讓勝利星星可見
                    print("🌟 最終Boss被擊敗！勝利星星出現了！")
                else:
                    print("🔥 第一階段Boss被擊敗，準備最終挑戰！")

            # Boss系統移除，簡化遊戲體驗

            # 更新武器系統（子彈飛行等）
            all_targets = self.monster_manager.monsters[:]  # 複製怪物列表

            # 添加Boss作為目標（如果存在）
            if self.monster_manager.boss:
                all_targets.append(self.monster_manager.boss)

            collision_results = self.weapon_manager.update(targets=all_targets)

            # 處理子彈碰撞結果
            for collision in collision_results:
                # 每發子彈擊中得10分
                base_score = 10
                self.score += base_score

                # 顯示傷害數字
                target = collision["target"]
                bullet = collision["bullet"]
                damage = collision["damage"]

                # 在怪物位置顯示傷害數字
                target_type = getattr(target, "monster_type", "unknown")
                self.damage_display.add_damage_number(
                    target.x + target.width // 2,
                    target.y,
                    damage,
                    bullet.bullet_type,
                    target_type,
                )

                # 如果有狀態效果，也顯示效果名稱
                if collision["status_effect"]:
                    effect_name_map = {"slow": "減速", "paralysis": "麻痺"}
                    effect_name = effect_name_map.get(
                        collision["status_effect"]["type"], "狀態效果"
                    )
                    self.damage_display.add_status_effect_text(
                        target.x + target.width // 2, target.y - 20, effect_name
                    )

            # 更新傷害顯示
            self.damage_display.update()

        # 移除 death_screen 狀態處理，改用死亡倒數機制

    def play_shooting_sound(self, damage=30):
        """
        播放射擊音效 - 根據子彈強度調整音量\n
        \n
        特點：\n
        1. 根據子彈傷害值動態調整音量大小\n
        2. 傷害越高，音效越響亮，差距明顯\n
        3. 支援多頻道播放，適合連續射擊\n
        4. 音效載入失敗時不影響遊戲運行\n
        \n
        參數:\n
        damage (int): 子彈傷害值，範圍 20-90\n
        \n
        音量計算（差距加大）：\n
        - 傷害 20（冰彈）→ 音量 0.1（很小聲）\n
        - 傷害 35（火彈/衝鋒槍）→ 音量 0.4\n
        - 傷害 90（狙擊槍）→ 音量 1.0（最大聲）\n
        """
        if self.shooting_sound:
            try:
                # 根據傷害值計算音量（線性映射，範圍更大）
                # 傷害範圍：20-90，音量範圍：0.1-1.0（差距9倍）
                min_damage = 20
                max_damage = 90
                min_volume = 0.1  # 從 0.3 降低到 0.1，讓小威力子彈很小聲
                max_volume = 1.0  # 維持最大音量

                # 限制傷害值在有效範圍內
                damage = max(min_damage, min(max_damage, damage))

                # 線性插值計算音量
                volume_ratio = (damage - min_damage) / (max_damage - min_damage)
                volume = min_volume + (max_volume - min_volume) * volume_ratio

                # 設定音效音量並播放
                self.shooting_sound.set_volume(volume)
                self.shooting_sound.play()

                # 除錯資訊：顯示當前音量（可啟用來觀察效果）
                print(f"🔊 射擊音效：傷害 {damage} → 音量 {volume:.2f}")

            except pygame.error as e:
                # 音效播放失敗時不影響遊戲
                print(f"播放射擊音效失敗: {e}")

    def play_ultimate_sound(self):
        """
        播放必殺技音效 - 雷電轟鳴聲（超大音量版本）\n
        \n
        特點：\n
        1. 使用專門的雷電音效，震撼感十足\n
        2. 音量設定為4倍大聲，突出必殺技的威力\n
        3. 使用多頻道同時播放技術增強音量感\n
        4. 音效載入失敗時不影響遊戲運行\n
        \n
        音效特性：\n
        - 使用 heavy-thunder-sound-effect 雷電音效\n
        - 音量強化到4倍大聲\n
        - 適合20秒冷卻的強力技能\n
        """
        if self.ultimate_sound:
            try:
                # 設定超大音量（pygame會自動限制在1.0，但我們盡力而為）
                max_volume = min(1.0, ULTIMATE_SOUND_VOLUME)  # 確保不超過1.0
                self.ultimate_sound.set_volume(max_volume)

                # 多重播放技術：同時在多個頻道播放相同音效來增強音量感
                # 這會讓音效聽起來更響亮更震撼
                for i in range(3):  # 同時播放3次
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.play(self.ultimate_sound)
                    else:
                        # 如果沒有可用頻道，直接播放
                        self.ultimate_sound.play()

                # 除錯資訊：顯示必殺技音效觸發
                print(
                    f"⚡⚡⚡ 必殺技音效：超大聲雷電轟鳴！音量 {ULTIMATE_SOUND_VOLUME}倍（實際{max_volume}）"
                )

            except pygame.error as e:
                # 音效播放失敗時不影響遊戲
                print(f"播放必殺技音效失敗: {e}")

    def play_game_over_sound(self):
        """
        播放玩家死亡音效 - Game Over 音效\n
        \n
        特點：\n
        1. 音量適中，不會過於突兀但足夠引起注意\n
        2. 只在玩家真正死亡時播放，避免重複播放\n
        3. 音效載入失敗時不影響遊戲運行\n
        \n
        使用時機：\n
        - 玩家血量歸零死亡時\n
        - 玩家掉出螢幕死亡時\n
        - 受到致命傷害時\n
        """
        if self.game_over_sound:
            try:
                # 播放死亡音效
                self.game_over_sound.play()
                print(f"💀 播放死亡音效：Game Over！")

            except pygame.error as e:
                # 音效播放失敗時不影響遊戲
                print(f"播放死亡音效失敗: {e}")

    def play_victory_sound(self):
        """
        播放勝利星星音效 - 成功收集星星時的慶祝音效\n
        \n
        特點：\n
        1. 使用愉快的勝利音效，讓玩家感受成就感\n
        2. 音量適中，不會蓋過其他遊戲音效\n
        3. 在玩家成功收集到勝利星星時播放\n
        4. 音效載入失敗時不影響遊戲運行\n
        \n
        使用時機：\n
        - 玩家收集到 Boss 勝利星星時\n
        - 玩家收集到最右邊破關星星時\n
        - 完成重要成就時\n
        """
        if self.victory_sound:
            try:
                # 播放勝利音效
                self.victory_sound.play()
                print(f"🌟 播放勝利星星音效：Stage Clear！")

            except pygame.error as e:
                # 音效播放失敗時不影響遊戲
                print(f"播放勝利星星音效失敗: {e}")

    def play_health_pickup_sound(self):
        """
        播放愛心道具音效 - 撿到愛心時的溫馨音效\n
        \n
        特點：\n
        1. 使用溫馨的道具拾取音效，給玩家正面回饋\n
        2. 音量適中，不會打斷遊戲節奏\n
        3. 在玩家拾取愛心道具並成功恢復生命值時播放\n
        4. 音效載入失敗時不影響遊戲運行\n
        \n
        使用時機：\n
        - 玩家碰到愛心道具並成功恢復生命值時\n
        - 拾取其他有益道具時（未來擴展）\n
        """
        if self.health_pickup_sound:
            try:
                # 播放愛心道具音效
                self.health_pickup_sound.play()
                print(f"💚 播放愛心道具音效：吃到寶物！")

            except pygame.error as e:
                # 音效播放失敗時不影響遊戲
                print(f"播放愛心道具音效失敗: {e}")

    def manage_sniper_incoming_music(self):
        """
        管理狙擊怪來襲音樂播放\n
        \n
        根據狙擊Boss的存在狀態決定是否播放特殊音樂\n
        """
        # 檢查是否有狙擊Boss存在
        has_sniper_boss = self.monster_manager.boss is not None and hasattr(
            self.monster_manager.boss, "tracking_bullets"
        )

        if has_sniper_boss and not self.is_sniper_music_playing:
            # 狙擊Boss存在但音樂還沒播放，開始播放
            self.play_sniper_incoming_music()
        elif not has_sniper_boss and self.is_sniper_music_playing:
            # 狙擊Boss不存在但音樂還在播放，停止播放
            self.stop_sniper_incoming_music()

    def play_sniper_incoming_music(self):
        """
        播放狙擊怪來襲音樂 - 超大音量版本\n
        \n
        使用多重播放技術增強音量感，達到3倍大聲的效果\n
        """
        if self.sniper_incoming_music and not self.is_sniper_music_playing:
            try:
                # 設定最大音量（pygame會自動限制在1.0，但我們盡力而為）
                max_volume = min(1.0, SNIPER_INCOMING_MUSIC_VOLUME)
                self.sniper_incoming_music.set_volume(max_volume)

                # 多重播放技術：同時在多個頻道播放相同音樂來增強音量感
                # 這會讓音樂聽起來更響亮更震撼
                self.sniper_music_channels = []  # 儲存多個音樂頻道

                for i in range(3):  # 同時播放3次來達到3倍音量效果
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.play(self.sniper_incoming_music, loops=-1)
                        self.sniper_music_channels.append(channel)
                    else:
                        # 如果沒有可用頻道，直接播放
                        self.sniper_incoming_music.play(loops=-1)

                self.is_sniper_music_playing = True
                print(
                    f"🎯🎯🎯 狙擊怪來襲音樂開始播放！音量 {SNIPER_INCOMING_MUSIC_VOLUME}倍（3倍大聲）"
                )

            except pygame.error as e:
                print(f"播放狙擊怪來襲音樂失敗: {e}")

    def stop_sniper_incoming_music(self):
        """
        停止狙擊怪來襲音樂 - 停止所有多重播放頻道\n
        """
        if self.is_sniper_music_playing:
            try:
                # 停止所有音樂頻道
                if (
                    hasattr(self, "sniper_music_channels")
                    and self.sniper_music_channels
                ):
                    for channel in self.sniper_music_channels:
                        if channel:
                            channel.stop()
                    self.sniper_music_channels = []
                elif (
                    hasattr(self, "sniper_music_channel") and self.sniper_music_channel
                ):
                    self.sniper_music_channel.stop()
                else:
                    # 停止所有正在播放的音樂（如果沒有專用頻道）
                    pygame.mixer.stop()

                self.is_sniper_music_playing = False
                self.sniper_music_channel = None
                print("🎯 狙擊怪來襲音樂已停止（3倍音量版本）")

            except pygame.error as e:
                print(f"停止狙擊怪來襲音樂失敗: {e}")

    def reset_game(self):
        """
        重置遊戲到初始狀態\n
        """
        # 停止狙擊怪來襲音樂（如果正在播放）
        if self.is_sniper_music_playing:
            self.stop_sniper_incoming_music()

        # 停止Boss背景音樂（如果正在播放）
        if self.is_boss_music_playing:
            self.stop_boss_music_with_fade()

        # 重置遊戲狀態
        self.game_state = "playing"
        self.star_collected = False
        self.score = 0
        self.game_over_time = 0

        # 重置遊戲物件
        self.player = Player(100, SCREEN_HEIGHT - 200)
        self.weapon_manager = WeaponManager()
        self.monster_manager = MonsterManager()
        self.damage_display = DamageDisplayManager()
        self.level_manager = LevelManager()

        # 重新初始化背景和UI系統
        self.cloud_system = CloudSystem(
            self.level_manager.level_width, self.level_manager.level_height
        )

        # 重置攝影機
        self.camera_x = 0
        self.camera_y = 0

        # 重置時間管理
        self.last_update_time = time.time()

        print("🔄 遊戲已重置")

    def draw(self):
        """
        繪製遊戲畫面 - 把所有物件畫到螢幕上\n
        \n
        繪製順序（從背景到前景）：\n
        1. 背景和環境場景\n
        2. 關卡平台和陷阱\n
        3. 怪物和子彈\n
        4. 玩家角色\n
        5. UI 介面（血量、分數等）\n
        """
        if self.game_state == "playing":
            # 先清空螢幕並繪製天空背景
            self.screen.fill(SKY_COLOR)

            # 繪製遠山背景（在地平線上）- 使用標準 Pygame 座標系統
            horizon_y = 500  # 固定地平線在 Y=500，玩家在 Y=600

            for i in range(5):
                # 簡化座標：背景山峰幾乎不移動
                mountain_x = i * (SCREEN_WIDTH // 4) - (
                    self.camera_x * 0.05
                )  # 極輕微視差
                mountain_height = 50 + i * 20
                mountain_color = (64 + i * 10, 64 + i * 10, 80 + i * 10)  # 漸層灰藍色

                # 繪製三角形山峰
                mountain_points = [
                    (mountain_x - 100, horizon_y),
                    (mountain_x, horizon_y - mountain_height),
                    (mountain_x + 100, horizon_y),
                ]

                pygame.draw.polygon(self.screen, mountain_color, mountain_points)

            # 繪製地面背景（在螢幕下方）
            ground_height = SCREEN_HEIGHT // 4  # 地面佔螢幕下方1/4
            ground_rect = pygame.Rect(
                0, SCREEN_HEIGHT - ground_height, SCREEN_WIDTH, ground_height
            )
            pygame.draw.rect(self.screen, (101, 67, 33), ground_rect)  # 深棕色地面

            # 繪製草地表面
            grass_height = 10
            grass_rect = pygame.Rect(
                0,
                SCREEN_HEIGHT - ground_height - grass_height,
                SCREEN_WIDTH,
                grass_height,
            )
            pygame.draw.rect(self.screen, (34, 139, 34), grass_rect)  # 草綠色

            # 繪製關卡場景（包含背景、平台和陷阱）
            self.level_manager.draw(self.screen, self.camera_x, self.camera_y)

            # 繪製怪物（需要攝影機偏移）
            self.monster_manager.draw(self.screen, self.camera_x, self.camera_y)

            # 繪製武器系統（子彈等）
            self.weapon_manager.draw(self.screen, self.camera_x, self.camera_y)

            # 繪製傷害數字
            self.damage_display.draw(self.screen, self.camera_x, self.camera_y)

            # 繪製玩家
            if self.player.is_alive:
                self.player.draw(self.screen, self.camera_x, self.camera_y)

            # 繪製狙擊槍準心（在最上層）
            self.player.draw_crosshair(self.screen, self.camera_x, self.camera_y)

            # 繪製 UI 元素（固定在螢幕上，不受攝影機影響）
            self.player.draw_health_bar(self.screen)
            self.player.draw_bullet_ui(self.screen)
            self.player.draw_ultimate_ui(self.screen)

            # 繪製分數（恢復到原始位置）
            score_font = get_chinese_font(FONT_SIZE_MEDIUM)
            score_text = score_font.render(f"分數: {self.score}", True, WHITE)
            score_rect = score_text.get_rect()
            score_rect.topright = (SCREEN_WIDTH - 20, 20)  # 恢復到右上角原始位置
            self.screen.blit(score_text, score_rect)

        elif self.game_state == "victory":
            # 繪製勝利畫面
            self.screen.fill(BLACK)

            victory_text = get_chinese_font(FONT_SIZE_LARGE).render(
                "🏆 勝利！", True, YELLOW
            )
            victory_rect = victory_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
            )
            self.screen.blit(victory_text, victory_rect)

            score_text = self.font.render(f"最終分數: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
            )
            self.screen.blit(score_text, score_rect)

            congrats_text = self.font.render("恭喜找到目標星星！", True, GREEN)
            congrats_rect = congrats_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
            )
            self.screen.blit(congrats_text, congrats_rect)

            restart_text = self.font.render("按 R 重新開始，ESC 離開", True, WHITE)
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
            )
            self.screen.blit(restart_text, restart_rect)

        # 移除死亡畫面繪製邏輯，改用死亡倒數機制

        elif self.game_state == "game_over":
            # 繪製遊戲結束畫面
            self.screen.fill(GAME_OVER_BG_COLOR)

            # 標題文字
            game_over_text = get_chinese_font(FONT_SIZE_LARGE).render(
                DEATH_TITLE_TEXT, True, GAME_OVER_TITLE_COLOR
            )
            text_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)
            )
            self.screen.blit(game_over_text, text_rect)

            # 最終分數
            score_text = self.font.render(
                f"{DEATH_FINAL_SCORE_TEXT}: {self.score}", True, GAME_OVER_TEXT_COLOR
            )
            score_rect = score_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
            )
            self.screen.blit(score_text, score_rect)

            # 爬升高度（保留原有功能）
            height_level = max(1, int(-(self.player.y - SCREEN_HEIGHT) / 120))
            level_text = self.font.render(
                f"爬升高度: 第 {height_level} 層", True, GAME_OVER_TEXT_COLOR
            )
            level_rect = level_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(level_text, level_rect)

            # 重新開始提示
            restart_text = self.font.render(
                DEATH_RETRY_TEXT, True, GAME_OVER_RETRY_COLOR
            )
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
            )
            self.screen.blit(restart_text, restart_rect)

            # 離開遊戲提示
            quit_text = self.font.render(DEATH_QUIT_TEXT, True, GAME_OVER_TEXT_COLOR)
            quit_rect = quit_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
            )
            self.screen.blit(quit_text, quit_rect)

        # 最後繪製雲朵系統（最上層顯示）
        if self.game_state == "playing":
            self.cloud_system.draw(self.screen, self.camera_x, self.camera_y)

        # 更新整個螢幕顯示
        pygame.display.flip()

    def start_boss_music(self):
        """
        開始播放Boss背景音樂，支持循環播放
        """
        if not self.boss_music or self.is_boss_music_playing:
            return

        try:
            # 如果有其他音樂在播放，停止它們
            if self.is_sniper_music_playing:
                self.stop_sniper_music()

            # 播放Boss音樂，使用-1表示無限循環
            self.boss_music_channel = pygame.mixer.find_channel()
            if self.boss_music_channel:
                self.boss_music_channel.play(self.boss_music, loops=-1)
                self.is_boss_music_playing = True
                print("🎵 Boss背景音樂開始播放（循環）")

        except Exception as e:
            print(f"播放Boss音樂時發生錯誤: {e}")

    def stop_boss_music_with_fade(self):
        """
        以漸弱效果停止Boss背景音樂
        """
        if not self.is_boss_music_playing or not self.boss_music_channel:
            return

        try:
            # 使用pygame的fadeout功能實現漸弱效果
            fade_time_ms = int(self.boss_music_fade_duration * 1000)  # 轉換為毫秒
            self.boss_music_channel.fadeout(fade_time_ms)

            self.is_boss_music_playing = False
            self.boss_music_channel = None
            print(f"🎵 Boss背景音樂以 {self.boss_music_fade_duration} 秒漸弱停止")

        except Exception as e:
            print(f"停止Boss音樂時發生錯誤: {e}")

    def update_boss_music_status(self):
        """
        更新Boss音樂播放狀態，檢查是否需要重新播放
        """
        if self.is_boss_music_playing and self.boss_music_channel:
            # 檢查音樂是否還在播放
            if not self.boss_music_channel.get_busy():
                print("🎵 Boss音樂播放結束，準備重新播放")
                self.is_boss_music_playing = False
                self.boss_music_channel = None

                # 如果還有Boss存在，重新開始播放音樂
                if self.monster_manager.boss and self.monster_manager.boss.is_alive:
                    self.start_boss_music()

    def stop_sniper_music(self):
        """
        停止狙擊怪音樂播放
        """
        if self.is_sniper_music_playing:
            for channel in self.sniper_music_channels:
                if channel and channel.get_busy():
                    channel.stop()
            self.sniper_music_channels.clear()
            self.is_sniper_music_playing = False
            print("🎵 狙擊怪音樂已停止")

    def run(self):
        """
        主遊戲迴圈 - 控制整個遊戲的運行節奏\n
        \n
        這是遊戲的心臟，會一直重複執行：\n
        1. 處理玩家輸入\n
        2. 更新遊戲狀態\n
        3. 繪製新畫面\n
        4. 控制幀率\n
        \n
        直到玩家選擇離開遊戲為止。\n
        """
        while self.running:
            # 處理事件（按鍵、滑鼠、視窗關閉等）
            self.handle_events()

            # 更新遊戲邏輯
            self.update()

            # 繪製遊戲畫面
            self.draw()

            # 控制遊戲幀率，確保穩定的 60 FPS
            self.clock.tick(FPS)

        # 遊戲結束時清理資源
        pygame.quit()
        sys.exit()


######################主程式入口######################


def main():
    """
    程式進入點 - 建立遊戲實例並開始運行\n
    """
    game = ElementalParkourShooter()
    game.run()


# 只有在直接執行時才啟動遊戲
if __name__ == "__main__":
    main()
