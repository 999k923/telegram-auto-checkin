# Telegram 自动签到脚本
自动在 Telegram 机器人和群组上每天定时签到打卡的 Python 脚本。emby订阅保号方便
---

## ✨ 功能特点

- 🎯 **无限目标**：支持添加无限个签到目标，每个独立配置
- 🔘 **灵活方式**：每个目标可独立选择按钮点击或文本命令
- 🤖 **智能识别**：自动识别群组名称、ID、用户名多种格式
- ⏰ **定时调度**：支持自定义签到时间，精确到分钟
- 🎲 **随机延迟**：模拟人类行为，避免被检测为机器人
- 📝 **完整日志**：自动保存签到历史和详细日志
- 🔐 **安全可靠**：使用官方 Telegram Client API
- 🛠️ **丰富工具**：提供群组查找、按钮测试等辅助工具

## 📋 系统要求

- Ubuntu 18.04+ / Debian 10+ (或其他 Linux 发行版)
- Python 3.8+
- Telegram 账号
- 512MB+ 内存

## 🎯 快速开始

### 方式一：从 GitHub 部署

```bash
# 1. 克隆仓库
git clone https://github.com/999k923/telegram-auto-checkin.git
cd telegram-auto-checkin

# 2. 安装虚拟环境依赖（如果未安装 python3-venv）
sudo apt install python3.12-venv

# 3. 创建虚拟环境
python3 -m venv venv

# 4. 激活虚拟环境（激活后会看到 (venv) 提示）
source venv/bin/activate  # (venv) 提示出现

# 5. 一键安装（自动完成所有配置）
sudo bash install.sh

```

**脚本会自动完成：**
- ✅ 安装 Python 和依赖
- ✅ 创建虚拟环境
- ✅ 引导配置 API 凭证
- ✅ 交互式配置签到目标

### 获取 Telegram API 凭证

1. 访问 https://my.telegram.org
2. 使用手机号登录
3. 点击 "API development tools"
4. 创建应用获取 `API_ID` 和 `API_HASH`

获取如果提示ERROR，+86手机注册账号换香港或者台湾的干净节点。

### 第三步：按提示配置

部署脚本会自动引导你完成所有配置：

#### 🔑 配置 API 凭证

```
请输入 API_ID (数字): 12345678
请输入 API_HASH (32位字符串): abcdef123456...
请输入手机号 (如 +8613800138000): +8613800138000

```

#### 🎯 配置签到目标（交互式）

**第 1 个目标：**
```
1️⃣  显示名称: @okemby_bot
2️⃣  目标标识: @okemby_bot
3️⃣  签到命令: /start  #用于呼出按钮的命令
4️⃣  签到方式: 1 (按钮点击)
5️⃣  按钮文字: 签到

✅ 第 1 个目标已添加!
```

**继续添加：**
```
是否添加第 2 个签到目标? (y/n): y

1️⃣  显示名称: Cloud Cat Group
2️⃣  目标标识: Cloud Cat Group
3️⃣  签到命令: /checkin
4️⃣  签到方式: 2 (文本命令)

✅ 第 2 个目标已添加!

是否添加第 3 个签到目标? (y/n): n
```

**完成配置：**
```
共配置 2 个签到目标

确认保存配置? (y/n): y
✅ 配置已成功保存!
```

### 第四步：首次登录验证

```bash
source venv/bin/activate
python test_login.py
```

按提示输入：
- Telegram 发送的验证码
- 两步验证密码（如果启用）

### 第五步：测试签到

```bash
python manual_checkin.py
```

查看输出，确认所有目标签到成功：

```
═══════════════════════════════════════
开始签到: @okemby_bot
═══════════════════════════════════════
📤 向 @okemby_bot 发送 /start 并点击按钮: 签到
✅ [2025-11-20 10:00:00] @okemby_bot 签到成功!

═══════════════════════════════════════
开始签到: Cloud Cat Group
═══════════════════════════════════════
📤 向 Cloud Cat Group 发送签到命令: /checkin
✅ [2025-11-20 10:00:05] Cloud Cat Group 签到成功!
```

### 第六步：设置自动运行

```bash
chmod +x setup_service.sh
sudo ./setup_service.sh
```
启动服务
```bash
sudo systemctl start telegram-auto-checkin
```

**完成！** 现在可以退出 SSH，脚本会在后台自动运行。

```bash
# 查看服务状态
sudo systemctl status telegram-auto-checkin

# 退出 SSH
exit
```

### 卸载脚本
```bash
sudo ./uninstall.sh
```

## 🛠️ 常用工具

### 📋 查看所有群组和机器人

不确定群组名称或找不到群组？使用这个工具：

```bash
source venv/bin/activate
python list_groups.py
```

**输出示例：群组用“名称”，机器人使用“用户名”。**
```
📱 群组列表
═══════════════════════════════════════
[1] 名称: Cloud Cat Group
    类型: 超级群组
    ID: -1001234567890
    ✅ 配置使用: Cloud Cat Group

🤖 机器人列表
═══════════════════════════════════════
[1] 名称: OKemby Bot
    用户名: @okemby_bot
    ✅ 配置使用: @okemby_bot
```

### ➕ 添加新的签到目标

**方法一：交互式添加（推荐）**

```bash
python add_target.py
```

支持连续添加多个目标，自动保存配置。

**方法二：重新配置所有目标**

```bash
python setup_targets.py
```

从头开始配置所有签到目标。

### 🔘 查看机器人按钮

```bash
python test_buttons.py
```

显示机器人的所有按钮，方便确定配置。

### 👥 测试群组签到

```bash
python test_group.py
```

测试群组的签到方式，查看是否有按钮。

### 🧪 手动测试签到

```bash
python manual_checkin.py
```

手动执行一次所有目标的签到测试。

## 📂 项目结构

```
telegram-auto-checkin/
├── main.py                 # 主程序（定时调度）
├── checkin.py              # 签到逻辑（支持多目标）
├── telegram_client.py      # Telegram 客户端（智能识别）
├── config.py               # 配置管理（多目标支持）
│
├── setup_targets.py        # 配置向导 - 首次部署 ⭐ 核心
├── add_target.py           # 添加目标 - 支持无限添加 ⭐ 核心
├── list_groups.py          # 列出群组 - 查找名称/ID ⭐ 核心
│
├── test_login.py           # 登录测试
├── test_buttons.py         # 按钮查看
├── test_group.py           # 群组测试
├── manual_checkin.py       # 手动签到
│
├── deploy.sh               # 一键部署脚本 ⭐ 自动化
├── setup_service.sh        # 系统服务安装
├── run.sh                  # 后台运行脚本
├── stop.sh                 # 停止脚本
│
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量配置（自动生成）
│
├── README.md               # 项目文档（本文件）
├── QUICKSTART.md           # 5分钟快速开始
├── MULTI_TARGET_GUIDE.md   # 多目标配置详解
├── SETUP_GUIDE.md          # 按钮签到指南
├── UPGRADE.md              # 版本升级指南
└── DEPLOYMENT_SUMMARY.md   # 部署功能总结
```

## 🎮 使用说明

### 🔧 修改配置

#### 修改签到时间

```bash
nano .env

# 修改这两行
CHECKIN_HOUR=10    # 改为10点
CHECKIN_MINUTE=30  # 改为30分

# 重启服务
sudo systemctl restart telegram-auto-checkin
```

#### 添加新的签到目标

```bash
# 进入项目目录
cd ~/telegram-auto-checkin
source venv/bin/activate

# 运行添加工具
python add_target.py

# 按提示添加新目标

# 测试
python manual_checkin.py

# 重启服务
sudo systemctl restart telegram-auto-checkin
```

#### 删除签到目标

```bash
# 编辑配置文件
nano .env

# 在 CHECKIN_TARGETS 中删除对应的目标
# 重启服务
sudo systemctl restart telegram-auto-checkin
```

### 📊 查看日志

```bash
# 查看程序日志
tail -f auto_checkin.log

# 查看签到历史
cat checkin_history.log

# 查看系统日志
sudo journalctl -u telegram-auto-checkin -f

# 查看最近50条日志
sudo journalctl -u telegram-auto-checkin -n 50
```

### 🔄 服务管理

```bash
# 启动服务
sudo systemctl start telegram-auto-checkin

# 停止服务
sudo systemctl stop telegram-auto-checkin

# 重启服务
sudo systemctl restart telegram-auto-checkin

# 查看状态
sudo systemctl status telegram-auto-checkin

# 开机自启
sudo systemctl enable telegram-auto-checkin

# 禁用自启
sudo systemctl disable telegram-auto-checkin
```

## ⚙️ 配置说明

### 环境变量配置

`.env` 文件示例：

```bash
# Telegram API 配置
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
PHONE_NUMBER=+8613800138000

# 签到目标配置（自动生成的 JSON 格式）
CHECKIN_TARGETS=[{"name":"@okemby_bot","target":"@okemby_bot","command":"/start","button_text":"签到"},{"name":"Cloud Cat Group","target":"Cloud Cat Group","command":"/checkin","button_text":""}]

# 签到时间配置
CHECKIN_HOUR=9          # 签到时间（小时）0-23
CHECKIN_MINUTE=0        # 签到时间（分钟）0-59

# 时区配置
TIMEZONE=Asia/Shanghai  # 中国时区

# 随机延迟配置（秒）
RANDOM_DELAY_MIN=0      # 最小延迟
RANDOM_DELAY_MAX=300    # 最大延迟（5分钟）
```

### 签到目标配置详解

每个目标包含以下字段：

```json
{
  "name": "显示名称",           // 在日志中显示的名称
  "target": "目标标识",         // 机器人用户名/群组名称/ID
  "command": "/start",          // 要发送的命令
  "button_text": "签到"         // 按钮文字，留空则使用命令方式
}
```

**目标标识格式：**

| 类型 | 格式 | 示例 |
|------|------|------|
| 机器人 | @username | `@okemby_bot` |
| 群组名称 | 完整名称 | `Cloud Cat Group` |
| 群组ID | 负数ID | `-1001234567890` |

**签到方式：**

| 方式 | button_text | 说明 |
|------|-------------|------|
| 按钮点击 | `"签到"` | 发送命令后点击按钮 |
| 文本命令 | `""` (留空) | 直接发送命令 |

### 配置示例

#### 示例 1：单个机器人（按钮签到）

```bash
CHECKIN_TARGETS=[{"name":"@okemby_bot","target":"@okemby_bot","command":"/start","button_text":"签到"}]
```

#### 示例 2：机器人 + 群组

```bash
CHECKIN_TARGETS=[{"name":"机器人","target":"@okemby_bot","command":"/start","button_text":"签到"},{"name":"群组","target":"Cloud Cat Group","command":"/checkin","button_text":""}]
```

#### 示例 3：多个目标（混合方式）

```bash
CHECKIN_TARGETS=[{"name":"Bot1","target":"@bot1","command":"/start","button_text":"签到"},{"name":"Group1","target":"-1001234567890","command":"/checkin","button_text":""},{"name":"Bot2","target":"@bot2","command":"/daily","button_text":"打卡"}]
```

## 🛡️ 安全注意事项

1. **保护 Session 文件**
   - `telegram_session.session` 文件等同于登录凭证
   - 不要分享给任何人
   - 已自动添加到 `.gitignore`

2. **保护 API 凭证**
   - 不要公开 `API_ID` 和 `API_HASH`
   - 不要将 `.env` 文件提交到 Git

3. **使用专用账号**
   - 建议使用小号进行自动化操作
   - 避免使用主账号

4. **合理设置延迟**
   - 使用随机延迟避免被检测
   - 不要频繁操作

## 🐛 故障排查

### 登录相关

#### ❌ 无法登录

**问题：** API ID/Hash 错误

**解决：**
```bash
# 检查 .env 配置
cat .env | grep API

# 确认凭证来源：https://my.telegram.org
# API_ID 是纯数字，API_HASH 是32位字符串
```

#### ❌ 未收到验证码

**解决：**
1. 检查手机号格式（需要 `+` 和国际区号）
2. 确认网络连接正常
3. 检查 Telegram 是否被屏蔽

### 签到相关

#### ❌ 找不到群组

**问题：** `Cannot find any entity corresponding to "xxx"`

**解决：**
```bash
# 1. 列出所有群组，获取精确名称或 ID
python list_groups.py

# 2. 使用显示的名称或 ID 重新配置
python add_target.py

# 3. 测试
python manual_checkin.py
```

#### ❌ 找不到按钮

**问题：** `未找到包含 'xxx' 的按钮`

**解决：**
```bash
# 查看机器人的所有按钮
python test_buttons.py

# 复制准确的按钮文字到配置
python add_target.py
```

#### ❌ 签到无回复

**解决：**
```bash
# 1. 测试机器人/群组
python test_buttons.py  # 机器人
python test_group.py    # 群组

# 2. 检查配置
cat .env | grep CHECKIN_TARGETS

# 3. 查看详细日志
tail -f auto_checkin.log
```

### 服务相关

#### ❌ 服务启动失败

**解决：**
```bash
# 查看详细错误
sudo journalctl -u telegram-auto-checkin -n 50 --no-pager

# 重新安装服务
sudo ./setup_service.sh

# 检查配置文件
python -c "import config; print('配置正确')"
```

#### ❌ 定时任务不执行

**解决：**
```bash
# 1. 检查服务状态
sudo systemctl status telegram-auto-checkin

# 2. 查看调度器日志
sudo journalctl -u telegram-auto-checkin | grep "下次签到"

# 3. 验证时区设置
cat .env | grep TIMEZONE
```

## 📝 常见问题

### Q: 如何同时在多个机器人/群组签到？

**A:** 使用配置工具添加多个目标：

```bash
python add_target.py
# 或
python setup_targets.py
```

详见 `MULTI_TARGET_GUIDE.md`

### Q: 机器人是按钮签到还是命令签到？

**A:** 运行测试工具查看：

```bash
python test_buttons.py  # 查看机器人按钮
python test_group.py    # 测试群组方式
```

### Q: 群组名称如何填写？

**A:** 运行 `python list_groups.py` 查看所有群组的精确名称和 ID，推荐使用 ID。

### Q: 需要一直开着 Telegram 客户端吗？

**A:** 不需要。脚本使用 Telegram API 独立运行，与客户端无关。

### Q: 会被封号吗？

**A:** 正常使用不会。建议：
- 使用小号
- 设置随机延迟（已内置）
- 不要频繁操作

### Q: 支持 Windows/Mac 吗？

**A:** 主要代码支持跨平台，但部署脚本是为 Linux 设计的，需要修改。

### Q: 如何知道签到是否成功？

**A:** 查看日志：

```bash
# 签到历史
cat checkin_history.log

# 实时日志
tail -f auto_checkin.log

# 系统日志
sudo journalctl -u telegram-auto-checkin -f
```

### Q: 可以修改签到时间吗？

**A:** 可以，编辑 `.env` 后重启服务：

```bash
nano .env
# 修改 CHECKIN_HOUR 和 CHECKIN_MINUTE
sudo systemctl restart telegram-auto-checkin
```

## 🔄 更新升级

### 更新代码

```bash
# 1. 备份配置
cp .env .env.backup
cp telegram_session.session telegram_session.backup

# 2. 停止服务
sudo systemctl stop telegram-auto-checkin

# 3. 更新代码（上传新文件或 git pull）

# 4. 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 5. 恢复配置
cp .env.backup .env

# 6. 重启服务
sudo systemctl start telegram-auto-checkin
```

详见 `UPGRADE.md`


### 如果手机的TGAPP登录的时候要验证码，没有其他设备登录的状态，就可以用这个get_code.py
```bash
cd telegram-auto-checkin
source venv/bin/activate
python get_code.py
```


