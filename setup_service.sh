#!/bin/bash

# 系统服务安装脚本

set -e

echo "=================================="
echo "安装 Telegram 自动签到系统服务"
echo "=================================="
echo ""

# 获取当前目录和用户
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

# 检查是否有 sudo 权限
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 sudo 运行此脚本"
    echo "sudo ./setup_service.sh"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "$CURRENT_DIR/venv" ]; then
    echo "❌ 未找到虚拟环境，请先运行部署脚本"
    echo "   ./deploy.sh"
    exit 1
fi

# 检查 session 文件
if [ ! -f "$CURRENT_DIR/telegram_session.session" ]; then
    echo "⚠️  警告：未找到 session 文件"
    echo "   请先运行登录测试："
    echo "   python test_login.py"
    echo ""
    read -p "是否继续安装服务? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 创建 systemd 服务文件
SERVICE_FILE="/etc/systemd/system/telegram-auto-checkin.service"

echo "创建服务文件: $SERVICE_FILE"

cat > $SERVICE_FILE << EOF
[Unit]
Description=Telegram Auto Check-in Service
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ 服务文件创建成功"

# 重新加载 systemd
echo ""
echo "重新加载 systemd..."
systemctl daemon-reload

# 启用服务
echo "启用服务（开机自启）..."
systemctl enable telegram-auto-checkin

echo ""
echo "=================================="
echo "✅ 服务安装完成！"
echo "=================================="
echo ""
echo "服务管理命令："
echo ""
echo "启动服务:"
echo "  sudo systemctl start telegram-auto-checkin"
echo ""
echo "停止服务:"
echo "  sudo systemctl stop telegram-auto-checkin"
echo ""
echo "重启服务:"
echo "  sudo systemctl restart telegram-auto-checkin"
echo ""
echo "查看状态:"
echo "  sudo systemctl status telegram-auto-checkin"
echo ""
echo "查看日志:"
echo "  sudo journalctl -u telegram-auto-checkin -f"
echo ""
echo "=================================="
echo ""

read -p "是否现在启动服务? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl start telegram-auto-checkin
    sleep 2
    systemctl status telegram-auto-checkin
fi
