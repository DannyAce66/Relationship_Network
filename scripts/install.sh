#!/usr/bin/env bash
# Relationship Network — One-Click Install
# 关系网络一键安装脚本
#
# Usage / 用法:
#   chmod +x scripts/install.sh
#   ./scripts/install.sh

set -e

echo "============================================"
echo " Relationship Network (RN) — Installer"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    echo "   https://www.python.org/downloads/"
    exit 1
fi

PYTHON=$(command -v python3)
PYTHON_VER=$($PYTHON --version 2>&1)
echo "✅ $PYTHON_VER"
echo ""

# Install the package
echo "📦 Installing RN..."
$PYTHON -m pip install -e . --quiet 2>/dev/null || pip3 install -e . --quiet

if command -v rn &>/dev/null; then
    echo "✅ RN installed successfully"
else
    echo "⚠️  'rn' command not on PATH. You can still use: python3 -m rn.cli"
fi
echo ""

# Create data directory
RN_DIR="$HOME/.rn"
if [ ! -d "$RN_DIR" ]; then
    mkdir -p "$RN_DIR"
    echo "✅ Created $RN_DIR"
else
    echo "✅ $RN_DIR already exists"
fi

# Create empty data file if not exists
if [ ! -f "$RN_DIR/persons.jsonl" ]; then
    touch "$RN_DIR/persons.jsonl"
    echo "✅ Created empty persons.jsonl"
else
    echo "✅ persons.jsonl already exists"
fi
echo ""

# Optional: Add sample data for testing
echo ""
read -p "Add 10 sample contacts for testing? (y/n): " ADD_SAMPLE
if [ "$ADD_SAMPLE" = "y" ] || [ "$ADD_SAMPLE" = "Y" ]; then
    cp data/sample.jsonl "$RN_DIR/persons.jsonl"
    echo "✅ Sample data loaded"
fi
echo ""

# Agent integration hint
echo "============================================"
echo " 🎉 Installation Complete!"
echo "============================================"
echo ""
echo "Quick test:"
echo "  rn --data data/sample.jsonl list"
echo ""
echo "Add your first contact:"
echo "  rn add \"John Smith,investor,NYC,met at conference\""
echo ""
echo "For AI Agent integration (auto-detect names in chat):"
echo "  Load skills/AGENTS.md into your agent's system prompt"
echo "  or copy it to your agent's skills directory."
echo ""
echo "  Hermes:  cp skills/AGENTS.md ~/.hermes/skills/relationship-network/SKILL.md"
echo "  OpenClaw: cp skills/AGENTS.md E:/OpenClaw/skills/relationship-network/SKILL.md"
echo "  Claw Code: Already auto-detected in project root"
echo ""
