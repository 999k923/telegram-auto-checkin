# 📚 GitHub 上传和部署完整教程

> 从零开始，手把手教你上传到 GitHub 并实现一键部署

---

## 📋 目录

1. [上传到 GitHub](#1-上传到-github)
2. [从 GitHub 部署](#2-从-github-部署)
3. [更新代码](#3-更新代码)

---

## 1. 上传到 GitHub

### 准备工作

#### A. 注册 GitHub 账号

1. 打开 https://github.com
2. 点击右上角 **Sign up**（注册）
3. 填写邮箱、密码、用户名
4. 验证邮箱

#### B. 安装 Git（本地电脑）

**Windows：**
1. 下载：https://git-scm.com/download/win
2. 双击安装，一路 Next
3. 打开命令行，输入 `git --version` 检查安装

**Mac：**
```bash
# 使用 Homebrew
brew install git
```

**Linux：**
```bash
sudo apt install git -y
```

### 步骤 1：创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角 **+** → **New repository**
3. 填写信息：
   - **Repository name**（仓库名）：`telegram-auto-checkin`
   - **Description**（描述）：`Telegram 自动签到机器人`
   - **Public**（公开）或 **Private**（私有）：建议选 **Private**（私有）
   - ❌ 不要勾选 "Initialize this repository with a README"
4. 点击 **Create repository**

### 步骤 2：配置 Git（首次使用）

在本地电脑打开终端（命令行），输入：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

### 步骤 3：上传项目到 GitHub

**打开终端，进入项目目录：**

```bash
# Windows (PowerShell)
cd C:\Users\Administrator\CodeBuddy\20251119

# Mac/Linux
cd ~/CodeBuddy/20251119
```

**初始化 Git 仓库并上传：**

```bash
# 1. 初始化 Git 仓库
git init

# 2. 添加所有文件
git add .

# 3. 提交更改
git commit -m "初始提交：Telegram 自动签到机器人"

# 4. 添加远程仓库（替换成你的仓库地址）
git remote add origin https://github.com/你的用户名/telegram-auto-checkin.git

# 5. 推送到 GitHub
git push -u origin master
```

> 💡 替换 `你的用户名` 为你的 GitHub 用户名

**如果推送时要求登录：**

- 输入 GitHub 用户名
- 密码输入 **Personal Access Token**（不是账号密码）

**创建 Personal Access Token：**

1. GitHub 右上角头像 → **Settings**
2. 左侧菜单最下方 → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token** → **Generate new token (classic)**
5. 勾选 `repo` 权限
6. 点击 **Generate token**
7. 复制生成的 token（只显示一次，记得保存！）

### 步骤 4：验证上传成功

1. 打开浏览器访问你的仓库：
   ```
   https://github.com/你的用户名/telegram-auto-checkin
   ```

2. 应该能看到所有项目文件

---

## 2. 从 GitHub 部署

### 方式 A：一键部署（推荐）

**连接到服务器后，运行：**

```bash
# 克隆仓库
git clone https://github.com/你的用户名/telegram-auto-checkin.git

# 进入目录
cd telegram-auto-checkin

# 赋予执行权限
chmod +x install.sh

# 运行一键安装脚本
sudo bash install.sh
```

**如果是私有仓库，克隆时需要登录：**

```bash
# 使用 Personal Access Token
git clone https://你的用户名:你的Token@github.com/你的用户名/telegram-auto-checkin.git
```

**脚本会自动：**

1. ✅ 检查系统环境
2. ✅ 安装 Python3、pip、git 等依赖
3. ✅ 创建虚拟环境
4. ✅ 安装 Python 包
5. ✅ 引导配置 API 凭证
6. ✅ 引导配置签到目标

**配置完成后，按提示操作：**

```bash
# 1. 首次登录
source venv/bin/activate
python test_login.py

# 2. 测试签到
python manual_checkin.py

# 3. 启动服务
sudo ./setup_service.sh
sudo systemctl start telegram-auto-checkin
```

### 方式 B：手动部署

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/telegram-auto-checkin.git
cd telegram-auto-checkin

# 2. 安装系统依赖
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 4. 安装 Python 依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp .env.example .env
nano .env
# 编辑 .env 文件，填入你的 API_ID, API_HASH, PHONE_NUMBER

# 6. 配置签到目标
python setup_targets.py

# 7. 首次登录
python test_login.py

# 8. 测试签到
python manual_checkin.py

# 9. 设置自动运行
chmod +x setup_service.sh run.sh stop.sh
sudo ./setup_service.sh
sudo systemctl start telegram-auto-checkin
```

---

## 3. 更新代码

### 本地修改后更新到 GitHub

```bash
# 进入项目目录
cd ~/CodeBuddy/20251119

# 查看修改状态
git status

# 添加修改的文件
git add .

# 提交更改
git commit -m "描述你的修改"

# 推送到 GitHub
git push
```

### 服务器拉取最新代码

```bash
# 进入项目目录
cd ~/telegram-auto-checkin

# 停止服务
sudo systemctl stop telegram-auto-checkin

# 拉取最新代码
git pull

# 更新依赖（如果有新增）
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start telegram-auto-checkin
```

---

## 📦 完整文件清单

上传到 GitHub 的文件应该包括：

```
telegram-auto-checkin/
├── main.py                    # 主程序
├── checkin.py                 # 签到逻辑
├── telegram_client.py         # Telegram 客户端
├── config.py                  # 配置管理
├── requirements.txt           # Python 依赖
├── install.sh                 # 一键安装脚本 ⭐
├── deploy.sh                  # 部署脚本
├── run.sh                     # 后台运行脚本
├── stop.sh                    # 停止脚本
├── setup_service.sh           # 服务安装脚本
├── setup_targets.py           # 签到目标配置向导
├── add_target.py              # 添加签到目标工具
├── list_groups.py             # 列出所有群组工具
├── test_login.py              # 登录测试工具
├── test_group.py              # 群组测试工具
├── test_buttons.py            # 按钮测试工具
├── manual_checkin.py          # 手动签到工具
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略文件
├── README.md                  # 项目说明
├── INSTALL.md                 # 安装教程 ⭐
├── GITHUB_GUIDE.md            # GitHub 教程（本文件）⭐
├── QUICKSTART.md              # 快速开始
├── CHECKLIST.md               # 部署检查清单
├── SETUP_GUIDE.md             # 设置指南
├── DEPLOYMENT_SUMMARY.md      # 部署摘要
├── MULTI_TARGET_GUIDE.md      # 多目标指南
└── UPGRADE.md                 # 升级指南
```

**⚠️ 不要上传这些文件：**

- ❌ `.env`（包含敏感信息）
- ❌ `*.session`（Telegram 登录凭证）
- ❌ `*.log`（日志文件）
- ❌ `venv/`（虚拟环境）
- ❌ `__pycache__/`（Python 缓存）

这些文件已在 `.gitignore` 中排除。

---

## 🎯 一键部署命令总结

### 全新部署（从 GitHub）

```bash
# 一条命令完成所有操作
git clone https://github.com/你的用户名/telegram-auto-checkin.git && \
cd telegram-auto-checkin && \
chmod +x install.sh && \
sudo bash install.sh
```

### 快速测试

```bash
cd ~/telegram-auto-checkin
source venv/bin/activate
python test_login.py && python manual_checkin.py
```

### 启动服务

```bash
cd ~/telegram-auto-checkin
sudo ./setup_service.sh
sudo systemctl start telegram-auto-checkin
sudo systemctl enable telegram-auto-checkin
```

---

## 🐛 常见问题

### Q: git clone 提示权限错误？

**A:** 如果是私有仓库，需要使用 token：

```bash
git clone https://你的用户名:ghp_xxxxx@github.com/你的用户名/telegram-auto-checkin.git
```

### Q: 提示 Permission denied (publickey)？

**A:** 需要配置 SSH 密钥或使用 HTTPS + Token。

**使用 HTTPS（简单）：**
```bash
git remote set-url origin https://github.com/你的用户名/telegram-auto-checkin.git
```

### Q: 如何删除 GitHub 上的仓库？

**A:**
1. 进入仓库页面
2. 点击 **Settings**（设置）
3. 滚动到最下方，点击 **Delete this repository**
4. 输入仓库名确认删除

### Q: 多台服务器如何部署？

**A:** 每台服务器都执行相同的部署命令：

```bash
git clone https://github.com/你的用户名/telegram-auto-checkin.git
cd telegram-auto-checkin
sudo bash install.sh
```

每台服务器都需要独立配置和登录。

---

## 🎉 完成！

现在你已经学会：

- ✅ 上传项目到 GitHub
- ✅ 从 GitHub 一键部署
- ✅ 更新和维护代码

任何问题，查看 [INSTALL.md](INSTALL.md) 或 [README.md](README.md)！
