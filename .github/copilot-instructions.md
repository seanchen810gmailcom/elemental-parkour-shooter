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

# AI Coding Agent Instructions for Elemental Parkour Shooter

## 概要

這份說明提供給自動化程式碼助理（AI coding agent），用來在此 Pygame 專案中實作或變更功能時遵循的架構、風格與流程要點。主要關注模組化結構、元素屬性系統，以及常見開發任務與測試流程。

> 參考：專案的詳細風格與註解規範請見 `.github/instructions/info.instructions.md`（包含註解範例、文檔字串格式與命名規範）。

## 主要架構

專案採模組化設計：

```
src/
├── main.py      # 主遊戲迴圈、狀態管理
├── config.py    # 全域常數
├── core/        # 元素系統、基礎遊戲物件
├── entities/    # 玩家、怪物、武器
└── systems/     # 關卡、怪物管理、Boss
```

每個系統以管理器（Manager）模式實作，常見管理器：`MonsterManager`、`WeaponManager`、`LevelManager`、`BossManager`、`DamageDisplayManager`。每個管理器應提供 `update()` 方法，並在主迴圈以固定順序呼叫。

## 元素屬性系統

所有元素相關邏輯集中於 `src/core/element_system.py`：

- ElementSystem.calculate_damage(base_damage, attacker_element, target)
- ElementSystem.get_status_effect(attacker_element, target)

範例剋制關係（可在 ElementSystem 調整）：

- 水 → 岩漿怪（2x 傷害）
- 雷 → 水怪（2x 傷害 + 麻痺）
- 冰 → 龍捲風怪（強力減速）
- 火 → 對水怪有效，對岩漿怪可能抗性

重要：不要在多處複製屬性判定邏輯，所有平衡改動應集中在 ElementSystem。

## 程式碼風格與測試

- 命名：變數/函式為 snake_case，類別為 PascalCase。
- 註解與文件：使用繁體中文；public 方法需有完整 docstring（參數、回傳、範例）。
- 開發流程：更新後執行 linters/測試與簡單運行測試（例如呼叫 `python3 -m src.main` 的一個小場景）。

舉例 docstring 範本（請遵循 `.github/instructions/info.instructions.md` 的格式）：

```python
def calculate_damage(self, base_damage, attacker_element, target_type):
    """
    計算考慮屬性剋制後的最終傷害

    參數:
    base_damage (int): 基礎傷害
    attacker_element (str): 攻擊元素
    target_type (str): 目標類型

    回傳:
    int: 經過剋制後的最終傷害（最小為 1）
    """
    ...
```

## 常見任務指引

- 新增怪物：在 `entities/monsters.py` 繼承 `Monster`，更新 `config.py`、在 `ElementSystem` 定義弱點，並把生成邏輯加到 `MonsterManager`。
- 新增子彈類型：擴充 `entities/weapon.py` 的 `Bullet`，在 `config.py` 設定參數，並在 ElementSystem 加入剋制關係。
- 關卡：在 `systems/level_system.py` 新增 `generate_*_level()`。

## 調試要點

- 若遇到模組導入錯誤，請用 `python3 -m src.main` 執行模組路徑。
- 字體載入出錯會自動降級，檢查 console 輸出以確定使用的是哪個字體。
- 碰撞或顯示問題常因 camera 偏移或 draw 座標未減攝影機偏移造成。

## 交付與 PR 建議

- 每次變更應包含：簡短的 PR 描述、修改的檔案列表、以及如何在本地重現變更的步驟。
- 若變更涉及平衡（元素數值、怪物數值），請在 PR 中包含測試說明或數值範例。

---

保持簡潔、模組化、並集中處理元素邏輯；如需更詳細的註解格式與範例，參考 `.github/instructions/info.instructions.md`。
