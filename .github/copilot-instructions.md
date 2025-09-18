# AI Coding Agent Instructions for Elemental Parkour Shooter

## 專案概覽

這是一個基於 Pygame 的 2D 跑酷射擊遊戲，結合元素屬性系統和嚴格模組化架構。玩家使用跑酷技能（雙跳、爬牆）在 30 層垂直關卡中對抗具有元素弱點的怪物。

## 核心架構設計

### 1. 模組化結構與執行方式

```
src/
├── main.py              # 主遊戲迴圈和狀態管理
├── config.py            # 集中化常數配置 + 字體管理
├── core/                # 核心系統（元素、基礎物件）
├── entities/            # 遊戲實體（玩家、武器、怪物）
├── systems/             # 管理器系統（關卡、Boss、怪物管理）
└── utils/               # 工具函數
```

**關鍵原則**:

- 每個模組都有明確的職責，新功能必須放在正確的目錄中
- 支援雙重導入模式：模組模式 (`python3 -m src.main`) 和直接執行
- 所有檔案使用 try/except ImportError 模式處理相對/絕對導入

**導入模式範例**:

```python
try:
    from ..config import *
    from ..core.game_objects import GameObject
except ImportError:
    from src.config import *
    from src.core.game_objects import GameObject
```

### 2. 管理器模式與更新順序

每個複雜系統都有專用管理器，**必須嚴格按照以下順序更新**（在 `main.py` 中）：

```python
# 固定更新順序 - 破壞此順序會導致狀態不一致
player_update_result = self.player.update(platforms)
level_update_result = self.level_manager.update(dt, self.player, bullets)
monster_update_result = self.monster_manager.update(player, platforms, dt)
collision_results = self.weapon_manager.update(targets=all_targets)
self.damage_display.update()
```

**管理器職責**:

- `MonsterManager`: 怪物生成、AI、Boss 戰、投射物管理
- `WeaponManager`: 子彈物理、碰撞檢測、必殺技系統
- `LevelManager`: 30 層跑酷平台生成、星星系統
- `DamageDisplayManager`: 浮動傷害數字、UI 效果

**管理器通信模式**:

```python
# 管理器間通過字典返回值通信，避免直接耦合
monster_update_result = self.monster_manager.update(player, platforms, dt)
if monster_update_result["boss_defeated"]:
    # 在Boss位置生成勝利星星
    self.level_manager.star_x = monster_update_result["boss_death_x"]
    self.level_manager.star_y = monster_update_result["boss_death_y"] - 50
```

## 元素屬性系統

**絕對關鍵**: 所有元素相關邏輯都集中於 `src/core/element_system.py`：

```python
# 核心 API
ElementSystem.calculate_damage(base_damage, attacker_element, target_type)
ElementSystem.get_status_effect(attacker_element, target_type)
ElementSystem.get_effectiveness_rating(attacker_element, target_type)
```

**使用模式**（在 `weapon.py` 中）：

```python
# 子彈傷害計算
damage, status_effect = bullet.get_damage_against_target(target_type)
target.take_damage(damage)
if status_effect:
    target.add_status_effect(status_effect["type"], status_effect["duration"], status_effect["intensity"])
```

**屬性剋制關係**:

- `water` → `lava_monster` (2x 弱點攻擊)
- `thunder` → `water_monster` (2x 弱點攻擊 + 麻痺)
- `fire` → `water_monster` (1.5x 額外傷害)
- `ice` → `tornado_monster` (2x 弱點攻擊 + 減速)
- `fire` → `lava_monster` (0.5x 抗性)

## 遊戲平衡與難度配置

### 配置集中化原則

所有數值調整都在 `config.py` 中進行，已針對挑戰性進行調整：

```python
# 怪物難度已強化（+50% 血量/攻擊力）
LAVA_MONSTER_HEALTH = 120  # 提升血量 80→120 (+50%)
LAVA_MONSTER_DAMAGE = 45   # 提升傷害 30→45 (+50%)

# Boss 系統更具挑戰性
LAVA_TORNADO_BOSS_HEALTH = 1500  # 提升Boss血量 1000→1500 (+50%)

# 玩家容錯率降低
PLAYER_MAX_HEALTH = 800    # 玩家血量增加為兩倍
PLAYER_LIVES = 2           # 從3次降到2次
```

### 動態難度調整模式

在 `MonsterManager` 中實現：

- 生成間隔從 4 秒縮短到 3 秒
- 最大怪物數量控制在 3 隻
- 每波屬性增長率提升（血量+15%，攻擊力+8%）

### 武器系統平衡

四種武器的差異化設計：

```python
# 機關槍：攻擊力低但射速極快
"machine_gun": {"fire_rate": 0.1, "damage": 8}

# 衝鋒槍：攻擊力高射速中等
"assault_rifle": {"fire_rate": 0.4, "damage": 40}

# 散彈槍：近距離高傷害（5發彈丸）
"shotgun": {"pellet_count": 5, "damage": 25}

# 狙擊槍：高傷害低射速
"sniper": {"fire_rate": 1.5, "damage": 90}
```

## 開發者工作流程

### 執行命令

```bash
# 推薦執行方式 (模組模式，避免導入問題)
python3 -m src.main

# 使用啟動腳本 (包含預檢查)
./scripts/start_game.sh

# 快速開發測試
python3 main.py
```

### 碰撞檢測架構

專案有多個獨立的碰撞系統，**不要合併**：

- `WeaponManager.check_bullet_collisions()`: 玩家子彈對怪物
- `MonsterManager.update_boss_fire_bullets()`: Boss 火焰子彈對玩家
- `Player.handle_collisions()`: 玩家對平台物理
- `Monster.handle_collisions()`: 怪物對平台物理

### 音效系統架構

- 音效路徑集中於 `config.py` 的音效設定區段
- 動態音量調整：`play_shooting_sound(damage)` 根據傷害調整音量
- 多頻道播放：必殺技音效同時播放 3 次增強效果
- 音效載入失敗時優雅降級，不影響遊戲運行

## 專案特定慣例

### 導入模式

所有模組都使用雙重導入模式：

```python
# 標準模式，支持直接執行和模組執行
try:
    from ..config import *
    from ..core.game_objects import GameObject
except ImportError:
    from src.config import *
    from src.core.game_objects import GameObject
```

### 字體系統

使用 `get_chinese_font(size)` 函數處理繁體中文字體：

- 支持字體緩存避免重複載入
- 自動降級到系統預設字體
- macOS 特定字體路徑：`/System/Library/Fonts/STHeiti Light.ttc`

### 攝影機系統

所有 draw 方法都需要處理攝影機偏移：

```python
def draw(self, screen, camera_x=0, camera_y=0):
    screen_x = self.x - camera_x
    screen_y = self.y - camera_y
    # 繪製邏輯...
```

### 怪物 AI 與投射物

- 某些怪物有獨立的投射物系統（如 `WaterMonster.water_bullets`）
- 怪物 AI 使用平台邊界檢測避免掉落：`check_platform_boundary()`
- Boss 系統已簡化，Boss 作為強化版怪物在 `MonsterManager` 中管理

### 程式碼風格

- 命名：變數/函式為 snake_case，類別為 PascalCase
- 註解：統一使用繁體中文；所有 public 方法需完整 docstring
- 主程式：不使用 `if __name__ == "__main__":` 慣例，直接呼叫 `main()`

## 常見開發任務

### 平衡調整模式

1. **怪物數值**: 修改 `config.py` 中對應常數
2. **生成頻率**: 調整 `MonsterManager.spawn_interval`
3. **關卡難度**: 修改 `LevelManager.generate_parkour_platforms()` 中的平台參數
4. **Boss 強度**: 調整 `MonsterManager.spawn_boss()` 中的 Boss 屬性倍數

### 新增怪物

1. 在 `entities/monsters.py` 繼承 `Monster` 類別
2. 更新 `config.py` 增加怪物常數
3. 在 `ElementSystem` 定義弱點和抗性關係
4. 把生成邏輯加到 `MonsterManager.spawn_monster()`

### 新增狀態效果

1. 在 `ElementSystem.STATUS_EFFECT_MAP` 定義效果配置
2. 確保目標物件有 `add_status_effect()` 方法
3. 在怪物的 `update()` 方法中處理效果邏輯

## 常見問題與調試

### 模組導入錯誤

- 使用 `python3 -m src.main` 而不是直接執行
- 確保所有 `__init__.py` 檔案存在

### 字體顯示問題

- 使用 `get_chinese_font(size)` 處理中文字體
- 字體載入失敗會自動降級，檢查 console 輸出

### 碰撞與顯示問題

- 所有 draw 方法座標需要減去攝影機偏移
- 碰撞檢測在邏輯座標系進行，顯示在螢幕座標系

### 怪物投射物系統

- 水怪使用獨立的 `water_bullets` 列表管理投射物
- 每個投射物包含位置、速度、傷害、生存時間等屬性
- 投射物更新在怪物的 `update()` 方法中獨立處理

### 性能與平衡

- 怪物數量控制在 6 個以內
- 平台生成間距確保可達性
- 元素效果持續時間不超過 3 秒

## 交付建議

每次變更應包含：

- 簡短的功能描述
- 修改的檔案清單
- 本地測試步驟
- 如涉及平衡調整，提供測試數值範例

---

**核心原則**: 保持模組化、集中處理元素邏輯、使用繁體中文註解。詳細風格規範參考 `.github/instructions/info.instructions.md`。
