#!/bin/bash

# 停止并禁用服务
sudo systemctl stop telegram-auto-checkin
sudo systemctl disable telegram-auto-checkin

# 删除 systemd 服务文件
sudo rm -f /etc/systemd/system/telegram-auto-checkin.service

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 删除虚拟环境
rm -rf venv

# 删除程序目录
cd ..
rm -rf telegram-auto-checkin

# 删除日志文件（如果存在）
rm -f /var/log/telegram-auto-checkin.log

echo "✅ 卸载完成！"
