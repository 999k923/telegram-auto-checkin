# 升级指南 - 添加 Cloud Cat Group 签到

## 🎯 目标

在现有的 `@okemby_bot` 签到基础上，添加 `Cloud Cat Group` 群组签到。

## 📋 操作步骤（5分钟）

### 步骤 1：停止服务（如果正在运行）

```bash
sudo systemctl stop telegram-auto-checkin
```

### 步骤 2：测试群组签到方式

```bash
cd ~/telegram-auto-checkin
source venv/bin/activate
python test_group.py
```

按提示操作：
- 输入群组名称：`Cloud Cat Group`
- 输入命令（根据群组机器人要求）：`/checkin` 或其他
- 查看是否有按钮需要点击

**记录测试结果：**
- 群组名称：`Cloud Cat Group`
- 签到命令：`________`
- 按钮文字：`________` （如果有）

### 步骤 3：备份当前配置

```bash
cp .env .env.backup
```

### 步骤 4：修改 .env 文件

```bash
nano .env
```

#### 选项 A：使用 JSON 多目标配置（推荐）

找到并**注释掉**旧的单目标配置：
```bash
# BOT_USERNAME=@okemby_bot
# CHECKIN_COMMAND=/start
# CHECKIN_BUTTON_TEXT=签到
```

添加多目标配置：
```bash
CHECKIN_TARGETS=[{"name":"@okemby_bot","target":"@okemby_bot","command":"/start","button_text":"签到"},{"name":"Cloud Cat Group","target":"Cloud Cat Group","command":"/checkin","button_text":""}]
```

**根据步骤2的测试结果调整：**
- 如果群组使用按钮，填入 `"button_text":"按钮文字"`
- 如果群组使用命令，保持 `"button_text":""`
- 如果命令不是 `/checkin`，修改 `"command":"/你的命令"`

#### 选项 B：保持原配置不变（需运行两次）

保持原配置，创建第二个配置文件（需要运行两个实例）。

### 步骤 5：测试新配置

```bash
python manual_checkin.py
```

应该看到两个签到都执行：
```
============================================================
开始签到: @okemby_bot
============================================================
✅ [@okemby_bot] 签到成功!

============================================================
开始签到: Cloud Cat Group
============================================================
✅ [Cloud Cat Group] 签到成功!
```

### 步骤 6：重启服务

```bash
sudo systemctl start telegram-auto-checkin
sudo systemctl status telegram-auto-checkin
```

### 步骤 7：验证

查看日志确认配置正确：
```bash
sudo journalctl -u telegram-auto-checkin -f
```

## ✅ 完整配置示例

### 示例 1：机器人（按钮）+ 群组（命令）

```bash
API_ID=12345678
API_HASH=your_hash
PHONE_NUMBER=+8613800138000

CHECKIN_TARGETS=[{"name":"@okemby_bot","target":"@okemby_bot","command":"/start","button_text":"签到"},{"name":"Cloud Cat Group","target":"Cloud Cat Group","command":"/checkin","button_text":""}]

CHECKIN_HOUR=9
CHECKIN_MINUTE=0
TIMEZONE=Asia/Shanghai
RANDOM_DELAY_MIN=0
RANDOM_DELAY_MAX=300
```

### 示例 2：两个都是按钮签到

```bash
CHECKIN_TARGETS=[{"name":"@okemby_bot","target":"@okemby_bot","command":"/start","button_text":"签到"},{"name":"Cloud Cat Group","target":"Cloud Cat Group","command":"/start","button_text":"打卡"}]
```

## 🔍 JSON 格式说明

每个目标用 `{}` 包裹，用 `,` 分隔：

```json
[
  {
    "name": "显示名称",
    "target": "@bot 或群组名称",
    "command": "/命令",
    "button_text": "按钮文字或留空"
  },
  {
    "name": "第二个目标",
    "target": "...",
    "command": "...",
    "button_text": "..."
  }
]
```

**注意：**
- 使用**双引号** `"`，不是单引号 `'`
- 整个内容在**一行**中
- 如果格式错误，访问 https://jsonformatter.org/ 验证

## 🐛 常见问题

### Q: 配置后只签到一个？

A: 检查 JSON 格式是否正确，运行：
```bash
python -c "import config; print(config.CHECKIN_TARGETS)"
```

### Q: 群组签到失败？

A: 
1. 确认群组名称准确（包括大小写、空格）
2. 确认你在该群组中
3. 运行 `python test_group.py` 详细测试

### Q: 想恢复原配置？

A: 
```bash
cp .env.backup .env
sudo systemctl restart telegram-auto-checkin
```

## 📝 检查清单

- [ ] 已停止服务
- [ ] 已测试群组签到方式（`test_group.py`）
- [ ] 已备份原配置（`.env.backup`）
- [ ] 已修改 `.env` 添加多目标配置
- [ ] 已测试新配置（`manual_checkin.py`）
- [ ] 两个目标都签到成功
- [ ] 已重启服务
- [ ] 已查看日志验证

## 📞 需要帮助？

查看详细文档：
```bash
cat MULTI_TARGET_GUIDE.md
```
