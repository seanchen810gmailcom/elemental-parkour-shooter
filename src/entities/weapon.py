######################載入套件######################
import pygame
import math
import time

# 支援直接執行和模組執行兩種方式
try:
    from ..config import *
    from ..core.game_objects import GameObject
except ImportError:
    from src.config import *
    from src.core.game_objects import GameObject

######################子彈類別######################


class Bullet(GameObject):
    """
    子彈類別 - 處理各種屬性子彈的飛行和效果\n
    \n
    支援四種元素屬性子彈：\n
    1. 水彈 - 對岩漿怪造成雙倍傷害\n
    2. 冰彈 - 造成減速效果\n
    3. 雷彈 - 對水怪造成雙倍傷害和麻痺效果\n
    4. 火彈 - 高傷害但對岩漿怪抗性\n
    \n
    參數:\n
    x (float): 子彈初始 X 座標\n
    y (float): 子彈初始 Y 座標\n
    direction_x (float): X 方向的移動向量\n
    direction_y (float): Y 方向的移動向量\n
    bullet_type (str): 子彈屬性類型\n
    """

    def __init__(self, x, y, direction_x, direction_y, bullet_type):
        # 根據武器類型設定顏色
        weapon_colors = {
            "machine_gun": (255, 165, 0),  # 橘色
            "assault_rifle": (128, 0, 128),  # 紫色
            "shotgun": (255, 0, 0),  # 紅色
            "sniper": (0, 255, 255),  # 青色
        }

        color = weapon_colors.get(bullet_type, WHITE)
        super().__init__(x, y, BULLET_SIZE, BULLET_SIZE, color)

        # 移動屬性
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = BULLET_SPEED

        # 子彈屬性
        self.bullet_type = bullet_type
        self.damage = self.get_base_damage()

        # 狀態管理
        self.is_active = True
        self.max_distance = 9999  # 讓子彈飛得超級遠，永遠不會因為距離而消失
        self.distance_traveled = 0

        # 記錄初始位置（用來計算飛行距離）
        self.start_x = x
        self.start_y = y

        # 新增武器類型支援
        self.weapon_type = (
            bullet_type  # 武器類型：machine_gun, assault_rifle, shotgun, sniper
        )

    def get_base_damage(self):
        """
        獲取子彈的基礎傷害值\n
        \n
        回傳:\n
        int: 根據武器類型回傳對應的基礎傷害\n
        """
        damage_values = {
            "machine_gun": 15,  # 機關槍：攻擊力低
            "assault_rifle": 40,  # 衝鋒槍：攻擊力高
            "shotgun": 25,  # 散彈槍：攻擊力中等
            "sniper": 100,  # 狙擊槍：攻擊力超高
        }
        return damage_values.get(self.bullet_type, 20)

    def update(self):
        """
        更新子彈位置和狀態 - 每幀執行的移動邏輯\n
        \n
        處理：\n
        1. 根據方向和速度移動子彈\n
        2. 計算飛行距離\n
        3. 檢查是否超出射程\n
        4. 檢查是否飛出螢幕邊界\n
        """
        if not self.is_active:
            return

        # 根據方向向量移動子彈
        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed

        # 計算已飛行的距離
        distance_x = self.x - self.start_x
        distance_y = self.y - self.start_y
        self.distance_traveled = math.sqrt(distance_x**2 + distance_y**2)

        # 檢查是否超出最大射程（已設為9999，基本不會觸發）
        if self.distance_traveled > self.max_distance:
            self.is_active = False

        # 移除螢幕邊界檢查，讓子彈永遠飛行

        # 更新碰撞矩形
        self.update_rect()

    def get_damage_against_target(self, target_type):
        """
        計算對特定目標的傷害值 - 簡化版本，不使用元素系統\n
        \n
        參數:\n
        target_type (str): 目標怪物類型\n
        \n
        回傳:\n
        tuple: (damage, status_effect_info)\n
        """
        # 直接返回基礎傷害，不考慮元素剋制
        final_damage = self.damage

        # 不使用狀態效果
        status_effect = None

        return final_damage, status_effect

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製子彈 - 根據武器類型使用不同視覺效果\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        \n
        繪製方式：\n
        - 機關槍：小圓形\n
        - 衝鋒槍：矩形\n
        - 散彈槍：三角形\n
        - 狙擊槍：大圓形\n
        """
        # 計算螢幕位置
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if not self.is_active:
            return

        center_x = int(screen_x + self.width // 2)
        center_y = int(screen_y + self.height // 2)
        radius = self.width // 2

        if self.bullet_type == "machine_gun":
            # 機關槍：小圓形
            pygame.draw.circle(screen, self.color, (center_x, center_y), radius // 2)

        elif self.bullet_type == "assault_rifle":
            # 衝鋒槍：矩形
            bullet_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
            pygame.draw.rect(screen, self.color, bullet_rect)

        elif self.bullet_type == "shotgun":
            # 散彈槍：三角形
            points = [
                (center_x, center_y - radius),  # 頂點
                (center_x - radius, center_y + radius),  # 左下
                (center_x + radius, center_y + radius),  # 右下
            ]
            pygame.draw.polygon(screen, self.color, points)

        elif self.bullet_type == "sniper":
            # 狙擊槍：大圓形
            pygame.draw.circle(screen, self.color, (center_x, center_y), radius)
            # 內圈顯示威力
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius // 2)


######################武器管理器類別######################


class WeaponManager:
    """
    武器管理器 - 統一管理所有子彈和攻擊行為\n
    \n
    負責：\n
    1. 子彈的生成和銷毀\n
    2. 子彈與目標的碰撞檢測\n
    3. 近戰攻擊的處理\n
    4. 武器系統的整體更新\n
    """

    def __init__(self):
        self.bullets = []  # 所有活躍的子彈列表

    def create_bullet(self, bullet_info):
        """
        根據玩家射擊資訊建立新子彈\n
        \n
        參數:\n
        bullet_info (list or dict): 包含子彈資訊的字典或列表\n
        \n
        回傳:\n
        list: 新建立的子彈物件列表\n
        """
        if bullet_info is None:
            return []

        new_bullets = []

        # 處理多發子彈的情況（散彈槍）
        if isinstance(bullet_info, list):
            for info in bullet_info:
                bullet = self._create_single_bullet(info)
                if bullet:
                    new_bullets.append(bullet)
        else:
            # 單發子彈
            bullet = self._create_single_bullet(bullet_info)
            if bullet:
                new_bullets.append(bullet)

        self.bullets.extend(new_bullets)
        return new_bullets

    def _create_single_bullet(self, info):
        """
        創建單發子彈\n
        \n
        參數:\n
        info (dict): 子彈資訊\n
        \n
        回傳:\n
        Bullet: 子彈物件\n
        """
        bullet = Bullet(
            info["start_x"],
            info["start_y"],
            info["direction_x"],
            info["direction_y"],
            info["type"],
        )

        # 設定武器特定屬性
        if "damage" in info:
            bullet.damage = info["damage"]
        if "speed" in info:
            bullet.speed = info["speed"]

        return bullet

    def handle_melee_attack(self, melee_info, targets):
        """
        處理近戰攻擊 - 檢查攻擊範圍內的目標\n
        \n
        參數:\n
        melee_info (dict): 近戰攻擊資訊\n
        targets (list): 可能被攻擊的目標列表\n
        \n
        回傳:\n
        list: 被擊中的目標列表\n
        """
        if melee_info is None:
            return []

        hit_targets = []
        attack_rect = melee_info["attack_rect"]

        for target in targets:
            if hasattr(target, "rect") and attack_rect.colliderect(target.rect):
                # 目標被近戰攻擊擊中
                damage = melee_info["damage"]
                knockback = melee_info["knockback"]
                direction = melee_info["direction"]

                # 對目標造成傷害
                if hasattr(target, "take_damage"):
                    target.take_damage(damage)

                # 對目標施加擊退效果
                if hasattr(target, "apply_knockback"):
                    target.apply_knockback(knockback, direction)

                hit_targets.append(target)

        return hit_targets

    def update_bullets(self):
        """
        更新所有子彈的狀態 - 移除非活躍的子彈\n
        """
        # 更新每顆子彈
        for bullet in self.bullets:
            bullet.update()

        # 移除非活躍的子彈
        self.bullets = [bullet for bullet in self.bullets if bullet.is_active]

    def check_bullet_collisions(self, targets):
        """
        檢查子彈與目標的碰撞 - 處理命中效果\n
        \n
        參數:\n
        targets (list): 可能被子彈擊中的目標列表\n
        \n
        回傳:\n
        list: 發生碰撞的資訊列表\n
        """
        collision_results = []
        bullets_to_remove = []

        for bullet in self.bullets:
            if not bullet.is_active:
                continue

            for target in targets:
                if hasattr(target, "rect") and bullet.rect.colliderect(target.rect):
                    # 子彈擊中目標

                    # 計算傷害（考慮屬性剋制）
                    target_type = getattr(target, "monster_type", "unknown")
                    damage, status_effect = bullet.get_damage_against_target(
                        target_type
                    )

                    # 對目標造成傷害
                    if hasattr(target, "take_damage"):
                        target.take_damage(damage)

                    # 施加狀態效果
                    if status_effect and hasattr(target, "add_status_effect"):
                        target.add_status_effect(
                            status_effect["type"],
                            status_effect["duration"],
                            status_effect["intensity"],
                        )

                    # 記錄碰撞結果
                    collision_info = {
                        "bullet": bullet,
                        "target": target,
                        "damage": damage,
                        "status_effect": status_effect,
                    }
                    collision_results.append(collision_info)

                    # 標記子彈為待移除
                    bullets_to_remove.append(bullet)
                    break  # 子彈只能擊中一個目標

        # 移除擊中目標的子彈
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                bullet.is_active = False

        return collision_results

    def update(self, targets=None):
        """
        武器系統的主要更新方法\n
        \n
        參數:\n
        targets (list): 可能的攻擊目標列表\n
        \n
        回傳:\n
        list: 所有碰撞結果\n
        """
        # 更新所有子彈
        self.update_bullets()

        # 檢查子彈碰撞
        collision_results = []
        if targets:
            collision_results = self.check_bullet_collisions(targets)

        return collision_results

    def draw(self, screen, camera_x=0, camera_y=0):
        """
        繪製所有武器相關元素\n
        \n
        參數:\n
        screen (pygame.Surface): 要繪製到的螢幕表面\n
        camera_x (int): 攝影機 x 偏移\n
        camera_y (int): 攝影機 y 偏移\n
        """
        # 繪製所有活躍的子彈
        for bullet in self.bullets:
            bullet.draw(screen, camera_x, camera_y)

    def get_bullet_count(self):
        """
        獲取當前活躍子彈數量 - 用於性能監控\n
        \n
        回傳:\n
        int: 活躍子彈數量\n
        """
        return len([bullet for bullet in self.bullets if bullet.is_active])

    def clear_all_bullets(self):
        """
        清除所有子彈 - 用於關卡重置或遊戲結束\n
        """
        self.bullets.clear()
