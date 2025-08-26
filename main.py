######################載入套件######################
import pygame
import sys
import time
from config import *
from game_objects import *
from player import Player
from weapon import WeaponManager
from monster_manager import MonsterManager
from damage_display import DamageDisplayManager
from level_system import LevelManager

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

        # 建立遊戲視窗
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("跑酷射擊大冒險 - Elemental Parkour Shooter")

        # 設定遊戲時鐘，控制幀率
        self.clock = pygame.time.Clock()

        # 遊戲狀態管理
        self.game_state = "playing"  # 目前先直接開始遊戲，之後可加入選單
        self.running = True

        # 分數系統
        self.score = 0
        self.font = pygame.font.Font(None, SCORE_FONT_SIZE)

        # 初始化遊戲物件
        self.player = Player(100, SCREEN_HEIGHT - 200)  # 在安全位置生成玩家
        self.weapon_manager = WeaponManager()  # 武器系統管理器
        self.monster_manager = MonsterManager()  # 怪物系統管理器
        self.damage_display = DamageDisplayManager()  # 傷害顯示管理器
        self.level_manager = LevelManager()  # 關卡場景管理器

        # 攝影機系統
        self.camera_x = 0
        self.camera_y = 0

        # 時間管理
        self.last_update_time = time.time()

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

        # 處理連續按鍵和滑鼠輸入
        if self.game_state == "playing" and self.player.is_alive:
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            self.player.handle_input(keys, mouse_buttons)

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

            # 更新玩家狀態
            if self.player.is_alive:
                # 使用關卡管理器的平台資料
                platforms = self.level_manager.get_platforms()
                self.player.update(platforms)

                # 檢查玩家與陷阱的碰撞
                hazard_damage = self.level_manager.check_hazard_collisions(self.player)
                if hazard_damage > 0:
                    self.player.take_damage(hazard_damage)

                # 處理玩家的射擊
                bullet_info = (
                    self.player.shoot()
                    if self.player.keys_pressed.get("shoot", False)
                    else None
                )
                if bullet_info:
                    self.weapon_manager.create_bullet(bullet_info)

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

                # 檢查玩家是否死亡
                if not self.player.is_alive:
                    self.game_state = "game_over"

            # 更新關卡系統
            bullets = self.weapon_manager.bullets
            self.level_manager.update(dt, self.player, bullets)

            # 更新攝影機
            self.update_camera()

            # 更新怪物系統
            platforms = self.level_manager.get_platforms()
            monster_update_result = self.monster_manager.update(
                self.player, platforms, dt
            )

            # 根據怪物擊殺數增加分數
            if monster_update_result["monsters_killed"] > 0:
                self.score += monster_update_result["monsters_killed"] * 50

            # 波次推進時額外得分
            if monster_update_result["wave_advanced"]:
                self.score += 200

            # 更新武器系統（子彈飛行等）
            collision_results = self.weapon_manager.update(
                targets=self.monster_manager.monsters
            )

            # 處理子彈碰撞結果
            for collision in collision_results:
                # 每發子彈擊中得10分
                self.score += 10

                # 顯示傷害數字
                target = collision["target"]
                bullet = collision["bullet"]
                damage = collision["damage"]

                # 在怪物位置顯示傷害數字
                self.damage_display.add_damage_number(
                    target.x + target.width // 2,
                    target.y,
                    damage,
                    bullet.bullet_type,
                    target.monster_type,
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

            # 繪製 UI 元素（固定在螢幕上，不受攝影機影響）
            self.player.draw_health_bar(self.screen)
            self.player.draw_bullet_ui(self.screen)

            # 獲取怪物統計資訊
            monster_stats = self.monster_manager.get_monster_stats()
            level_info = self.level_manager.get_level_info()

            # 繪製遊戲資訊
            info_texts = [
                f"分數: {self.score}",
                f"關卡: {level_info['level']} ({level_info['theme'].capitalize()})",
                f"波次: {monster_stats['current_wave']}",
                f"怪物: {monster_stats['total_alive']}/{monster_stats['max_monsters']}",
                f"擊殺: {monster_stats['total_killed']}",
                f"子彈: {self.weapon_manager.get_bullet_count()}",
            ]

            for i, text in enumerate(info_texts):
                rendered_text = self.font.render(text, True, SCORE_COLOR)
                self.screen.blit(rendered_text, (10, 10 + i * 30))

            # 繪製怪物類型統計
            type_info = [
                f"岩漿: {monster_stats['type_counts']['lava']}",
                f"水: {monster_stats['type_counts']['water']}",
                f"風: {monster_stats['type_counts']['tornado']}",
            ]

            small_font = pygame.font.Font(None, 24)
            for i, text in enumerate(type_info):
                rendered_text = small_font.render(text, True, WHITE)
                self.screen.blit(rendered_text, (SCREEN_WIDTH - 150, 10 + i * 25))

            # 繪製控制說明
            instructions = [
                "WASD/方向鍵: 移動和跳躍",
                "滑鼠左鍵: 射擊",
                "滑鼠右鍵: 近戰攻擊",
                "1234: 切換子彈類型",
                "ESC: 離開遊戲",
            ]

            font_small = pygame.font.Font(None, 20)
            for i, instruction in enumerate(instructions):
                text = font_small.render(instruction, True, WHITE)
                self.screen.blit(text, (10, SCREEN_HEIGHT - 120 + i * 22))

        elif self.game_state == "game_over":
            # 繪製遊戲結束畫面
            game_over_text = self.font.render("遊戲結束！", True, RED)
            text_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(game_over_text, text_rect)

            restart_text = self.font.render("按 ESC 離開遊戲", True, WHITE)
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            self.screen.blit(restart_text, restart_rect)

        # 更新整個螢幕顯示
        pygame.display.flip()

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


# 啟動遊戲
main()
