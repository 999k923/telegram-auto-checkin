# 🚀 快速参考卡片

> 常用命令速查表

---

## 📦 一键部署

### 从 GitHub 部署

```bash
git clone https://github.com/你的用户名/telegram-auto-checkin.git
cd telegram-auto-checkin
sudo bash install.sh
```

### 从压缩包部署

```bash
unzip telegram-auto-checkin.zip
cd telegram-auto-checkin
sudo bash install.sh
```

---

## 🔧 首次配置

```bash
# 进入项目目录
cd ~/telegram-auto-checkin

# 激活虚拟环境
source venv/bin/activate

# 首次登录（输入验证码）
python test_login.py

# 测试签到
python manual_checkin.py
```

---

## ⚙️ 启动服务

### 方式 A：systemd 服务（推荐）

```bash
# 安装服务
sudo ./setup_service.sh

# 启动服务
sudo systemctl start telegram-auto-checkin

# 开机自启
sudo systemctl enable telegram-auto-checkin

# 查看状态
sudo systemctl status telegram-auto-checkin

# 停止服务
sudo systemctl stop telegram-auto-checkin

# 重启服务
sudo systemctl restart telegram-auto-checkin

# 查看日志
sudo journalctl -u telegram-auto-checkin -f
```

### 方式 B：后台脚本

```bash
# 启动
./run.sh

# 停止
./stop.sh

# 查看日志
tail -f auto_checkin.log
```

### 方式 C：前台运行（调试）

```bash
source venv/bin/activate
python main.py
```

---

## 🛠️ 管理工具

```bash
# 进入项目目录并激活环境
cd ~/telegram-auto-checkin
source venv/bin/activate

# 添加新签到目标
python add_target.py

# 列出所有群组/对话
python list_groups.py

# 测试登录状态
python test_login.py

# 手动执行签到
python manual_checkin.py

# 测试群组消息
python test_group.py

# 测试按钮功能
python test_buttons.py
```

---

## 📝 配置文件

### 编辑配置

```bash
# 编辑环境变量
nano .env

# 重要配置项：
# API_ID=12345678
# API_HASH=abcd...
# PHONE_NUMBER=+8613800138000
# CHECKIN_HOUR=9
# CHECKIN_MINUTE=0
# TIMEZONE=Asia/Shanghai
# CHECKIN_TARGETS=[...]
```

### 重新配置签到目标

```bash
source venv/bin/activate
python setup_targets.py
```

---

## 📊 查看日志

```bash
# 查看最新日志
tail -50 auto_checkin.log

# 实时监控日志
tail -f auto_checkin.log

# 查看系统服务日志
sudo journalctl -u telegram-auto-checkin -n 50

# 实时监控服务日志
sudo journalctl -u telegram-auto-checkin -f
```

---

## 🔄 更新代码

### 从 GitHub 更新

```bash
cd ~/telegram-auto-checkin

# 停止服务
sudo systemctl stop telegram-auto-checkin

# 拉取最新代码
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start telegram-auto-checkin
```

### 手动更新

```bash
# 停止服务
sudo systemctl stop telegram-auto-checkin

# 备份配置
cp .env .env.backup
cp telegram_session.session telegram_session.session.backup 2>/dev/null || true

# 上传新文件覆盖

# 恢复配置
cp .env.backup .env
cp telegram_session.session.backup telegram_session.session 2>/dev/null || true

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start telegram-auto-checkin
```

---

## 🐛 故障排查

### 检查服务状态

```bash
# 查看服务状态
sudo systemctl status telegram-auto-checkin

# 查看详细日志
sudo journalctl -u telegram-auto-checkin -n 100 --no-pager

# 查看应用日志
cat auto_checkin.log
```

### 重置登录会话

```bash
# 删除会话文件
rm telegram_session.session*

# 重新登录
source venv/bin/activate
python test_login.py
```

### 测试签到功能

```bash
source venv/bin/activate

# 测试登录
python test_login.py

# 列出群组
python list_groups.py

# 手动签到
python manual_checkin.py
```

---

## 🗑️ 完全卸载

```bash
# 停止并禁用服务
sudo systemctl stop telegram-auto-checkin
sudo systemctl disable telegram-auto-checkin

# 删除服务文件
sudo rm /etc/systemd/system/telegram-auto-checkin.service
sudo systemctl daemon-reload

# 删除项目目录
rm -rf ~/telegram-auto-checkin

# 清理用户数据（可选）
rm -rf ~/.telegram-auto-checkin
```

---

## 📞 获取帮助

- 📖 完整文档：`cat README.md`
- 🎯 安装教程：`cat INSTALL.md`
- 📚 GitHub 教程：`cat GITHUB_GUIDE.md`
- ✅ 部署检查：`cat CHECKLIST.md`
- ⚡ 快速开始：`cat QUICKSTART.md`

---

## 💡 常用场景

### 场景 1：添加新的签到目标

```bash
cd ~/telegram-auto-checkin
source venv/bin/activate
python add_target.py
sudo systemctl restart telegram-auto-checkin
```

### 场景 2：更改签到时间

```bash
nano .env
# 修改 CHECKIN_HOUR 和 CHECKIN_MINUTE
sudo systemctl restart telegram-auto-checkin
```

### 场景 3：查看今天是否签到成功

```bash
tail -100 auto_checkin.log | grep "$(date +%Y-%m-%d)"
```

### 场景 4：手动触发一次签到

```bash
cd ~/telegram-auto-checkin
source venv/bin/activate
python manual_checkin.py
```

### 场景 5：服务器重启后检查

```bash
# 检查服务是否自动启动
sudo systemctl status telegram-auto-checkin

# 如果没启动，手动启动
sudo systemctl start telegram-auto-checkin
```

---

**祝使用愉快！** 🎉
