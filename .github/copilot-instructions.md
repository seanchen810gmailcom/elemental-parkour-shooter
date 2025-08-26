# AI Coding Agent Instructions for Elemental Parkour Shooter

## 項目概覽

這是一個基於 Pygame 的 2D 跑酷射擊遊戲，結合元素屬性系統和模組化架構。玩家使用跑酷技能在不同主題關卡中對抗具有元素弱點的怪物。

## 核心架構模式

### 1. 嚴格模組化結構

```
src/
├── main.py              # 主遊戲迴圈和狀態管理
├── config.py            # 集中化常數配置
├── core/                # 核心系統（元素、基礎物件）
├── entities/            # 遊戲實體（玩家、武器、怪物）
├── systems/             # 管理器系統（關卡、Boss、怪物管理）
└── utils/               # 工具函數
```

**關鍵原則**: 每個模組都有明確的職責。新功能必須放在正確的目錄中。

### 2. 管理器模式

遊戲使用多個專用管理器來處理複雜系統：

- **`MonsterManager`**: 怪物生成、波次推進、難度調整
- **`WeaponManager`**: 子彈系統、碰撞檢測、近戰攻擊
- **`LevelManager`**: 關卡場景、陷阱、主題切換
- **`BossManager`**: Boss 戰鬥邏輯和多階段機制
- **`DamageDisplayManager`**: 傷害數字和狀態效果顯示

**注意**: 每個管理器都有自己的 `update()` 方法，按特定順序在主迴圈中調用。

### 3. 元素屬性系統核心

```python
# core/element_system.py - 所有屬性邏輯的中央處理
ElementSystem.calculate_damage(base_damage, attacker_element, target_type)
ElementSystem.get_status_effect(attacker_element, target_type)
```

**剋制關係**:

- 水 → 岩漿怪 (2x 傷害)
- 雷 → 水怪 (2x 傷害 + 麻痺)
- 冰 → 龍捲風怪 (強力減速)
- 火 → 水怪有效，對岩漿怪抗性

**重要**: 修改屬性平衡時，只需在 `ElementSystem` 中調整，不要分散在多個文件中。

## 開發工作流程

### 運行遊戲

```bash
# 推薦方式（自動依賴檢查）
./scripts/start_game.sh

# 開發模式
python3 -m src.main

# 直接執行
python3 main.py
```

### 依賴管理

- **核心依賴**: `pygame>=2.5.0`
- **安裝**: `pip3 install -r requirements.txt`
- **字體系統**: 自動降級到系統可用的中文字體

### 程式碼風格要求

**必須遵循**: 參考 `.github/instructions/info.instructions.md`

**關鍵規則**:

1. **變數命名**: `snake_case` (例: `monster_manager`, `bullet_speed`)
2. **類別命名**: `PascalCase` (例: `ElementSystem`, `MonsterManager`)
3. **註解語言**: 所有註解使用**繁體中文**
4. **文檔字串**: 必須包含參數說明、回傳值、使用範例

**註解風格範例**:

```python
def calculate_damage(self, base_damage, attacker_element, target_type):
    """
    計算考慮屬性剋制後的最終傷害\n
    \n
    參數:\n
    base_damage (int): 基礎傷害值，範圍 > 0\n
    attacker_element (str): 攻擊者的元素屬性\n
    target_type (str): 目標的怪物類型\n
    \n
    回傳:\n
    int: 最終傷害值，最小為1\n
    """
    # 檢查弱點攻擊（對特定怪物造成雙倍傷害）
    if attacker_element in self.WEAKNESS_MAP:
        if target_type in self.WEAKNESS_MAP[attacker_element]:
            final_damage = int(base_damage * WEAKNESS_MULTIPLIER)
```

## 重要設計模式

### 1. 狀態機 AI

怪物使用狀態機： `'patrol'` → `'chase'` → `'attack'` → `'stunned'`

```python
# monsters.py - AI 狀態機實現
def update_ai(self, player, platforms):
    if can_attack:
        self.ai_state = "attack"
    elif player_detected:
        self.ai_state = "chase"
    else:
        self.ai_state = "patrol"
```

### 2. 組件化更新循環

主遊戲迴圈按固定順序更新組件，確保數據流一致性：

```python
# main.py - 更新順序很重要
def update(self):
    self.player.update(platforms)
    self.level_manager.update(dt, self.player, bullets)
    self.monster_manager.update(self.player, platforms, dt)
    self.weapon_manager.update(targets=all_targets)
    self.damage_display.update()
```

### 3. 攝影機系統

使用相對座標系統，所有繪製方法接受 `camera_x`, `camera_y` 參數：

```python
def draw(self, screen, camera_x=0, camera_y=0):
    # 所有位置都要減去攝影機偏移
    draw_x = self.x - camera_x
    draw_y = self.y - camera_y
```

## 常見開發任務

### 添加新怪物類型

1. 在 `entities/monsters.py` 中繼承 `Monster` 類別
2. 在 `config.py` 中添加配置常數
3. 在 `core/element_system.py` 中定義弱點關係
4. 更新 `MonsterManager` 的生成邏輯

### 添加新子彈類型

1. 在 `entities/weapon.py` 中擴展 `Bullet` 類別
2. 在 `config.py` 中定義傷害和顏色
3. 在 `ElementSystem` 中添加剋制關係
4. 更新玩家的切換 UI

### 關卡設計

1. 在 `systems/level_system.py` 中添加新的 `generate_*_level()` 方法
2. 定義平台佈局、陷阱位置和主題顏色
3. 更新 `LevelManager.generate_level()` 中的關卡切換邏輯

## 調試和故障排除

### 常見問題

- **模組導入錯誤**: 確保使用 `python3 -m src.main` 運行
- **字體載入失敗**: 系統會自動降級到預設字體，檢查控制台輸出
- **碰撞檢測問題**: 檢查攝影機偏移是否正確應用
- **性能問題**: 檢查怪物數量和子彈清理邏輯

### 日誌和診斷

遊戲在控制台輸出重要事件：

- 字體載入狀態
- 波次推進資訊
- Boss 戰鬥狀態
- 關卡切換通知

## 擴展指南

該項目設計為模組化擴展。添加新功能時：

1. **確定適當的模組**：新功能屬於哪個系統？
2. **遵循現有模式**：參考類似功能的實現方式
3. **更新配置**：在 `config.py` 中添加相關常數
4. **考慮平衡性**：新功能如何影響元素屬性系統？
5. **測試互動**：確保與現有系統正確整合

記住：這個遊戲的核心是元素屬性剋制系統，所有新功能都應該考慮如何與這個系統協調工作。
