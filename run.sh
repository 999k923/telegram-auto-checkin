#!/bin/bash

# 简单的后台运行脚本（通过 systemd 启动）

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

# 创建 systemd 服务文件 (如果不存在)
SERVICE_FILE="/etc/systemd/system/telegram-auto-checkin.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo "创建 systemd 服务文件..."

    cat > $SERVICE_FILE << EOF
[Unit]
Description=Telegram Auto Check-in Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$SCRIPT_DIR/venv/bin"
ExecStart=$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ systemd 服务文件创建成功"
else
    echo "⚠️ 服务文件已经存在，无需创建"
fi

# 重新加载 systemd 配置
echo "重新加载 systemd 配置..."
sudo systemctl daemon-reload

# 启动服务
echo "启动 Telegram Auto Check-in 服务..."
sudo systemctl start telegram-auto-checkin

# 设置服务开机自启
echo "设置服务开机自启..."
sudo systemctl enable telegram-auto-checkin

echo "✅ 服务已启动并设置为开机自启"
