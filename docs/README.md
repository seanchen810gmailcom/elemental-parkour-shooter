# 跑酷射擊大冒險 (Elemental Parkour Shooter)

一個結合跑酷動作與元素射擊的 Python 遊戲，使用 pygame 開發。

## 🎮 遊戲特色

### 核心玩法

- **跑酷 + 射擊**：邊進行跑酷動作（跳躍、爬牆、雙跳）邊對抗怪物
- **元素屬性系統**：四種子彈類型，每種都有獨特的剋制關係
- **多樣化怪物**：三種不同類型的怪物，各有特殊攻擊模式
- **波次挑戰**：隨著遊戲進行，敵人變得更強更多

### 玩家能力

- **移動系統**：WASD 或方向鍵控制移動
- **跑酷技能**：
  - 跳躍和二段跳
  - 爬牆和滑牆
  - 牆面跳躍
- **戰鬥系統**：
  - 遠距離射擊（滑鼠左鍵）
  - 近距離近戰攻擊（滑鼠右鍵）

## 🔥 元素屬性系統

### 子彈類型

1. **水彈（1 鍵）**：對岩漿怪造成雙倍傷害
2. **冰彈（2 鍵）**：造成減速效果，對龍捲風怪特別有效
3. **雷彈（3 鍵）**：對水怪造成雙倍傷害和麻痺效果
4. **火彈（4 鍵）**：高傷害，但對岩漿怪有抗性

### 屬性剋制關係

- 水 → 剋制岩漿怪
- 雷 → 剋制水怪
- 冰 → 對所有敵人造成減速
- 火 → 對水怪有效，對岩漿怪抗性

## 👾 怪物類型

### 1. 岩漿怪（紅色）

- **特點**：防禦力高，血量多
- **攻擊**：近戰 + 熔岩球遠程攻擊
- **弱點**：水屬性攻擊
- **抗性**：火屬性攻擊

### 2. 水怪（藍色）

- **特點**：移動速度快，靈活
- **攻擊**：近戰 + 水彈散射 + 衝刺
- **弱點**：雷屬性和火屬性攻擊
- **特殊**：能發射多發水彈進行範圍攻擊

### 3. 龍捲風怪（灰色）

- **特點**：速度極快，血量較低
- **攻擊**：近戰 + 旋風推開 + 瞬移
- **弱點**：冰屬性攻擊（強力減速）
- **特殊**：能瞬移到玩家附近

## 🎯 遊戲操作

### 基本控制

- **移動**：A/D 鍵或左右方向鍵
- **跳躍**：W 鍵或空白鍵或上方向鍵
- **射擊**：滑鼠左鍵
- **近戰**：滑鼠右鍵

### 子彈切換

- **1 鍵**：水彈
- **2 鍵**：冰彈
- **3 鍵**：雷彈
- **4 鍵**：火彈

### 系統控制

- **ESC**：離開遊戲

## 🏆 遊戲目標

- 在不斷增強的怪物波次中生存
- 善用屬性剋制系統對抗不同類型的敵人
- 獲得高分並挑戰更高的波次
- 掌握跑酷技巧在戰鬥中保持優勢

## 📊 計分系統

- **子彈擊中**：10 分
- **近戰擊中**：20 分
- **擊殺怪物**：50 分
- **完成波次**：200 分

## 🛠️ 技術實作

### 檔案結構

```
├── main.py              # 主遊戲檔案
├── config.py            # 遊戲設定和常數
├── player.py            # 玩家角色系統
├── weapon.py            # 武器和子彈系統
├── monsters.py          # 怪物類別定義
├── monster_manager.py   # 怪物管理器
├── game_objects.py      # 基礎遊戲物件
├── element_system.py    # 屬性剋制系統
├── damage_display.py    # 傷害數字顯示
└── README.md           # 說明文件
```

### 系統架構

- **物件導向設計**：清晰的類別繼承結構
- **模組化開發**：各系統獨立且易於維護
- **狀態管理**：完整的遊戲狀態和 AI 狀態機
- **效果系統**：狀態效果和屬性剋制計算

## 🚀 運行需求

### 系統需求

- Python 3.7+
- pygame 2.0+

### 安裝步驟

1. 確保已安裝 Python
2. 安裝 pygame：`pip install pygame`
3. 運行遊戲：`python main.py`

## 🎨 視覺特效

- **即時傷害數字**：顯示造成的傷害和效果類型
- **屬性剋制指示**：不同顏色表示弱點/抗性攻擊
- **狀態效果視覺**：怪物受到狀態效果時的顏色變化
- **動態 UI**：即時顯示遊戲狀態和統計資訊

## 🔄 未來擴展

遊戲採用模組化設計，未來可以輕鬆加入：

- Boss 戰系統
- 不同場景和環境
- 更多武器類型
- 道具和升級系統
- 多人遊戲模式

---

享受這個結合策略思考與反應速度的跑酷射擊冒險吧！記住善用屬性剋制，這是獲勝的關鍵！

## 👾 Monster Types

### 1. 🌋 Lava Monster

- **Strengths**: High defense, shoots molten lava balls creating fire zones
- **Weakness**: Vulnerable to water-based attacks
- **Behavior**: Slow but tanky, creates area denial with lava pools

### 2. 🌊 Water Monster

- **Strengths**: High mobility, rapid swimming, wide-range water projectiles
- **Weakness**: Takes heavy damage from electric and fire attacks
- **Behavior**: Fast and agile, uses hit-and-run tactics

### 3. 🌪️ Tornado Monster

- **Strengths**: Extreme speed, can pull players and cause displacement
- **Weakness**: Low health, disperses quickly when hit
- **Behavior**: High damage but fragile, creates chaos with wind attacks

## 🔫 Weapon System

Players wield a single adaptive firearm with **dual combat modes**:

### Ranged Mode

- Fires elemental bullets with different properties
- Effective for medium to long-range combat
- Bullet types can be switched based on enemy weaknesses

### Melee Mode

- Close-quarters combat using the gun as a weapon
- Knockback effect to push away enemies
- Quick escape option when overwhelmed

## 💥 Elemental Ammunition System

### Bullet Types & Effects

| Bullet Type         | Icon | Effective Against | Special Properties                |
| ------------------- | ---- | ----------------- | --------------------------------- |
| **Water Bullets**   | 💧   | Lava Monsters     | High damage to fire enemies       |
| **Ice Bullets**     | ❄️   | Tornado Monsters  | Slowing effect                    |
| **Thunder Bullets** | ⚡   | Water Monsters    | Paralysis effect                  |
| **Fire Bullets**    | 🔥   | Water Monsters    | Ineffective against Lava Monsters |

### Ammunition Acquisition

- Collect power-ups scattered throughout levels
- Upgrade stations at checkpoints
- Rare drops from defeated monsters
- Strategic resource management required

## 👑 Boss Design

### Elemental Fusion Bosses

#### 🌋🌪️ Molten Tornado Beast

- **Abilities**: Spinning fire attacks, lava tornadoes
- **Strategy**: Requires alternating ice and water bullets
- **Phases**: Multiple attack patterns as health decreases

#### 🌊⚡ Tsunami Leviathan

- **Abilities**: Massive water waves, electric storm attacks
- **Strategy**: Use fire bullets during water phase, earth attacks during electric phase
- **Environment**: Dynamic arena with changing water levels

### Boss Battle Mechanics

- Multi-phase encounters
- Requires mastery of all bullet types
- Environmental hazards and interactive elements
- Adaptive difficulty based on player performance

## 🎮 Level Design & Environments

### 1. 🌋 Volcanic Caverns

- **Hazards**: Lava pits, falling rocks, steam geysers
- **Enemies**: Primarily Lava Monsters
- **Mechanics**: Heat-based platforming challenges

### 2. 🌊 Underwater Tunnels

- **Hazards**: Drowning zones, water currents, pressure chambers
- **Enemies**: Water Monsters and hybrid creatures
- **Mechanics**: Oxygen management, underwater physics

### 3. 🌪️ Hurricane Canyon

- **Hazards**: Wind gusts, floating debris, unstable platforms
- **Enemies**: Tornado Monsters, flying creatures
- **Mechanics**: Wind-affected jumping, aerial combat

## 🎯 Key Features

1. **🏃 Dynamic Parkour System**

   - Fluid movement mechanics
   - Wall running, double jumping, sliding
   - Environmental traversal challenges

2. **⚔️ Strategic Combat**

   - Rock-paper-scissors elemental system
   - Real-time bullet switching
   - Risk/reward weapon positioning

3. **🎨 Adaptive Weapon Design**

   - Single weapon, multiple functions
   - Seamless mode switching
   - Upgradeable components

4. **🌍 Diverse Environments**

   - Multiple themed levels
   - Unique environmental challenges
   - Interactive destructible elements

5. **�� Immersive Experience**
   - Dynamic soundtrack responding to action
   - Particle effects and visual feedback
   - Responsive UI and controls

## 🚀 Development Roadmap

### Phase 1: Core Mechanics

- [ ] Basic parkour movement system
- [ ] Weapon switching mechanics
- [ ] Elementary enemy AI

### Phase 2: Combat System

- [ ] Elemental damage system
- [ ] Monster behavior patterns
- [ ] Ammunition management

### Phase 3: Level Design

- [ ] Environment creation tools
- [ ] Hazard implementation
- [ ] Checkpoint system

### Phase 4: Boss Battles

- [ ] Boss AI development
- [ ] Multi-phase encounter design
- [ ] Cinematic sequences

### Phase 5: Polish & Optimization

- [ ] Performance optimization
- [ ] Audio implementation
- [ ] UI/UX refinement

## 🛠️ Technical Requirements

### Minimum System Requirements

- **OS**: Windows 10 / macOS 10.14 / Ubuntu 18.04
- **Processor**: Intel i5-6600K / AMD Ryzen 5 2600
- **Memory**: 8 GB RAM
- **Graphics**: GTX 1060 / RX 580
- **Storage**: 5 GB available space

### Recommended System Requirements

- **OS**: Windows 11 / macOS 12.0 / Ubuntu 20.04
- **Processor**: Intel i7-9700K / AMD Ryzen 7 3700X
- **Memory**: 16 GB RAM
- **Graphics**: RTX 3060 / RX 6600 XT
- **Storage**: 10 GB available space (SSD recommended)

## 🤝 Contributing

We welcome contributions from the community! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

### Areas for Contribution

- Level design and environmental art
- Monster behavior scripting
- UI/UX improvements
- Performance optimization
- Bug fixes and testing

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Project Lead**: [Your Name]
- **Email**: [your.email@example.com]
- **Discord**: [Discord Server Link]
- **Twitter**: [@YourTwitterHandle]

---

⭐ **Star this repository if you're excited about Elemental Parkour Shooter!** ⭐

_Last updated: August 26, 2025_
