# 跑酷射擊大冒險 - Elemental Parkour Shooter# 跑酷射擊大冒險 (Elemental Parkour Shooter)

## 專案說明一個結合跑酷動作與元素射擊的 Python 遊戲，使用 pygame 開發。

這是一個結合跑酷動作和射擊元素的 2D 遊戲，使用 Python 和 Pygame 開發。## 🎮 遊戲特色

# 跑酷射擊大冒險 — Elemental Parkour Shooter

這是一個使用 Python 和 Pygame 開發的 2D 跑酷射擊遊戲，結合流暢的跑酷動作與元素屬性的戰鬥系統。

## 專案重點

- 流暢的跑酷動作（雙跳、牆面互動）
- 即時射擊系統：四種元素子彈（水、冰、雷、火）
- 元素剋制系統：根據敵人類型產生額外效果
- 模組化程式碼結構，易於擴充與維護

## 目前功能（概要）

- 玩家移動與跳躍
- 子彈類型切換（鍵盤 1-4）
- 多種怪物類型（岩漿怪、水怪、龍捲風怪）
- 怪物 AI 與波次管理
- 傷害數字顯示（Damage Display）

## 系統需求

- Python 3.8+
- pygame >= 2.5.0

## 安裝

建議建立虛擬環境並安裝相依套件：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 運行遊戲

推薦使用專案提供的腳本或模組方式啟動：

```bash
# 使用啟動腳本 (會做一些預檢查)
./scripts/start_game.sh

# 或以模組方式執行
python3 -m src.main

# 或直接執行 (開發或快速測試)
python3 main.py
```

## 基本操作

- 移動：A / D 或 左 / 右
- 跳躍：W / 空白 / 上
- 子彈切換：1（水） 2（冰） 3（雷） 4（火）
- 射擊：滑鼠左鍵
- 近戰：滑鼠右鍵
- 暫停/繼續：空白鍵
- 退出：ESC

## 檔案結構 (重點)

```
src/
├── main.py            # 主遊戲迴圈與狀態管理
├── config.py          # 全域常數與參數
├── core/              # 核心系統 (元素、基礎物件)
├── entities/          # 玩家、怪物、武器等實體
└── systems/           # 關卡、怪物管理、Boss 等管理器
```

## 元素剋制（簡要）

- 水 → 對岩漿怪造成額外傷害
- 雷 → 對水怪造成額外傷害並可能麻痺
- 冰 → 對某些敵人造成減速效果
- 火 → 對水怪有效，但對岩漿怪可能減傷

元素平衡的定義集中在 `src/core/element_system.py`。

## 開發者注意事項

- 遵循專案的程式碼風格：變數使用 snake_case，類別使用 PascalCase，且所有註解與文檔字串使用繁體中文。
- 若新增或調整屬性剋制，請修改 `ElementSystem`，不要散佈多處邏輯。

## 貢獻

歡迎提交 PR 與 issue。請先閱讀專案中的開發說明與風格指南。

---

最後更新：2025-08-26
