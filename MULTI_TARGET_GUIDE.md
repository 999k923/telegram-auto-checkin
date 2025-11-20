# 多目标签到配置指南

本指南说明如何同时在多个机器人/群组签到。

## 🎯 使用场景

- 同时在机器人和群组签到
- 同时在多个机器人签到
- 同时在多个群组签到

## 📝 配置步骤

### 第一步：测试群组签到方式

```bash
source venv/bin/activate
python test_group.py
```

按提示操作：
1. 输入群组名称（如 `Cloud Cat Group`）
2. 输入签到命令（如 `/checkin`）
3. 查看是否有按钮
4. 测试签到是否成功

### 第二步：编辑 .env 文件

```bash
nano .env
```

### 配置示例

#### 示例 1：机器人（按钮） + 群组（命令）

```bash
CHECKIN_TARGETS=[{"name":"@okemby_bot","target":"@okemby_bot","command":"/start","button_text":"签到"},{"name":"Cloud Cat Group","target":"Cloud Cat Group","command":"/checkin","button_text":""}]
```

**说明：**
- 第一个目标：`@okemby_bot` 机器人，发送 `/start`，点击"签到"按钮
- 第二个目标：`Cloud Cat Group` 群组，发送 `/checkin` 命令（无按钮）

#### 示例 2：两个都是按钮签到

```bash
CHECKIN_TARGETS=[{"name":"@okemby_bot","target":"@okemby_bot","command":"/start","button_text":"签到"},{"name":"Cloud Cat Group","target":"Cloud Cat Group","command":"/start","button_text":"打卡"}]
```

#### 示例 3：两个都是命令签到

```bash
CHECKIN_TARGETS=[{"name":"Bot A","target":"@bot_a","command":"/checkin","button_text":""},{"name":"Bot B","target":"@bot_b","command":"/sign","button_text":""}]
```

#### 示例 4：三个或更多目标

```bash
CHECKIN_TARGETS=[{"name":"机器人1","target":"@bot1","command":"/start","button_text":"签到"},{"name":"群组1","target":"Group 1","command":"/checkin","button_text":""},{"name":"机器人2","target":"@bot2","command":"/daily","button_text":"每日签到"}]
```

## 📋 配置字段说明

每个签到目标包含以下字段：

```json
{
  "name": "显示名称",           // 日志中显示的名称（可选）
  "target": "目标标识",         // 机器人用户名（如 @bot）或群组名称
  "command": "/命令",           // 要发送的命令
  "button_text": "按钮文字"     // 按钮文字，留空表示使用命令方式
}
```

### 字段详解

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 显示名称，日志中使用 | `"@okemby_bot"` |
| `target` | 机器人用户名（需要@）或群组完整名称 | `"@okemby_bot"` 或 `"Cloud Cat Group"` |
| `command` | 签到命令 | `"/start"` 或 `"/checkin"` |
| `button_text` | 按钮文字，留空=使用命令方式 | `"签到"` 或 `""` |

## 🔧 JSON 格式化工具

在线格式化 JSON（避免格式错误）：
- https://jsonformatter.org/

## ✅ 配置验证

### 测试单个群组

```bash
python test_group.py
```

### 测试所有目标

```bash
python manual_checkin.py
```

应该看到类似输出：
```
============================================================
开始签到: @okemby_bot
============================================================
📤 向 @okemby_bot 发送 /start 并点击按钮: 签到
✅ [2024-01-01 09:00:00] @okemby_bot 签到成功!

============================================================
开始签到: Cloud Cat Group
============================================================
📤 向 Cloud Cat Group 发送签到命令: /checkin
✅ [2024-01-01 09:00:05] Cloud Cat Group 签到成功!
```

## 🎲 高级配置

### 不同目标使用不同延迟

如果想给不同目标设置不同延迟，可以修改代码或在签到之间自动延迟 3 秒（已内置）。

### 优先级顺序

目标按照在数组中的顺序依次执行：
```json
[
  第一个执行,
  第二个执行,
  第三个执行
]
```

## 🐛 常见问题

### Q: 群组名称如何填写？

A: 
- 填写群组的**完整名称**（不是用户名）
- 区分大小写
- 运行 `python test_group.py` 可以自动检测

### Q: 群组签到失败？

A: 检查：
1. 你是否在该群组中
2. 群组名称是否完全正确（包括空格、大小写）
3. 机器人是否在群组中且正常工作
4. 运行 `python test_group.py` 进行详细测试

### Q: JSON 格式错误？

A: 
- 确保使用**双引号** `"` 而不是单引号 `'`
- 确保所有括号、逗号都正确
- 使用在线 JSON 验证工具检查

### Q: 如何临时禁用某个目标？

A: 从 JSON 数组中删除该对象，或使用简单配置（方式二）。

## 📖 完整示例

### 实际使用的完整 .env 配置

```bash
# API 配置
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
PHONE_NUMBER=+8613800138000

# 多个签到目标
CHECKIN_TARGETS=[{"name":"OKemby机器人","target":"@okemby_bot","command":"/start","button_text":"签到"},{"name":"Cloud Cat 群组","target":"Cloud Cat Group","command":"/checkin","button_text":""}]

# 时间配置
CHECKIN_HOUR=9
CHECKIN_MINUTE=0
TIMEZONE=Asia/Shanghai
RANDOM_DELAY_MIN=0
RANDOM_DELAY_MAX=300
```

## 🔄 从单目标升级到多目标

如果你之前使用的是单目标配置：

**旧配置（单目标）：**
```bash
BOT_USERNAME=@okemby_bot
CHECKIN_COMMAND=/start
CHECKIN_BUTTON_TEXT=签到
```

**新配置（多目标）：**
```bash
# 注释掉旧配置
# BOT_USERNAME=@okemby_bot
# CHECKIN_COMMAND=/start
# CHECKIN_BUTTON_TEXT=签到

# 使用新配置
CHECKIN_TARGETS=[{"name":"@okemby_bot","target":"@okemby_bot","command":"/start","button_text":"签到"}]
```

添加第二个目标：
```bash
CHECKIN_TARGETS=[{"name":"@okemby_bot","target":"@okemby_bot","command":"/start","button_text":"签到"},{"name":"Cloud Cat Group","target":"Cloud Cat Group","command":"/checkin","button_text":""}]
```

## 📝 快速生成配置

运行测试后，根据提示生成配置：

```bash
# 测试第一个目标
python test_buttons.py
# 记录配置信息

# 测试第二个目标
python test_group.py
# 记录配置信息

# 合并到 CHECKIN_TARGETS
```
