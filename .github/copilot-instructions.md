# AI Coding Agent Instructions for Elemental Parkour Shooter

## 專案概覽

這是一個基於 Pygame 的 2D 跑酷射擊遊戲，結合元素屬性系統和嚴格模組化架構。玩家使用跑酷技能（雙跳、爬牆）在程序生成的關卡中對抗具有元素弱點的怪物。

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

### 2. 管理器模式

每個複雜系統都有專用管理器，必須提供 `update()` 方法並在主迴圈固定順序呼叫：

- `MonsterManager`: 怪物生成、AI、碰撞
- `WeaponManager`: 子彈物理、碰撞檢測
- `LevelManager`: 程序生成平台、環境物件
- `DamageDisplayManager`: 浮動傷害數字

**關鍵更新順序**（在 `main.py` 中）：

1. Player 更新（包含移動和射擊）
2. LevelManager 更新（平台和星星）
3. MonsterManager 更新（AI 和生成）
4. WeaponManager 更新（子彈碰撞）
5. DamageDisplayManager 更新（UI 效果）

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

### 屬性剋制關係（可在 ElementSystem 調整）：

- 水 → 岩漿怪（2x 傷害）
- 雷 → 水怪（2x 傷害 + 麻痺效果）
- 冰 → 龍捲風怪（強力減速）
- 火 → 對水怪有效，對岩漿怪可能抗性

**重要**: 不要在多處複製屬性判定邏輯，所有平衡改動應集中在 ElementSystem。

## 管理器通信模式

### 數據傳遞慣例

管理器間通過字典返回值通信，避免直接耦合：

```python
# MonsterManager 返回波次狀態
monster_update_result = self.monster_manager.update(player, platforms, dt)
if monster_update_result["boss_defeated"]:
    # 在Boss位置生成勝利星星
    if self.monster_manager.boss:
        self.level_manager.star_x = self.monster_manager.boss.x

# WeaponManager 返回碰撞結果
collision_results = self.weapon_manager.update(targets=all_targets)
for collision in collision_results:
    # 處理傷害顯示和分數計算
    self.damage_display.add_damage_number(...)
```

### 資源共享模式

- `LevelManager.get_platforms()`: 提供平台數據給物理系統
- `Player.get_pending_bullet()`: 玩家射擊請求傳遞給武器系統
- `MonsterManager.monsters + boss`: 組合目標列表給武器系統

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

### 關鍵調試模式

- 模組導入錯誤時，必須用 `python3 -m src.main` 執行
- 字體載入失敗會自動降級，檢查 console 輸出確定實際字體
- 攝影機相關問題：所有 draw 方法都需要減去 `camera_x, camera_y` 偏移

### 碰撞檢測架構

專案有多個獨立的碰撞系統：

- `WeaponManager.check_bullet_collisions()`: 玩家子彈對怪物
- `Monster.check_water_bullet_collision()`: 怪物子彈對玩家（如水怪）
- `Player.handle_collisions()`: 玩家對平台物理
- `Monster.handle_collisions()`: 怪物對平台物理

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

### 怪物 AI 與投射物

- 某些怪物有獨立的投射物系統（如 `WaterMonster.water_bullets`）
- 怪物 AI 使用平台邊界檢測避免掉落：`check_platform_boundary()`
- Boss 系統已簡化，Boss 作為強化版怪物在 `MonsterManager` 中管理

### 程式碼風格

- 命名：變數/函式為 snake_case，類別為 PascalCase
- 註解：統一使用繁體中文；所有 public 方法需完整 docstring
- 主程式：不使用 `if __name__ == "__main__":` 慣例，直接呼叫 `main()`

## 常見開發任務

### 新增怪物

1. 在 `entities/monsters.py` 繼承 `Monster` 類別
2. 更新 `config.py` 增加怪物常數
3. 在 `ElementSystem` 定義弱點和抗性關係
4. 把生成邏輯加到 `MonsterManager.spawn_monster()`

### 新增子彈類型

1. 擴充 `entities/weapon.py` 的 `Bullet` 類別
2. 在 `config.py` 設定傷害和顏色參數
3. 在 `ElementSystem` 加入新的剋制關係

### 新增關卡

1. 在 `systems/level_system.py` 新增 `generate_*_level()` 方法
2. 定義平台佈局和環境特色
3. 設定怪物生成模式和難度

### 新增狀態效果

1. 在 `ElementSystem.STATUS_EFFECT_MAP` 定義效果配置
2. 確保目標物件有 `add_status_effect()` 方法
3. 在怪物的 `update()` 方法中處理效果邏輯

### 範例 docstring 格式

```python
def calculate_damage(self, base_damage, attacker_element, target_type):
    """
    計算考慮屬性剋制後的最終傷害\n
    \n
    參數:\n
    base_damage (int): 基礎傷害值，範圍 > 0\n
    attacker_element (str): 攻擊元素類型\n
    target_type (str): 目標怪物類型\n
    \n
    回傳:\n
    int: 經過剋制後的最終傷害（最小為 1）\n
    """
```

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
