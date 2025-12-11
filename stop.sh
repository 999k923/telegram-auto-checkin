#!/bin/bash

# 停止机器人脚本
PID_FILE="bot.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ 未找到 PID 文件，机器人可能未运行"
    exit 1
fi

PID=$(cat "$PID_FILE")

# 停止进程
if ps -p "$PID" > /dev/null 2>&1; then
    echo "停止机器人 (PID: $PID)..."
    kill "$PID"
    rm "$PID_FILE"
    echo "✅ 机器人已停止"
else
    echo "❌ 进程不存在 (PID: $PID)"
    rm "$PID_FILE"
fi

# 禁用开机自启
echo "禁用服务开机自启..."
sudo systemctl disable telegram-auto-checkin
echo "✅ 服务开机自启已禁用"

# 停止服务
echo "停止系统服务..."
sudo systemctl stop telegram-auto-checkin
echo "✅ 服务已停止"
