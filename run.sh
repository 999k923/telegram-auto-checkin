#!/bin/bash

# 简单的后台运行脚本（不使用 systemd）

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

# 激活虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: ./deploy.sh"
    exit 1
fi

source venv/bin/activate

# 检查是否已在运行
PID_FILE="bot.pid"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  机器人已在运行 (PID: $OLD_PID)"
        echo ""
        read -p "是否停止并重启? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill "$OLD_PID"
            sleep 2
        else
            exit 0
        fi
    fi
fi

# 后台运行
echo "启动 Telegram 签到机器人..."
nohup python main.py > output.log 2>&1 &
NEW_PID=$!

# 保存 PID
echo $NEW_PID > "$PID_FILE"

echo "✅ 机器人已启动 (PID: $NEW_PID)"
echo ""
echo "查看日志:"
echo "  tail -f bot.log"
echo "  tail -f output.log"
echo ""
echo "停止机器人:"
echo "  kill $NEW_PID"
echo "  或运行: ./stop.sh"
