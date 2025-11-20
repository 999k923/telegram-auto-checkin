# ⚡ 5分钟快速开始

## 🎯 全自动交互式部署（推荐）

### 1. 上传文件到服务器

```bash
cd ~
mkdir telegram-auto-checkin
cd telegram-auto-checkin
# 上传所有项目文件到此目录
```

### 2. 运行部署脚本

```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. 按照提示配置

部署脚本会自动引导你完成配置：

#### 📝 步骤 1：输入 API 凭证

```
请输入 API_ID (数字): 12345678
请输入 API_HASH (32位字符串): abc123...
请输入手机号 (如 +8613800138000): +8613800138000
```

**💡 如何获取 API 凭证？**
1. 访问 https://my.telegram.org
2. 登录后点击 "API development tools"
3. 创建应用获取 API_ID 和 API_HASH

#### 🎯 步骤 2：配置第 1 个签到目标

```
1️⃣  显示名称: @okemby_bot
2️⃣  目标标识: @okemby_bot
3️⃣  签到命令: /start
4️⃣  签到方式: 1 (按钮点击)
5️⃣  按钮文字: 签到
```

#### ➕ 步骤 3：添加更多目标（可选）

```
是否添加第 2 个签到目标? (y/n): y

1️⃣  显示名称: Cloud Cat Group
2️⃣  目标标识: Cloud Cat Group
3️⃣  签到命令: /checkin
4️⃣  签到方式: 2 (文本命令)
```

#### ✅ 步骤 4：继续添加或完成

```
是否添加第 3 个签到目标? (y/n): n

✅ 配置已保存！
```

**特点：**
- ✨ 支持添加**无限个**签到目标
- 🔘 每个目标可独立选择**按钮**或**命令**方式
- 🎨 交互式界面，简单易用

### 4. 首次登录验证

```bash
source venv/bin/activate
python test_login.py
```

按提示输入：
- 验证码（Telegram 发送）
- 两步验证密码（如果启用）

### 5. 测试签到

```bash
python manual_checkin.py
```

查看输出，确认所有目标都签到成功。

### 6. 设置自动运行

```bash
sudo ./setup_service.sh
```

**完成！** 脚本会在每天指定时间自动签到所有配置的目标。

---

## 🛠️ 常用工具

### 📋 查看所有群组和机器人

不确定群组名称？运行这个工具：

```bash
python list_groups.py
```

会显示：
- ✅ 所有你加入的群组（精确名称）
- ✅ 所有机器人（用户名）
- ✅ 群组 ID（可用于配置）
- ✅ 配置提示

### ➕ 添加新的签到目标

```bash
python add_target.py
```

支持连续添加多个目标，自动保存。

### 🔄 重新配置所有目标

```bash
python setup_targets.py
```

从头开始重新配置所有签到目标。

### 🔘 查看机器人按钮

```bash
python test_buttons.py
```

查看机器人的所有按钮，方便配置。

### 👥 测试群组签到

```bash
python test_group.py
```

测试群组的签到方式。

---

## 📋 配置示例

### 示例 1：单个机器人（按钮签到）

```
第 1 个目标:
  显示名称: @okemby_bot
  目标标识: @okemby_bot
  签到命令: /start
  签到方式: 1 (按钮)
  按钮文字: 签到

是否添加第 2 个目标? n
```

### 示例 2：机器人 + 群组

```
第 1 个目标:
  显示名称: OKemby机器人
  目标标识: @okemby_bot
  签到命令: /start
  签到方式: 1 (按钮)
  按钮文字: 签到

第 2 个目标:
  显示名称: Cloud Cat 群组
  目标标识: Cloud Cat Group
  签到命令: /checkin
  签到方式: 2 (命令)

是否添加第 3 个目标? n
```

### 示例 3：多个机器人

```
第 1 个: @bot1 (按钮签到)
第 2 个: @bot2 (命令签到)
第 3 个: @bot3 (按钮签到)
第 4 个: @bot4 (命令签到)
... 继续添加
```

---

## ⚙️ 修改配置

### 修改签到时间

```bash
nano .env

# 修改这两行
CHECKIN_HOUR=10    # 改为10点
CHECKIN_MINUTE=30  # 改为30分

# 重启服务
sudo systemctl restart telegram-auto-checkin
```

### 添加/删除签到目标

**方法1：使用交互式工具（推荐）**
```bash
python add_target.py
```

**方法2：手动编辑配置**
```bash
nano .env
```

### 查看运行日志

```bash
# 程序日志
tail -f auto_checkin.log

# 签到历史
cat checkin_history.log

# 系统日志
sudo journalctl -u telegram-auto-checkin -f
```

---

## 🐛 故障排查

### ❌ 找不到群组

**问题**: `Cannot find any entity corresponding to "xxx"`

**解决方法**:
```bash
# 1. 列出所有群组
python list_groups.py

# 2. 找到群组的精确名称或 ID
# 3. 使用精确名称或 ID 更新配置
python add_target.py  # 或手动编辑 .env
```

### ❌ 找不到按钮

**问题**: `未找到包含 'xxx' 的按钮`

**解决方法**:
```bash
# 查看机器人的所有按钮
python test_buttons.py

# 复制准确的按钮文字更新配置
```

### ❓ 测试群组签到方式

```bash
python test_group.py
```

输入群组名称和命令，查看是否有按钮。

### 🔍 查看详细错误

```bash
# 手动测试签到
python manual_checkin.py

# 查看详细日志
tail -f auto_checkin.log
```

---

## 📖 更多文档

- **README.md** - 完整文档和详细说明
- **MULTI_TARGET_GUIDE.md** - 多目标配置详解
- **SETUP_GUIDE.md** - 按钮签到详细指南
- **UPGRADE.md** - 版本升级指南

---

## 🎉 就是这么简单！

**核心优势：**
- 🚀 一键部署，全程交互式引导
- 🎯 支持无限个签到目标
- 🔘 按钮/命令方式自由选择
- 🛠️ 丰富的测试和管理工具

**运行 `./deploy.sh` 开始你的自动签到之旅！**
