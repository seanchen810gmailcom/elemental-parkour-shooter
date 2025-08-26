######################載入套件######################
import pygame
import random
import math
import time
from ..config import *
from ..core.game_objects import *
from ..entities.monsters import Monster
from ..core.element_system import ElementSystem

######################Boss基礎類別######################


class Boss(Monster):
    """
    Boss 怪物基礎類別\n
    \n
    所有 Boss 的共通功能：\n
    1. 多階段戰鬥模式\n
    2. 特殊攻擊技能\n
    3. 更高的血量和防禦力\n
    4. 複雜的 AI 行為模式\n
    5. 階段轉換的特殊效果\n
    """

    def __init__(self, x, y, width, height, color, health, damage, boss_type):
        """
        初始化 Boss 基礎屬性\n
        \n
        參數:\n
        x, y (int): Boss 初始位置\n
        width, height (int): Boss 尺寸\n
        color (tuple): Boss 顏色\n
        health (int): Boss 血量\n
        damage (int): Boss 攻擊力\n
        boss_type (str): Boss 類型標識\n
        """
        super().__init__(x, y, width, height, color, health, damage, boss_type)

        # Boss 特有屬性
        self.boss_type = boss_type
        self.phase = 1  # 當前階段
        self.max_phases = 3  # 最大階段數
        self.phase_health_thresholds = [0.66, 0.33, 0]  # 階段切換血量門檻
        self.special_attack_cooldown = 0  # 特殊攻擊冷卻時間
        self.invulnerable = False  # 無敵狀態
        self.invulnerable_timer = 0  # 無敵時間

        # 階段轉換效果
        self.phase_transitioning = False
        self.transition_timer = 0
        self.transition_duration = 2.0  # 轉換動畫持續時間

        # Boss 特殊技能
        self.special_attacks = []  # 特殊攻擊物件列表
        self.last_special_attack = 0  # 上次特殊攻擊時間
        self.special_attack_interval = 3.0  # 特殊攻擊間隔

    def take_damage(self, damage, damage_type="physical"):
        """
        Boss 受傷處理 - 包含階段轉換邏輯\n
        \n
        參數:\n
        damage (int): 受到的傷害\n
        damage_type (str): 傷害類型\n
        \n
        回傳:\n
        int: 實際受到的傷害\n
        """
        # 無敵狀態不受傷
        if self.invulnerable:
            return 0

        # 階段轉換中減少傷害
        if self.phase_transitioning:
            damage = int(damage * 0.3)

        actual_damage = super().take_damage(damage, damage_type)

        # 檢查是否需要階段轉換
        current_health_ratio = self.health / self.max_health
        next_threshold = self.phase_health_thresholds[
            min(self.phase - 1, len(self.phase_health_thresholds) - 1)
        ]

        if current_health_ratio <= next_threshold and self.phase < self.max_phases:
            self.start_phase_transition()

        return actual_damage

    def start_phase_transition(self):
        """
        開始階段轉換\n
        """
        if not self.phase_transitioning:
            self.phase_transitioning = True
            self.transition_timer = 0
            self.invulnerable = True
            self.phase += 1
            print(f"Boss 進入第 {self.phase} 階段！")

    def update_phase_transition(self, dt):
        """
        更新階段轉換狀態\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        """
        if self.phase_transitioning:
            self.transition_timer += dt

            if self.transition_timer >= self.transition_duration:
                self.phase_transitioning = False
                self.invulnerable = False
                self.on_phase_change()

    def on_phase_change(self):
        """
        階段轉換完成時的回調 - 由子類別實作\n
        """
        pass

    def update_special_attacks(self, dt, player):
        """
        更新特殊攻擊\n
        \n
        參數:\n
        dt (float): 時間間隔\n
        player (Player): 玩家物件\n
        """
        current_time = time.time()

        # 檢查是否可以發動特殊攻擊
        if (
            current_time - self.last_special_attack >= self.special_attack_interval
            and not self.phase_transitioning
        ):
            self.perform_special_attack(player)
            self.last_special_attack = current_time

        # 更新現有的特殊攻擊
        self.special_attacks = [
            attack for attack in self.special_attacks if attack.update(dt, player)
        ]

    def perform_special_attack(self, player):
        """
        執行特殊攻擊 - 由子類別實作\n
        \n
        參數:\n
        player (Player): 玩家物件\n
        """
        pass

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製 Boss - 包含階段轉換效果\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 基礎繪製
        super().draw(screen, camera_x, camera_y)

        # 階段轉換特效
        if self.phase_transitioning:
            # 繪製閃爍效果
            flash_alpha = int(128 + 127 * math.sin(self.transition_timer * 10))
            flash_surface = pygame.Surface((self.width, self.height))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill(WHITE)
            screen.blit(flash_surface, (screen_x, screen_y))

        # 無敵狀態的光環效果
        if self.invulnerable:
            pygame.draw.rect(
                screen,
                YELLOW,
                pygame.Rect(
                    screen_x - 5, screen_y - 5, self.width + 10, self.height + 10
                ),
                3,
            )

        # 繪製階段指示
        phase_text = f"階段 {self.phase}/{self.max_phases}"
        font = get_chinese_font(FONT_SIZE_NORMAL)
        text_surface = font.render(phase_text, True, WHITE)
        screen.blit(text_surface, (screen_x, screen_y - 40))

        # 繪製特殊攻擊
        for attack in self.special_attacks:
            attack.draw(screen, camera_x, camera_y)


######################熔岩龍捲Boss######################


class LavaTornadoBoss(Boss):
    """
    熔岩龍捲Boss - 火山場景的終極敵人\n
    \n
    特色能力：\n
    1. 第一階段：熔岩球攻擊 + 小範圍旋風\n
    2. 第二階段：熔岩雨 + 中範圍旋風 + 瞬移\n
    3. 第三階段：熔岩龍捲風 + 大範圍AOE + 連續瞬移\n
    \n
    弱點：冰系和水系攻擊\n
    抗性：火系攻擊\n
    """

    def __init__(self, x, y):
        """
        初始化熔岩龍捲Boss\n
        """
        super().__init__(
            x,
            y,
            LAVA_TORNADO_BOSS_WIDTH,
            LAVA_TORNADO_BOSS_HEIGHT,
            LAVA_TORNADO_BOSS_COLOR,
            LAVA_TORNADO_BOSS_HEALTH,
            LAVA_TORNADO_BOSS_DAMAGE,
            "lava_tornado_boss",
        )

        # 特殊攻擊相關
        self.lava_balls = []  # 熔岩球列表
        self.tornado_radius = 50  # 旋風半徑
        self.is_spinning = False  # 是否在旋轉
        self.spin_timer = 0  # 旋轉計時器
        self.teleport_cooldown = 0  # 瞬移冷卻

        # 階段特定屬性
        self.lava_rain_active = False
        self.lava_rain_timer = 0
        self.mega_tornado_charging = False
        self.mega_tornado_charge_time = 0

    def on_phase_change(self):
        """
        階段轉換時的特殊效果\n
        """
        if self.phase == 2:
            # 第二階段：增加攻擊力和移動速度
            self.damage = int(self.damage * 1.3)
            self.speed = int(self.speed * 1.2)
            self.special_attack_interval = 2.5
            print("熔岩龍捲Boss 進入狂暴狀態！")

        elif self.phase == 3:
            # 第三階段：最大強化
            self.damage = int(self.damage * 1.5)
            self.speed = int(self.speed * 1.4)
            self.special_attack_interval = 2.0
            print("熔岩龍捲Boss 進入終極形態！")

    def perform_special_attack(self, player):
        """
        根據當前階段執行不同的特殊攻擊\n
        """
        if self.phase == 1:
            self.lava_ball_attack(player)
        elif self.phase == 2:
            attack_choice = random.choice(["lava_rain", "tornado_spin", "teleport"])
            if attack_choice == "lava_rain":
                self.lava_rain_attack()
            elif attack_choice == "tornado_spin":
                self.tornado_spin_attack()
            elif attack_choice == "teleport":
                self.teleport_attack(player)
        elif self.phase == 3:
            attack_choice = random.choice(
                ["mega_tornado", "lava_eruption", "combo_attack"]
            )
            if attack_choice == "mega_tornado":
                self.mega_tornado_attack()
            elif attack_choice == "lava_eruption":
                self.lava_eruption_attack()
            elif attack_choice == "combo_attack":
                self.combo_attack(player)

    def lava_ball_attack(self, player):
        """
        熔岩球攻擊 - 第一階段主要攻擊\n
        """
        for i in range(3):  # 發射3顆熔岩球
            angle = math.atan2(player.y - self.y, player.x - self.x) + random.uniform(
                -0.3, 0.3
            )
            velocity_x = math.cos(angle) * 8
            velocity_y = math.sin(angle) * 8

            lava_ball = {
                "x": self.x + self.width // 2,
                "y": self.y + self.height // 2,
                "velocity_x": velocity_x,
                "velocity_y": velocity_y,
                "damage": self.damage,
                "lifetime": 3.0,
                "created_time": time.time(),
            }
            self.lava_balls.append(lava_ball)

    def lava_rain_attack(self):
        """
        熔岩雨攻擊 - 第二階段攻擊\n
        """
        self.lava_rain_active = True
        self.lava_rain_timer = 3.0  # 持續3秒
        print("Boss 發動熔岩雨攻擊！")

    def tornado_spin_attack(self):
        """
        旋風攻擊 - 製造推力區域\n
        """
        self.is_spinning = True
        self.spin_timer = 2.0  # 旋轉2秒
        print("Boss 開始旋轉攻擊！")

    def teleport_attack(self, player):
        """
        瞬移攻擊 - 瞬移到玩家附近\n
        """
        # 隨機選擇玩家周圍的位置
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, 200)
        new_x = player.x + math.cos(angle) * distance
        new_y = player.y + math.sin(angle) * distance

        # 限制在合理範圍內
        new_x = max(50, min(new_x, SCREEN_WIDTH * 3 - 50))
        new_y = max(50, min(new_y, SCREEN_HEIGHT - 100))

        self.x = new_x
        self.y = new_y
        self.update_rect()
        print("Boss 瞬移攻擊！")

    def mega_tornado_attack(self):
        """
        超級龍捲風攻擊 - 第三階段終極技能\n
        """
        self.mega_tornado_charging = True
        self.mega_tornado_charge_time = 2.0
        print("Boss 正在蓄力超級龍捲風！")

    def lava_eruption_attack(self):
        """
        熔岩噴發攻擊 - 全場AOE攻擊\n
        """
        # 在整個場地隨機生成熔岩噴發點
        for i in range(8):
            eruption_x = random.uniform(0, SCREEN_WIDTH * 3)
            eruption_y = random.uniform(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 50)

            eruption = {
                "x": eruption_x,
                "y": eruption_y,
                "radius": 60,
                "damage": self.damage * 1.5,
                "warning_time": 1.0,  # 1秒預警
                "active_time": 2.0,  # 2秒傷害時間
                "created_time": time.time(),
                "phase": "warning",  # warning -> active -> finished
            }
            self.special_attacks.append(LavaEruption(eruption))

        print("Boss 發動全場熔岩噴發！")

    def combo_attack(self, player):
        """
        組合攻擊 - 多種攻擊連續發動\n
        """
        self.lava_ball_attack(player)
        self.tornado_spin_attack()
        # 延遲瞬移
        self.teleport_cooldown = 1.0

    def update(self, player, platforms):
        """
        更新 Boss 狀態\n
        """
        super().update(player, platforms)

        if not self.is_alive:
            return

        dt = 1 / 60  # 假設60FPS

        # 更新階段轉換
        self.update_phase_transition(dt)

        # 更新特殊攻擊
        self.update_special_attacks(dt, player)

        # 更新熔岩球
        self.update_lava_balls(dt)

        # 更新旋轉狀態
        if self.is_spinning:
            self.spin_timer -= dt
            if self.spin_timer <= 0:
                self.is_spinning = False

        # 更新熔岩雨
        if self.lava_rain_active:
            self.lava_rain_timer -= dt
            if self.lava_rain_timer <= 0:
                self.lava_rain_active = False
            else:
                # 持續產生熔岩球
                if random.random() < 0.3:  # 30% 機率每幀產生
                    self.create_rain_lava_ball()

        # 更新超級龍捲風蓄力
        if self.mega_tornado_charging:
            self.mega_tornado_charge_time -= dt
            if self.mega_tornado_charge_time <= 0:
                self.mega_tornado_charging = False
                self.execute_mega_tornado()

        # 更新瞬移冷卻
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt
            if self.teleport_cooldown <= 0:
                self.teleport_attack(player)

    def update_lava_balls(self, dt):
        """
        更新熔岩球位置和碰撞\n
        """
        current_time = time.time()
        active_balls = []

        for ball in self.lava_balls:
            # 更新位置
            ball["x"] += ball["velocity_x"]
            ball["y"] += ball["velocity_y"]

            # 檢查生存時間
            if current_time - ball["created_time"] < ball["lifetime"]:
                active_balls.append(ball)

        self.lava_balls = active_balls

    def create_rain_lava_ball(self):
        """
        創建熔岩雨的熔岩球\n
        """
        # 從天空隨機位置掉落
        rain_ball = {
            "x": random.uniform(0, SCREEN_WIDTH * 3),
            "y": -50,  # 從螢幕上方開始
            "velocity_x": random.uniform(-2, 2),
            "velocity_y": random.uniform(6, 10),
            "damage": self.damage * 0.8,
            "lifetime": 5.0,
            "created_time": time.time(),
        }
        self.lava_balls.append(rain_ball)

    def execute_mega_tornado(self):
        """
        執行超級龍捲風攻擊\n
        """
        tornado = MegaTornado(
            self.x + self.width // 2, self.y + self.height // 2, self.damage * 2
        )
        self.special_attacks.append(tornado)
        print("超級龍捲風發動！")

    def check_lava_ball_collision(self, player):
        """
        檢查熔岩球與玩家的碰撞\n
        """
        for ball in self.lava_balls[:]:  # 使用切片複製避免修改時出錯
            ball_rect = pygame.Rect(ball["x"] - 8, ball["y"] - 8, 16, 16)
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

            if ball_rect.colliderect(player_rect):
                # 玩家受傷
                player.take_damage(ball["damage"])
                # 移除熔岩球
                self.lava_balls.remove(ball)

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製熔岩龍捲Boss和所有特效\n
        """
        super().draw(screen, camera_x, camera_y)

        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 繪製旋轉效果
        if self.is_spinning:
            center_x = screen_x + self.width // 2
            center_y = screen_y + self.height // 2
            for i in range(3):
                radius = self.tornado_radius + i * 20
                pygame.draw.circle(
                    screen, (255, 150, 0), (center_x, center_y), radius, 3
                )

        # 繪製蓄力效果
        if self.mega_tornado_charging:
            center_x = screen_x + self.width // 2
            center_y = screen_y + self.height // 2
            charge_radius = int(100 * (2.0 - self.mega_tornado_charge_time) / 2.0)
            pygame.draw.circle(screen, RED, (center_x, center_y), charge_radius, 5)

        # 繪製熔岩球
        for ball in self.lava_balls:
            ball_screen_x = ball["x"] - camera_x
            ball_screen_y = ball["y"] - camera_y
            if (
                -20 <= ball_screen_x <= SCREEN_WIDTH + 20
                and -20 <= ball_screen_y <= SCREEN_HEIGHT + 20
            ):
                pygame.draw.circle(
                    screen, LAVA_COLOR, (int(ball_screen_x), int(ball_screen_y)), 8
                )
                pygame.draw.circle(
                    screen, YELLOW, (int(ball_screen_x), int(ball_screen_y)), 4
                )


######################特殊攻擊物件######################


class LavaEruption:
    """
    熔岩噴發攻擊物件\n
    """

    def __init__(self, eruption_data):
        self.x = eruption_data["x"]
        self.y = eruption_data["y"]
        self.radius = eruption_data["radius"]
        self.damage = eruption_data["damage"]
        self.warning_time = eruption_data["warning_time"]
        self.active_time = eruption_data["active_time"]
        self.created_time = eruption_data["created_time"]
        self.phase = eruption_data["phase"]

    def update(self, dt, player):
        """
        更新噴發狀態\n
        """
        current_time = time.time()
        elapsed = current_time - self.created_time

        if self.phase == "warning" and elapsed >= self.warning_time:
            self.phase = "active"
        elif self.phase == "active" and elapsed >= self.warning_time + self.active_time:
            self.phase = "finished"
            return False  # 標記為可移除

        # 在活躍階段檢查玩家碰撞
        if self.phase == "active":
            distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
            if distance <= self.radius:
                player.take_damage(self.damage)

        return True  # 繼續存在

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製噴發效果\n
        """
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if self.phase == "warning":
            # 警告階段：紅色圓圈閃爍
            alpha = int(128 + 127 * math.sin(time.time() * 8))
            color = (255, 0, 0, alpha)  # 紅色半透明
            pygame.draw.circle(
                screen, RED, (int(screen_x), int(screen_y)), self.radius, 3
            )
        elif self.phase == "active":
            # 活躍階段：橘色實心圓
            pygame.draw.circle(
                screen, LAVA_COLOR, (int(screen_x), int(screen_y)), self.radius
            )
            pygame.draw.circle(
                screen, YELLOW, (int(screen_x), int(screen_y)), self.radius // 2
            )


class MegaTornado:
    """
    超級龍捲風攻擊物件\n
    """

    def __init__(self, x, y, damage):
        self.x = x
        self.y = y
        self.damage = damage
        self.radius = 100
        self.max_radius = 200
        self.growth_rate = 50  # 每秒成長速度
        self.lifetime = 5.0
        self.created_time = time.time()
        self.rotation = 0

    def update(self, dt, player):
        """
        更新龍捲風\n
        """
        current_time = time.time()
        elapsed = current_time - self.created_time

        if elapsed >= self.lifetime:
            return False

        # 龍捲風成長
        if self.radius < self.max_radius:
            self.radius += self.growth_rate * dt

        # 旋轉效果
        self.rotation += 5 * dt

        # 檢查玩家碰撞
        distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if distance <= self.radius:
            # 對玩家施加向外推力
            if distance > 0:
                push_x = (player.x - self.x) / distance * 300 * dt
                push_y = (player.y - self.y) / distance * 300 * dt
                player.velocity_x += push_x
                player.velocity_y += push_y
            # 造成傷害
            player.take_damage(self.damage * dt)  # 持續傷害

        return True

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製超級龍捲風\n
        """
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 繪製多層旋轉圓圈
        for i in range(5):
            radius = int(self.radius * (i + 1) / 5)
            rotation_offset = self.rotation + i * 0.5
            color_intensity = 255 - i * 30
            color = (color_intensity, color_intensity // 2, 0)

            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), radius, 3)


######################海嘯巨獸Boss######################


class TsunamiBoss(Boss):
    """
    海嘯巨獸Boss - 海底場景的終極敵人\n
    \n
    特色能力：\n
    1. 第一階段：水彈攻擊 + 小型海嘯\n
    2. 第二階段：雷電風暴 + 漩渦攻擊\n
    3. 第三階段：超級海嘯 + 雷電海嘯組合技\n
    \n
    弱點：雷系和火系攻擊\n
    抗性：水系和冰系攻擊\n
    """

    def __init__(self, x, y):
        """
        初始化海嘯巨獸Boss\n
        """
        super().__init__(
            x,
            y,
            TSUNAMI_BOSS_WIDTH,
            TSUNAMI_BOSS_HEIGHT,
            TSUNAMI_BOSS_COLOR,
            TSUNAMI_BOSS_HEALTH,
            TSUNAMI_BOSS_DAMAGE,
            "tsunami_boss",
        )

        self.water_bullets = []
        self.tsunamis = []
        self.whirlpools = []
        self.thunder_strikes = []

    def on_phase_change(self):
        """
        階段轉換特效\n
        """
        if self.phase == 2:
            print("海嘯巨獸 召喚雷電風暴！")
        elif self.phase == 3:
            print("海嘯巨獸 進入終極海嘯形態！")

    def perform_special_attack(self, player):
        """
        海嘯巨獸的特殊攻擊\n
        """
        if self.phase == 1:
            self.water_barrage_attack(player)
        elif self.phase == 2:
            attack_choice = random.choice(
                ["thunder_storm", "whirlpool", "mini_tsunami"]
            )
            if attack_choice == "thunder_storm":
                self.thunder_storm_attack()
            elif attack_choice == "whirlpool":
                self.whirlpool_attack(player)
            elif attack_choice == "mini_tsunami":
                self.mini_tsunami_attack()
        elif self.phase == 3:
            self.mega_tsunami_attack()

    def water_barrage_attack(self, player):
        """
        水彈齊射攻擊\n
        """
        for i in range(8):  # 8發水彈
            angle = (i * math.pi / 4) + random.uniform(-0.2, 0.2)
            velocity_x = math.cos(angle) * 12
            velocity_y = math.sin(angle) * 12

            water_bullet = {
                "x": self.x + self.width // 2,
                "y": self.y + self.height // 2,
                "velocity_x": velocity_x,
                "velocity_y": velocity_y,
                "damage": self.damage * 0.8,
                "lifetime": 4.0,
                "created_time": time.time(),
            }
            self.water_bullets.append(water_bullet)

    def thunder_storm_attack(self):
        """
        雷電風暴攻擊\n
        """
        for i in range(5):
            strike_x = random.uniform(0, SCREEN_WIDTH * 3)
            strike_y = random.uniform(0, SCREEN_HEIGHT)

            thunder_strike = {
                "x": strike_x,
                "y": strike_y,
                "damage": self.damage * 1.5,
                "warning_time": 0.8,
                "created_time": time.time(),
                "phase": "warning",
            }
            self.thunder_strikes.append(thunder_strike)

    def whirlpool_attack(self, player):
        """
        漩渦攻擊\n
        """
        whirlpool = {
            "x": player.x,
            "y": player.y,
            "radius": 80,
            "pull_strength": 150,
            "damage": self.damage,
            "lifetime": 4.0,
            "created_time": time.time(),
        }
        self.whirlpools.append(whirlpool)

    def mini_tsunami_attack(self):
        """
        小型海嘯攻擊\n
        """
        tsunami = {
            "x": 0,
            "y": SCREEN_HEIGHT - 150,
            "width": SCREEN_WIDTH * 3,
            "height": 100,
            "velocity_x": 0,
            "velocity_y": -50,
            "damage": self.damage * 1.2,
            "lifetime": 3.0,
            "created_time": time.time(),
        }
        self.tsunamis.append(tsunami)

    def mega_tsunami_attack(self):
        """
        超級海嘯攻擊\n
        """
        # 創建多重海嘯波
        for i in range(3):
            tsunami = {
                "x": -200 - i * 100,
                "y": SCREEN_HEIGHT - 200 - i * 30,
                "width": SCREEN_WIDTH * 3 + 400,
                "height": 150 + i * 20,
                "velocity_x": 200 + i * 50,
                "velocity_y": 0,
                "damage": self.damage * (1.5 + i * 0.3),
                "lifetime": 6.0,
                "created_time": time.time(),
            }
            self.tsunamis.append(tsunami)

    def update(self, player, platforms):
        """
        更新海嘯巨獸\n
        """
        super().update(player, platforms)

        if not self.is_alive:
            return

        dt = 1 / 60

        self.update_phase_transition(dt)
        self.update_special_attacks(dt, player)
        self.update_water_attacks(dt, player)

    def update_water_attacks(self, dt, player):
        """
        更新所有水系攻擊\n
        """
        current_time = time.time()

        # 更新水彈
        active_bullets = []
        for bullet in self.water_bullets:
            bullet["x"] += bullet["velocity_x"]
            bullet["y"] += bullet["velocity_y"]

            if current_time - bullet["created_time"] < bullet["lifetime"]:
                # 檢查碰撞
                bullet_rect = pygame.Rect(bullet["x"] - 6, bullet["y"] - 6, 12, 12)
                player_rect = pygame.Rect(
                    player.x, player.y, player.width, player.height
                )

                if bullet_rect.colliderect(player_rect):
                    player.take_damage(bullet["damage"])
                else:
                    active_bullets.append(bullet)

        self.water_bullets = active_bullets

        # 更新雷擊
        active_strikes = []
        for strike in self.thunder_strikes:
            elapsed = current_time - strike["created_time"]
            if strike["phase"] == "warning" and elapsed >= strike["warning_time"]:
                strike["phase"] = "active"
                # 檢查玩家是否在雷擊範圍內
                distance = math.sqrt(
                    (player.x - strike["x"]) ** 2 + (player.y - strike["y"]) ** 2
                )
                if distance <= 30:  # 雷擊範圍
                    player.take_damage(strike["damage"])
                    # 麻痺效果
                    from ..core.game_objects import StatusEffect

                    paralysis = StatusEffect("paralysis", 2.0)
                    player.status_effects.append(paralysis)
            elif (
                strike["phase"] == "active" and elapsed >= strike["warning_time"] + 0.2
            ):
                continue  # 雷擊結束，不加入 active_strikes
            else:
                active_strikes.append(strike)

        self.thunder_strikes = active_strikes

        # 更新漩渦
        active_whirlpools = []
        for whirlpool in self.whirlpools:
            if current_time - whirlpool["created_time"] < whirlpool["lifetime"]:
                # 檢查玩家是否在漩渦範圍內
                distance = math.sqrt(
                    (player.x - whirlpool["x"]) ** 2 + (player.y - whirlpool["y"]) ** 2
                )
                if distance <= whirlpool["radius"]:
                    # 向漩渦中心拉扯
                    if distance > 0:
                        pull_x = (
                            (whirlpool["x"] - player.x)
                            / distance
                            * whirlpool["pull_strength"]
                            * dt
                        )
                        pull_y = (
                            (whirlpool["y"] - player.y)
                            / distance
                            * whirlpool["pull_strength"]
                            * dt
                        )
                        player.velocity_x += pull_x
                        player.velocity_y += pull_y

                    # 在中心造成傷害
                    if distance <= 20:
                        player.take_damage(whirlpool["damage"] * dt)

                active_whirlpools.append(whirlpool)

        self.whirlpools = active_whirlpools

        # 更新海嘯
        active_tsunamis = []
        for tsunami in self.tsunamis:
            if current_time - tsunami["created_time"] < tsunami["lifetime"]:
                tsunami["x"] += tsunami["velocity_x"] * dt
                tsunami["y"] += tsunami["velocity_y"] * dt

                # 檢查玩家碰撞
                tsunami_rect = pygame.Rect(
                    tsunami["x"], tsunami["y"], tsunami["width"], tsunami["height"]
                )
                player_rect = pygame.Rect(
                    player.x, player.y, player.width, player.height
                )

                if tsunami_rect.colliderect(player_rect):
                    player.take_damage(tsunami["damage"])
                    # 海嘯推力
                    player.velocity_x += tsunami["velocity_x"] * 0.5 * dt
                    player.velocity_y += tsunami["velocity_y"] * 0.5 * dt

                active_tsunamis.append(tsunami)

        self.tsunamis = active_tsunamis

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製海嘯巨獸和所有攻擊\n
        """
        super().draw(screen, camera_x, camera_y)

        # 繪製水彈
        for bullet in self.water_bullets:
            bullet_screen_x = bullet["x"] - camera_x
            bullet_screen_y = bullet["y"] - camera_y
            if (
                -20 <= bullet_screen_x <= SCREEN_WIDTH + 20
                and -20 <= bullet_screen_y <= SCREEN_HEIGHT + 20
            ):
                pygame.draw.circle(
                    screen, CYAN, (int(bullet_screen_x), int(bullet_screen_y)), 6
                )
                pygame.draw.circle(
                    screen, WHITE, (int(bullet_screen_x), int(bullet_screen_y)), 3
                )

        # 繪製雷擊
        for strike in self.thunder_strikes:
            strike_screen_x = strike["x"] - camera_x
            strike_screen_y = strike["y"] - camera_y

            if strike["phase"] == "warning":
                pygame.draw.circle(
                    screen, YELLOW, (int(strike_screen_x), int(strike_screen_y)), 30, 3
                )
            elif strike["phase"] == "active":
                pygame.draw.circle(
                    screen, WHITE, (int(strike_screen_x), int(strike_screen_y)), 30
                )

        # 繪製漩渦
        for whirlpool in self.whirlpools:
            whirl_screen_x = whirlpool["x"] - camera_x
            whirl_screen_y = whirlpool["y"] - camera_y

            for i in range(3):
                radius = int(whirlpool["radius"] * (i + 1) / 3)
                alpha = 150 - i * 30
                pygame.draw.circle(
                    screen, CYAN, (int(whirl_screen_x), int(whirl_screen_y)), radius, 2
                )

        # 繪製海嘯
        for tsunami in self.tsunamis:
            tsunami_screen_x = tsunami["x"] - camera_x
            tsunami_screen_y = tsunami["y"] - camera_y

            tsunami_rect = pygame.Rect(
                tsunami_screen_x, tsunami_screen_y, tsunami["width"], tsunami["height"]
            )
            pygame.draw.rect(screen, WATER_COLOR, tsunami_rect)
            pygame.draw.rect(screen, WHITE, tsunami_rect, 3)


######################Boss管理器######################


class BossManager:
    """
    Boss 戰鬥管理器\n
    \n
    負責：\n
    1. Boss 生成和管理\n
    2. Boss 戰鬥狀態控制\n
    3. Boss 戰鬥UI顯示\n
    4. Boss 擊敗獎勵\n
    """

    def __init__(self):
        self.current_boss = None
        self.boss_active = False
        self.boss_battle_music_playing = False
        self.boss_spawn_timer = 0
        self.boss_defeated_timer = 0

    def should_spawn_boss(self, level_manager, wave_number):
        """
        判斷是否應該生成Boss\n
        \n
        參數:\n
        level_manager (LevelManager): 關卡管理器\n
        wave_number (int): 當前波次\n
        \n
        回傳:\n
        bool: 是否生成Boss\n
        """
        # 每3波生成一次Boss
        return wave_number % 3 == 0 and wave_number > 0

    def spawn_boss(self, level_manager):
        """
        根據關卡主題生成對應的Boss\n
        """
        if self.current_boss and self.current_boss.is_alive:
            return

        # 根據關卡主題決定Boss類型
        theme = level_manager.level_theme
        spawn_x = level_manager.level_width // 2
        spawn_y = level_manager.level_height - 300

        if theme == "volcano":
            self.current_boss = LavaTornadoBoss(spawn_x, spawn_y)
            print("🌋 熔岩龍捲Boss 出現！")
        elif theme == "underwater":
            self.current_boss = TsunamiBoss(spawn_x, spawn_y)
            print("🌊 海嘯巨獸Boss 出現！")
        elif theme == "hurricane":
            # 暫時使用熔岩龍捲Boss，可以後續添加風暴Boss
            self.current_boss = LavaTornadoBoss(spawn_x, spawn_y)
            print("🌪️ 風暴Boss 出現！")

        self.boss_active = True
        self.boss_battle_music_playing = True

    def update(self, dt, player, platforms):
        """
        更新Boss戰鬥\n
        """
        if not self.boss_active or not self.current_boss:
            return

        # 更新Boss
        self.current_boss.update(player, platforms)

        # 檢查Boss是否被擊敗
        if not self.current_boss.is_alive:
            self.boss_defeated_timer += dt
            if self.boss_defeated_timer >= 2.0:  # 2秒後清理
                self.boss_active = False
                self.boss_battle_music_playing = False
                self.boss_defeated_timer = 0
                print("Boss 已被擊敗！")
                return True  # 返回Boss被擊敗的信號

        return False

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製Boss和Boss戰UI\n
        """
        if not self.boss_active or not self.current_boss:
            return

        # 繪製Boss
        self.current_boss.draw(screen, camera_x, camera_y)

        # 繪製Boss血量條
        self.draw_boss_health_bar(screen)

    def draw_boss_health_bar(self, screen):
        """
        繪製Boss血量條\n
        """
        if not self.current_boss:
            return

        # Boss血量條位置（螢幕頂部）
        bar_width = SCREEN_WIDTH - 100
        bar_height = 20
        bar_x = 50
        bar_y = 50

        # 背景（黑色）
        bg_rect = pygame.Rect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4)
        pygame.draw.rect(screen, BLACK, bg_rect)

        # 血量條背景（深紅色）
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (100, 0, 0), bg_rect)

        # 當前血量（紅色）
        health_ratio = max(0, self.current_boss.health / self.current_boss.max_health)
        current_width = int(bar_width * health_ratio)
        health_rect = pygame.Rect(bar_x, bar_y, current_width, bar_height)
        pygame.draw.rect(screen, RED, health_rect)

        # Boss名稱和血量文字
        font = get_chinese_font(FONT_SIZE_NORMAL)
        boss_name = f"Boss: {self.current_boss.boss_type.replace('_', ' ').title()}"
        health_text = f"{self.current_boss.health}/{self.current_boss.max_health}"

        name_surface = font.render(boss_name, True, WHITE)
        health_surface = font.render(health_text, True, WHITE)

        screen.blit(name_surface, (bar_x, bar_y - 25))
        screen.blit(
            health_surface, (bar_x + bar_width - health_surface.get_width(), bar_y - 25)
        )

    def get_current_boss(self):
        """
        獲取當前Boss\n
        \n
        回傳:\n
        Boss: 當前Boss物件，如果沒有則返回None\n
        """
        return self.current_boss if self.boss_active else None
