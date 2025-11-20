# 按钮签到设置指南

由于 `@okemby_bot` 使用按钮而不是文本命令进行签到，按照以下步骤配置：

## 🔍 第一步：查看机器人的按钮

运行测试脚本查看所有按钮：

```bash
source venv/bin/activate
python test_buttons.py
```

这个脚本会：
1. 向机器人发送 `/start` 命令
2. 显示所有按钮的文字
3. 让你测试点击某个按钮

## ⚙️ 第二步：配置 .env 文件

根据测试结果，编辑 `.env` 文件：

```bash
nano .env
```

### 配置示例

```bash
# Telegram API 配置
API_ID=12345678
API_HASH=你的api_hash
PHONE_NUMBER=+8613800138000

# 机器人配置
BOT_USERNAME=@okemby_bot

# 签到配置
CHECKIN_COMMAND=/start              # 发送此命令会显示按钮
CHECKIN_BUTTON_TEXT=签到             # 按钮上的文字

# 时间配置
CHECKIN_HOUR=9
CHECKIN_MINUTE=0
TIMEZONE=Asia/Shanghai
```

### 常见按钮文字

根据不同机器人，按钮可能是：
- `签到`
- `每日签到`
- `打卡`
- `Check in`
- `Daily Check-in`
- `✅ 签到`
- `📅 签到`

**注意**：`CHECKIN_BUTTON_TEXT` 只需要包含按钮文字的一部分即可，例如：
- 如果按钮是 `✅ 签到`，填 `签到` 即可
- 如果按钮是 `Daily Check-in`，填 `Check` 即可

## 🎯 第三步：测试签到

```bash
source venv/bin/activate
python manual_checkin.py
```

查看日志，应该能看到：
```
找到按钮: 签到
🎯 找到目标按钮: 签到
✅ 已点击按钮: 签到
📨 点击后收到回复: ...
```

## 📝 完整配置示例

### 示例 1：简单签到按钮

如果机器人显示的是：
```
欢迎使用机器人！
[签到] [帮助]
```

配置：
```bash
CHECKIN_COMMAND=/start
CHECKIN_BUTTON_TEXT=签到
```

### 示例 2：带表情的签到按钮

如果机器人显示的是：
```
每日任务
[📅 每日签到] [🎁 领取奖励]
```

配置：
```bash
CHECKIN_COMMAND=/start
CHECKIN_BUTTON_TEXT=签到
# 或
CHECKIN_BUTTON_TEXT=每日签到
```

### 示例 3：英文签到按钮

如果机器人显示的是：
```
Main Menu
[Daily Check-in] [My Stats]
```

配置：
```bash
CHECKIN_COMMAND=/start
CHECKIN_BUTTON_TEXT=Check-in
```

## 🐛 故障排查

### 问题：找不到按钮

**解决方法：**
1. 运行 `python test_buttons.py` 查看实际的按钮文字
2. 复制准确的按钮文字到 `CHECKIN_BUTTON_TEXT`
3. 确认发送的命令是否正确（可能是 `/menu` 而不是 `/start`）

### 问题：点击按钮无反应

**解决方法：**
1. 手动在 Telegram 中测试点击按钮是否有效
2. 检查机器人是否需要先进行其他操作（如绑定账号）
3. 查看日志文件 `auto_checkin.log` 获取详细错误信息

### 问题：显示"未找到包含 'xxx' 的按钮"

**解决方法：**
1. 按钮文字可能不完全匹配
2. 运行 `test_buttons.py` 查看准确的按钮文字
3. 修改 `CHECKIN_BUTTON_TEXT` 为实际的按钮文字

## ✅ 验证配置

配置完成后，按顺序执行：

```bash
# 1. 查看按钮
python test_buttons.py

# 2. 测试签到
python manual_checkin.py

# 3. 查看日志
cat auto_checkin.log

# 4. 如果成功，启动自动签到
sudo systemctl start telegram-auto-checkin
```

## 💡 提示

1. **按钮文字区分大小写**：如果不确定，使用 `test_buttons.py` 查看准确的文字
2. **部分匹配即可**：`CHECKIN_BUTTON_TEXT` 只需包含按钮文字的一部分
3. **有些机器人需要多步操作**：可能需要先点击菜单，再点击签到
4. **定期检查**：机器人可能会更新界面，需要重新配置

## 🔄 如果按钮改变了

如果机器人更新了按钮，重新运行：

```bash
python test_buttons.py
# 查看新的按钮文字

nano .env
# 更新 CHECKIN_BUTTON_TEXT

sudo systemctl restart telegram-auto-checkin
# 重启服务
```
