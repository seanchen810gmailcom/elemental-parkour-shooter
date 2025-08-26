#!/bin/bash

# 跑酷射擊大冒險 - 啟動腳本

echo "🎮 正在啟動跑酷射擊大冒險..."
echo "📝 遊戲指南請查看 docs/GAME_GUIDE.md"
echo ""

# 檢查 Python 安裝
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 已找到"
else
    echo "❌ 未找到 Python 3，請先安裝 Python"
    exit 1
fi

# 檢查 pygame 安裝
python3 -c "import pygame" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Pygame 已安裝"
else
    echo "📦 正在安裝 Pygame..."
    pip3 install pygame
fi

echo ""
echo "🚀 正在啟動遊戲..."
echo "💡 提示：按 ESC 可以退出遊戲"
echo ""

# 切換到專案根目錄並啟動遊戲
cd "$(dirname "$0")/.."
python3 -m src.main

echo ""
echo "👋 感謝遊玩！"